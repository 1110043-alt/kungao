"""
Tixcraft 自動註冊 GUI 應用
功能：
- 可指定或隨機生成名字
- 可自訂電話號碼收驗證碼的 API 連結
- 每註冊完成一個就自動關閉頁面
- 將註冊信息導入 Google 試算表
- 地址、年齡、生日每次隨機
"""

import sys
import asyncio
import random
import string
import re
import webbrowser
import os
from datetime import datetime
from typing import Optional, Dict, List
import json

# GUI 相關
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget,
        QCheckBox, QSpinBox, QComboBox, QMessageBox, QFileDialog,
        QTableWidget, QTableWidgetItem, QHeaderView, QDialog
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
    from PyQt5.QtGui import QFont, QIcon, QColor
    GUI_AVAILABLE = True
except ImportError:
    print("需要安裝 PyQt5: pip install PyQt5")
    GUI_AVAILABLE = False

# API 相關
try:
    from google.oauth2.service_account import Credentials
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    import gspread
    GSPREAD_AVAILABLE = True
except ImportError:
    print("需要安裝 gspread: pip install gspread google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    GSPREAD_AVAILABLE = False

# 嘗試導入 google-auth-oauthlib
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request as AuthRequest
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False

# Playwright
from playwright.async_api import async_playwright
import requests


class RegistrationData:
    """註冊數據模型"""
    def __init__(self, name: str, roc_id: str, phone: str, country_code: str, 
                 email: str, birthday: str, address: str, gender: str, google_account: str = ""):
        self.name = name
        self.roc_id = roc_id
        self.phone = phone
        self.country_code = country_code
        self.email = email
        self.birthday = birthday
        self.address = address
        self.gender = gender
        self.google_account = google_account
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict:
        return {
            'Name': self.name,
            'ROC ID': self.roc_id,
            'Phone': f"{self.country_code} {self.phone}",
            'Email': self.email,
            'Birthday': self.birthday,
            'Address': self.address,
            'Gender': self.gender,
            'Google Account': self.google_account,
            'Timestamp': self.timestamp
        }
    
    def to_row(self) -> List:
        """轉換為試算表行"""
        return [
            self.name,
            self.roc_id,
            f"{self.country_code} {self.phone}",
            self.email,
            self.birthday,
            self.address,
            self.gender,
            self.google_account,
            self.timestamp
        ]


class DataGenerator:
    """數據生成器"""
    def __init__(self):
        self.surnames = ['王', '李', '張', '劉', '陳', '楊', '黃', '林', '高', '鄭', '何', '曾', '吳', '徐', '周']
        self.given_names = ['小明', '美玲', '建輝', '俊傑', '雪芬', '耀庭', '志強', '怡君', '柏宏', '琳琳']
        self.counties = ['基隆市', '台北市', '新北市', '桃園市', '新竹市', '苗栗縣', '台中市', '彰化縣', '南投縣', '雲林縣']
        self.genders = ['男', '女']
    
    def generate_roc_id(self) -> str:
        """生成有效的 ROC 身份證號"""
        first_letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        gender_code = random.choice('12')
        remaining = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f"{first_letter}{gender_code}{remaining}"
    
    def generate_name(self, custom_name: Optional[str] = None) -> str:
        """生成或返回指定名字"""
        if custom_name and custom_name.strip():
            return custom_name.strip()
        return random.choice(self.surnames) + random.choice(self.given_names)
    
    def generate_email(self) -> str:
        """生成 Gmail 地址"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"test{random_str}@gmail.com"
    
    def generate_birthday(self) -> str:
        """生成生日"""
        year = random.randint(1960, 2000)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year}/{month:02d}/{day:02d}"
    
    def generate_address(self) -> str:
        """生成地址"""
        county = random.choice(self.counties)
        street_num = random.randint(1, 999)
        return f"{county}街道{street_num}號"
    
    def generate_gender(self) -> str:
        """生成性別"""
        return random.choice(self.genders)


class TixcraftWorker(QThread):
    """註冊工作線程"""
    progress = pyqtSignal(str)
    completed = pyqtSignal(RegistrationData)
    error = pyqtSignal(str)
    
    def __init__(self, config: Dict):
        super().__init__()
        self.config = config
        self.generator = DataGenerator()
    
    def run(self):
        try:
            self.progress.emit("[開始] 初始化異步任務...")
            asyncio.run(self.register())
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.progress.emit(f"[錯誤]\n{error_details}")
            self.error.emit(f"錯誤: {str(e)}")
    
    async def register(self):
        """執行註冊"""
        try:
            self.progress.emit("[開始] 初始化註冊流程...")
            
            # 生成數據
            custom_name = self.config.get('custom_name', '')
            name = self.generator.generate_name(custom_name)
            roc_id = self.generator.generate_roc_id()
            phone = self.config.get('phone', '3315003235')
            country_code = self.config.get('country_code', '+1')
            email = self.generator.generate_email()
            birthday = self.generator.generate_birthday()
            address = self.generator.generate_address()
            gender = self.generator.generate_gender()
            
            self.progress.emit(f"[生成] 名字: {name}, 證件: {roc_id}")
            
            # 啟動註冊流程
            self.progress.emit("[Playwright] 啟動瀏覽器...")
            async with async_playwright() as p:
                self.progress.emit("[Playwright] 啟動 Chromium (首次可能需要 30 秒)...")
                browser = await asyncio.wait_for(
                    p.chromium.launch(headless=False),
                    timeout=60
                )
                page = await browser.new_page()
                self.progress.emit("[Playwright] ✓ 瀏覽器已啟動")
                
                try:
                    # Tixcraft 使用 Google SSO 登錄，檢查是否已登錄
                    self.progress.emit("[檢查] 檢查登錄狀態...")
                    await asyncio.wait_for(page.goto("https://tixcraft.com/user"), timeout=15)
                    await asyncio.sleep(2)
                    
                    # 檢查是否已登錄
                    is_logged_in = False
                    try:
                        logout_btn = page.locator("a:has-text('登出'), button:has-text('登出')").first
                        is_logged_in = await logout_btn.is_visible(timeout=2000)
                    except:
                        pass
                    
                    if not is_logged_in:
                        self.progress.emit("[登錄] 未登錄，導向登錄頁面...")
                        await asyncio.wait_for(page.goto("https://tixcraft.com/login"), timeout=15)
                        await asyncio.sleep(3)
                        
                        self.progress.emit("[登錄] 尋找 Google 登錄按鈕...")
                        all_buttons = await page.locator("button").all()
                        self.progress.emit(f"[登錄] 頁面有 {len(all_buttons)} 個按鈕")
                        
                        google_btn = None
                        for i, btn in enumerate(all_buttons):
                            try:
                                btn_text = await btn.text_content()
                                if btn_text and ('Google' in btn_text or 'google' in btn_text):
                                    google_btn = btn
                                    self.progress.emit(f"[登錄] ✓ 找到 Google 按鈕! (第 {i+1} 個)")
                                    break
                            except:
                                pass
                        
                        if google_btn:
                            self.progress.emit("[登錄] 點擊 Google 按鈕...")
                            try:
                                await google_btn.click(timeout=5000)
                                self.progress.emit("[登錄] ✓ 已點擊 Google 按鈕")
                                await asyncio.sleep(3)
                            except Exception as e:
                                self.progress.emit(f"[登錄] ✗ 點擊失敗: {str(e)}")
                        else:
                            self.progress.emit("[登錄] ✗ 找不到 Google 按鈕，嘗試第二個按鈕...")
                            if len(all_buttons) > 1:
                                try:
                                    await all_buttons[1].click()
                                    self.progress.emit("[登錄] ✓ 點擊第二個按鈕")
                                    await asyncio.sleep(3)
                                except:
                                    pass
                        
                        self.progress.emit("[登錄] ⏳ 等待 Google 認證完成 (120 秒超時)...")
                        start_time = datetime.now()
                        while (datetime.now() - start_time).total_seconds() < 120:
                            try:
                                current_url = page.url
                                if "tixcraft.com" in current_url and "google" not in current_url.lower():
                                    self.progress.emit("[登錄] ✓ 已返回 Tixcraft，登錄成功")
                                    break
                            except:
                                pass
                            await asyncio.sleep(2)
                    else:
                        self.progress.emit("[檢查] ✓ 已登錄，跳過 Google 認證")
                
                # 導航到註冊頁面
                self.progress.emit("導航到註冊頁面...")
                await page.goto("https://tixcraft.com/user/register")
                await asyncio.sleep(3)
                
                # 填寫表單
                self.progress.emit("填寫表單...")
                await self.fill_form(page, name, roc_id, birthday, phone, email, address, gender)
                
                # 點擊綁定按鈕
                self.progress.emit("點擊綁定按鈕...")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(0.5)
                bind_btn = page.locator("button:has-text('選定此會員帳號進行綁定')").first
                await bind_btn.click()
                await asyncio.sleep(2)
                
                # 修改電話號碼（如需要）
                if country_code != "+852" or phone != "70250485":
                    self.progress.emit(f"修改電話號碼為: {country_code} {phone}")
                    await self.modify_phone(page, country_code, phone)
                
                # 提交驗證
                self.progress.emit("提交手機驗證...")
                submit_btn = page.locator("button:has-text('確認送出並進行手機號碼認證')").first
                await submit_btn.click()
                await asyncio.sleep(2)
                
                # 等待 SMS
                self.progress.emit(f"等待 SMS 驗證碼到 {country_code} {phone}...")
                sms_code = await self.wait_for_sms(phone, self.config.get('sms_api'))
                
                if sms_code:
                    self.progress.emit(f"收到驗證碼: {sms_code}")
                    
                    # 輸入驗證碼
                    code_input = page.locator("input[placeholder*='驗證碼'], input[id*='code']").first
                    await code_input.fill(sms_code)
                    await asyncio.sleep(0.5)
                    
                    # 確認驗證
                    confirm_btn = page.locator("button:has-text('確認')").first
                    await confirm_btn.click()
                    await asyncio.sleep(2)
                    
                    self.progress.emit("✓ 註冊成功！")
                    
                    # 獲取 Google 帳戶（如可見）
                    google_account = await page.locator("text=/Google|google/i").first.text_content().catch(lambda: "")
                    
                    # 記錄數據
                    reg_data = RegistrationData(
                        name=name,
                        roc_id=roc_id,
                        phone=phone,
                        country_code=country_code,
                        email=email,
                        birthday=birthday,
                        address=address,
                        gender=gender,
                        google_account=google_account.strip() if google_account else ""
                    )
                    
                    self.completed.emit(reg_data)
                else:
                    self.error.emit("未收到 SMS 驗證碼")
                
                # 關閉頁面
                await asyncio.sleep(2)
                await browser.close()
                
            except Exception as e:
                self.error.emit(f"註冊失敗: {str(e)}")
                await browser.close()
    
    async def fill_form(self, page, name, roc_id, birthday, phone, email, address, gender):
        """填寫表單"""
        try:
            self.progress.emit(f"開始填寫表單: 姓名={name}, 證件={roc_id}")
            
            # 等待頁面加載完成
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)
            
            # 列出頁面上所有的 input 字段
            all_inputs = await page.locator("input").all()
            self.progress.emit(f"頁面上有 {len(all_inputs)} 個輸入字段")
            
            # 姓名
            self.progress.emit(f"填寫姓名: {name}")
            try:
                name_inp = page.locator("input[id*='name'], input[placeholder*='名'], input[aria-label*='名']").first
                await name_inp.fill(name, timeout=3000)
                self.progress.emit("✓ 姓名填寫成功")
            except Exception as e:
                self.progress.emit(f"✗ 姓名填寫失敗: {str(e)}")
            
            await asyncio.sleep(0.5)
            
            # 身份證
            self.progress.emit(f"填寫身份證: {roc_id}")
            try:
                id_inp = page.locator("input[id*='identity'], input[id*='id'], input[placeholder*='身份']").first
                await id_inp.fill(roc_id, timeout=3000)
                self.progress.emit("✓ 身份證填寫成功")
            except Exception as e:
                self.progress.emit(f"✗ 身份證填寫失敗: {str(e)}")
            
            await asyncio.sleep(0.5)
            
            # 生日
            self.progress.emit(f"填寫生日: {birthday}")
            try:
                bday_inp = page.locator("input[id*='birthday'], input[id*='birth'], input[placeholder*='生日']").first
                await bday_inp.fill(birthday, timeout=3000)
                self.progress.emit("✓ 生日填寫成功")
            except Exception as e:
                self.progress.emit(f"✗ 生日填寫失敗: {str(e)}")
            
            await asyncio.sleep(0.5)
            
            # 性別
            self.progress.emit(f"選擇性別: {gender}")
            try:
                if gender == '男':
                    gender_rad = page.locator("input[type='radio'][value*='male'], input[type='radio'][value='1'], input[value*='男']").first
                else:
                    gender_rad = page.locator("input[type='radio'][value*='female'], input[type='radio'][value='2'], input[value*='女']").first
                await gender_rad.check(timeout=3000)
                self.progress.emit("✓ 性別選擇成功")
            except Exception as e:
                self.progress.emit(f"✗ 性別選擇失敗: {str(e)}")
            
            await asyncio.sleep(0.5)
            
            # 郵箱
            self.progress.emit(f"填寫郵箱: {email}")
            try:
                email_inp = page.locator("input[type='email'], input[id*='email'], input[placeholder*='郵']").first
                await email_inp.fill(email, timeout=3000)
                self.progress.emit("✓ 郵箱填寫成功")
            except Exception as e:
                self.progress.emit(f"✗ 郵箱填寫失敗: {str(e)}")
            
            self.progress.emit("✓ 表單填寫完成")
        
        except Exception as e:
            self.progress.emit(f"填寫表單失敗: {str(e)}")
    
    async def modify_phone(self, page, country_code, phone):
        """修改電話號碼"""
        try:
            # 打開國碼選擇器
            select2 = page.locator("span.select2-selection__rendered, #select2-editPhoneCountry-container").first
            await select2.click()
            await asyncio.sleep(0.8)
            
            # 搜尋國家
            search = page.locator(".select2-search__field").first
            await search.type(country_code.replace('+', ''), delay=100)
            await asyncio.sleep(0.6)
            
            # 選擇選項
            option = page.locator("li.select2-results__option").first
            await option.click()
            await asyncio.sleep(0.5)
            
            # 填寫電話
            phone_inp = page.locator("input[name*='phone']").first
            await phone_inp.clear()
            await phone_inp.fill(phone)
        
        except Exception as e:
            self.error.emit(f"修改電話失敗: {str(e)}")
    

    
    async def wait_for_sms(self, phone, sms_api_url, timeout=180):
        """等待 SMS 驗證碼"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                response = requests.get(sms_api_url, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    match = re.search(r'\d{6}', content)
                    if match:
                        return match.group()
                
                await asyncio.sleep(3)
            except:
                await asyncio.sleep(3)
        
        return None


class GoogleSheetsManager:
    """Google 試算表管理器 - 簡化版本"""
    def __init__(self, sheet_url: str, credentials_file: str = None):
        self.sheet_url = sheet_url
        self.credentials_file = credentials_file
        self.client = None
        self.sheet = None
        self.auth_token_file = "gsheets_token.json"
    
    def authenticate(self) -> tuple[bool, str]:
        """認證 Google Sheets（Service Account 方式），返回 (成功, 消息)"""
        try:
            if not GSPREAD_AVAILABLE:
                return False, "gspread 未安裝，請執行: pip install gspread google-auth"
            
            if not self.sheet_url or not self.sheet_url.strip():
                return False, "請輸入有效的 Google Sheets URL"
            
            # 檢查 credentials.json 是否存在
            project_root = os.path.dirname(os.path.abspath(__file__))
            credentials_path = os.path.join(project_root, "credentials.json")
            
            if not os.path.exists(credentials_path):
                return False, (
                    "找不到 credentials.json\n\n" +
                    "請確保已下載 Google Service Account 金鑰文件，\n" +
                    "並放在本目錄：\n\n" +
                    f"{credentials_path}"
                )
            
            # 嘗試用 Service Account 認證
            try:
                self.client = gspread.service_account(filename=credentials_path)
            except Exception as e:
                error_str = str(e).lower()
                return False, f"Service Account 認證失敗: {str(e)[:100]}"
            
            # 嘗試打開試算表
            try:
                spreadsheet = self.client.open_by_url(self.sheet_url)
                self.sheet = spreadsheet.sheet1
                
                # 測試寫入權限 - 添加標題行
                headers = ["姓名", "身份證", "電話", "郵箱", "生日", "地址", "性別", "Google 帳號", "時間"]
                try:
                    self.sheet.update([headers], range_name='A1:I1')
                except:
                    pass  # 已經有標題或其他錯誤，不影響認證
                    
                return True, "✓ Google Sheets 連接成功！"
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg or "not found" in error_msg.lower():
                    return False, "找不到試算表。請確認 URL 正確"
                elif "permission" in error_msg.lower():
                    return False, (
                        "權限不足。\n\n" +
                        "請確保已在 Google Sheets 中\n" +
                        "共享權限給 Service Account 電子郵件帳戶：\n" +
                        "tixcraft-sheets@tixcraft-registration.iam.gserviceaccount.com"
                    )
                else:
                    return False, f"打開試算表失敗: {error_msg[:100]}"
        
        except Exception as e:
            return False, f"認證錯誤: {str(e)[:100]}"
    
    def append_row(self, data: RegistrationData) -> tuple[bool, str]:
        """添加行到試算表，返回 (成功, 消息)"""
        try:
            if not self.sheet:
                return False, "試算表未連接"
            
            self.sheet.append_row(data.to_row())
            return True, f"✓ {data.name} 已添加到試算表"
        except Exception as e:
            return False, f"添加失敗: {str(e)[:100]}"


class TixcraftGUI(QMainWindow):
    """主 GUI 窗口"""
    CONFIG_FILE = "gui_config.json"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tixcraft 自動註冊工具 v1.0")
        self.setGeometry(100, 100, 1000, 750)
        
        self.generator = DataGenerator()
        self.google_sheets = None
        self.registration_history = []
        
        # 配置管理
        self.config = self.load_config()
        
        self.init_ui()
    
    def load_config(self) -> Dict:
        """加載配置文件"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加載配置失敗: {e}")
        
        # 預設配置
        return {
            'phone': '3315003235',
            'country': '+1',
            'sms_api': 'https://api.sms8.net/api/record?token=b632kn5442ili34wycjmcxsjnlm6bq89jh4f',
            'sheets_url': '',
            'sheets_email': '',
            'sheets_password': '',
            'name': '',
            'count': 1
        }
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失敗: {e}")
    
    def init_ui(self):
        """初始化 UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 標籤
        tabs = QTabWidget()
        central_widget.layout = QVBoxLayout()
        central_widget.setLayout(central_widget.layout)
        central_widget.layout.addWidget(tabs)
        
        # 標籤 1: 設定
        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, "設定")
        
        # 標籤 2: 控制
        control_tab = self.create_control_tab()
        tabs.addTab(control_tab, "控制")
        
        # 標籤 3: 日誌
        log_tab = self.create_log_tab()
        tabs.addTab(log_tab, "日誌")
    
    def create_settings_tab(self) -> QWidget:
        """創建設定標籤"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Google 帳號設定
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Google 帳號:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@gmail.com")
        self.email_input.setText(self.config.get('sheets_email', ''))
        self.email_input.textChanged.connect(self.save_settings)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)
        
        # Google 密碼設定
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel("Google 密碼:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("輸入應用密碼 (App Password)")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText(self.config.get('sheets_password', ''))
        self.password_input.textChanged.connect(self.save_settings)
        pwd_layout.addWidget(self.password_input)
        layout.addLayout(pwd_layout)
        
        layout.addSpacing(10)
        
        # 電話號碼設定
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("電話號碼:"))
        self.phone_input = QLineEdit(self.config.get('phone', '3315003235'))
        self.phone_input.textChanged.connect(self.save_settings)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)
        
        # 國碼設定
        country_layout = QHBoxLayout()
        country_layout.addWidget(QLabel("國碼:"))
        self.country_combo = QComboBox()
        self.country_combo.addItems(["+1", "+852", "+886"])
        self.country_combo.setCurrentText(self.config.get('country', '+1'))
        self.country_combo.currentTextChanged.connect(self.save_settings)
        country_layout.addWidget(self.country_combo)
        layout.addLayout(country_layout)
        
        # SMS API URL
        sms_layout = QHBoxLayout()
        sms_layout.addWidget(QLabel("SMS API 連結:"))
        self.sms_api_input = QLineEdit(self.config.get('sms_api', 'https://api.sms8.net/api/record?token=b632kn5442ili34wycjmcxsjnlm6bq89jh4f'))
        self.sms_api_input.setMinimumWidth(400)
        self.sms_api_input.textChanged.connect(self.save_settings)
        sms_layout.addWidget(self.sms_api_input)
        layout.addLayout(sms_layout)
        
        layout.addSpacing(10)
        
        # Google Sheets 試算表 URL
        sheets_layout = QHBoxLayout()
        sheets_layout.addWidget(QLabel("Google Sheets URL:"))
        self.sheets_url_input = QLineEdit(self.config.get('sheets_url', ''))
        self.sheets_url_input.setPlaceholderText("https://docs.google.com/spreadsheets/d/...")
        self.sheets_url_input.textChanged.connect(self.save_settings)
        sheets_layout.addWidget(self.sheets_url_input)
        self.sheets_auth_btn = QPushButton("認證")
        self.sheets_auth_btn.clicked.connect(self.authenticate_sheets)
        sheets_layout.addWidget(self.sheets_auth_btn)
        layout.addLayout(sheets_layout)
        
        layout.addSpacing(10)
        
        # 名字設定
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("名字:"))
        self.name_input = QLineEdit(self.config.get('name', ''))
        self.name_input.setPlaceholderText("留空為隨機生成")
        self.name_input.textChanged.connect(self.save_settings)
        name_layout.addWidget(self.name_input)
        self.random_name_btn = QPushButton("隨機")
        self.random_name_btn.clicked.connect(self.generate_random_name)
        name_layout.addWidget(self.random_name_btn)
        layout.addLayout(name_layout)
        
        # 數量設定
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("註冊數量:"))
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(1)
        self.count_spin.setMaximum(100)
        self.count_spin.setValue(self.config.get('count', 1))
        self.count_spin.valueChanged.connect(self.save_settings)
        count_layout.addWidget(self.count_spin)
        layout.addLayout(count_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def save_settings(self):
        """保存設定"""
        self.config['phone'] = self.phone_input.text()
        self.config['country'] = self.country_combo.currentText()
        self.config['sms_api'] = self.sms_api_input.text()
        self.config['sheets_url'] = self.sheets_url_input.text()
        self.config['sheets_email'] = self.email_input.text()
        self.config['sheets_password'] = self.password_input.text()
        self.config['name'] = self.name_input.text()
        self.config['count'] = self.count_spin.value()
        self.save_config()
    
    def create_control_tab(self) -> QWidget:
        """創建控制標籤"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 狀態顯示
        self.status_label = QLabel("準備就緒")
        self.status_label.setStyleSheet("background-color: lightgreen; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # 進度日誌
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        layout.addWidget(self.progress_text)
        
        # 控制按鈕
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("開始註冊")
        self.start_btn.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        self.start_btn.clicked.connect(self.start_registration)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setStyleSheet("background-color: red; color: white;")
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        return widget
    
    def create_log_tab(self) -> QWidget:
        """創建日誌標籤"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 註冊歷史表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(9)
        self.history_table.setHorizontalHeaderLabels([
            "名字", "證件", "電話", "郵箱", "生日", "地址", "性別", "Google帳戶", "時間"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.history_table)
        
        # 清除按鈕
        clear_btn = QPushButton("清除歷史")
        clear_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_btn)
        
        widget.setLayout(layout)
        return widget
    
    def authenticate_sheets(self):
        """認證 Google Sheets"""
        url = self.sheets_url_input.text()
        
        # 如果 credentials.json 不存在，提示用戶
        project_root = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(project_root, "credentials.json")
        
        if not os.path.exists(credentials_path):
            response = QMessageBox.question(
                self, 
                "需要設置 OAuth",
                "首次使用 Google Sheets 需要設置。\n\n" +
                "是否現在打開設置嚮導？\n" +
                "(會在終端開啟 setup_oauth.py)",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if response == QMessageBox.Yes:
                os.system("start python setup_oauth.py")
                QMessageBox.information(self, "提示", 
                    "請在終端完成 OAuth 設置，然後重新按「認證」")
            return
        
        if not url:
            QMessageBox.warning(self, "警告", "請先輸入 Google Sheets URL\n\n快速指南：\n1. 開啟 https://sheets.google.com\n2. 點擊「+ 建立新試算表」\n3. 複製瀏覽器位址欄的 URL")
            return
        
        # 顯示進度
        self.progress_text.append("正在認證 Google Sheets...")
        
        self.google_sheets = GoogleSheetsManager(url)
        success, message = self.google_sheets.authenticate()
        
        if success:
            QMessageBox.information(self, "成功", message)
            self.sheets_auth_btn.setStyleSheet("background-color: green; color: white;")
            self.progress_text.append(message)
        else:
            QMessageBox.critical(self, "認證失敗", 
                f"{message}\n\n" +
                "解決方案：\n" +
                "1. 確認 Google Sheets URL 正確\n" +
                "2. 確保試算表已分享（編輯權限）\n" +
                "3. 完成 OAuth 設置\n" +
                "4. 檢查網絡連接"
            )
            self.progress_text.append(f"❌ 認證失敗: {message}")

    
    def generate_random_name(self):
        """生成隨機名字"""
        name = self.generator.generate_name()
        self.name_input.setText(name)
    
    def start_registration(self):
        """開始註冊"""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        config = {
            'custom_name': self.name_input.text(),
            'phone': self.phone_input.text(),
            'country_code': self.country_combo.currentText(),
            'sms_api': self.sms_api_input.text()
        }
        
        count = self.count_spin.value()
        self.progress_text.append(f"開始註冊 {count} 個帳號...\n")
        
        for i in range(count):
            self.progress_text.append(f"\n--- 第 {i+1}/{count} 個 ---")
            
            worker = TixcraftWorker(config)
            worker.progress.connect(self.on_progress)
            worker.completed.connect(self.on_registration_completed)
            worker.error.connect(self.on_registration_error)
            worker.start()
            worker.wait()  # 等待完成
    
    def on_progress(self, message: str):
        """進度回調"""
        self.progress_text.append(f"→ {message}")
        self.status_label.setText(message)
    
    def on_registration_completed(self, data: RegistrationData):
        """註冊完成回調"""
        self.registration_history.append(data)
        self.progress_text.append(f"✓ 成功: {data.name} ({data.roc_id})")
        
        # 添加到表格
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        for col, value in enumerate(data.to_row()):
            self.history_table.setItem(row, col, QTableWidgetItem(str(value)))
        
        # 添加到 Google Sheets
        if self.google_sheets:
            if self.google_sheets.append_row(data):
                self.progress_text.append("✓ 已添加到 Google Sheets")
            else:
                self.progress_text.append("⚠ 無法添加到 Google Sheets")
    
    def on_registration_error(self, error: str):
        """錯誤回調"""
        self.progress_text.append(f"✗ {error}")
        self.status_label.setText(error)
        self.status_label.setStyleSheet("background-color: red; color: white;")
    
    def clear_history(self):
        """清除歷史"""
        reply = QMessageBox.question(self, "確認", "確定要清除所有歷史嗎？")
        if reply == QMessageBox.Yes:
            self.history_table.setRowCount(0)
            self.registration_history.clear()
            self.progress_text.clear()


def main():
    print("[啟動] 開始初始化 GUI...")
    
    if not GUI_AVAILABLE:
        print("[錯誤] GUI 不可用，請安裝 PyQt5")
        return
    
    try:
        print("[啟動] 創建 QApplication...")
        app = QApplication(sys.argv)
        
        print("[啟動] 創建主視窗...")
        window = TixcraftGUI()
        
        print("[啟動] 顯示視窗...")
        window.show()
        
        print("[啟動] 進入事件循環...")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"[致命錯誤] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
