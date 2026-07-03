"""
Tixcraft 自動註冊 GUI 應用 (簡化版)
功能: Tixcraft Google SSO 自動登錄和表單填寫
"""

import sys
import asyncio
import random
import string
import re
import os
from datetime import datetime
from typing import Dict

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget,
        QSpinBox, QMessageBox
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    GUI_AVAILABLE = True
except ImportError:
    print("需要安裝 PyQt5: pip install PyQt5")
    GUI_AVAILABLE = False

try:
    import gspread
    GSPREAD_AVAILABLE = True
except ImportError:
    print("需要安裝 gspread: pip install gspread google-auth")
    GSPREAD_AVAILABLE = False

from playwright.async_api import async_playwright
import json


class DataGenerator:
    """數據生成器"""
    
    # 台灣常見地址列表
    TAIWAN_ADDRESSES = [
        "台北市中山區南京東路一段123號",
        "台北市信義區信義路四段100號",
        "台北市大安區敦化南路二段50號",
        "台北市松山區南京東路三段280號",
        "台新北市板橋區中山路一段100號",
        "新北市新店區北新路一段123號",
        "新北市永和區永和路二段50號",
        "新北市中和區中正路100號",
        "台中市西屯區台灣大道三段100號",
        "台中市南屯區文心路二段50號",
        "台中市北屯區軍功路一段123號",
        "台中市東區旱溪東路一段100號",
        "高雄市左營區博愛二路100號",
        "高雄市三民區中山路一段200號",
        "高雄市鳳山區五甲二路50號",
        "高雄市鼓山區中山路50號",
        "台南市中西區民權路二段100號",
        "台南市東區大同路一段50號",
        "台南市南區建平路50號",
        "台南市北區公園路二段100號",
    ]
    
    def generate_name(self, custom=""):
        return custom if custom else f"User{random.randint(1000, 9999)}"
    
    def generate_roc_id(self):
        """
        生成有效的台灣身分證號碼（含檢查碼）
        
        編碼結構：區域碼(1) + 性別碼(1) + 流水號(7) + 檢查碼(1) = 10碼
        
        區域碼對照：A(台北市), B(台中市), C(基隆市), D(台南市), E(高雄市), F(新北市)
                  G(宜蘭縣), H(桃園市), I(嘉義市), J(新竹縣), K(苗栗縣), L(彰化縣)
                  M(南投縣), N(花蓮縣), O(台東縣), P(澎湖縣), Q(金門縣), R(連江縣)
                  S(新竹市), T(嘉義縣), U(屏東縣), V(雲林縣)
        
        權數：1, 9, 8, 7, 6, 5, 4, 3, 2, 1
        檢查碼計算：(10 - (加權和 % 10)) % 10
        """
        # 常用的縣市碼
        city_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V']
        city_code = random.choice(city_codes)
        
        # 第2碼：性別碼 (男=1, 女=2)
        gender_code = random.choice([1, 2])
        
        # 第3-9碼：流水號 (7位)
        serial = [random.randint(0, 9) for _ in range(7)]
        
        # 將字母轉換為數字：A=10, B=11, ..., Z=33
        letter_code = ord(city_code) - ord('A') + 10
        
        # 組合所有數字：字母十位、字母個位、性別碼、流水號(7位)
        all_digits = [
            letter_code // 10,      # 字母十位
            letter_code % 10,       # 字母個位
            gender_code,             # 性別碼
            *serial                  # 流水號（7位）
        ]
        
        # 權數：1, 9, 8, 7, 6, 5, 4, 3, 2
        weights = [1, 9, 8, 7, 6, 5, 4, 3, 2]
        
        # 計算加權和
        sum_val = sum(digit * weight for digit, weight in zip(all_digits, weights))
        
        # 計算檢查碼：(10 - (sum_val % 10)) % 10
        check_code = (10 - (sum_val % 10)) % 10
        
        return f"{city_code}{gender_code}{''.join(map(str, serial))}{check_code}"
    
    def generate_email(self):
        return f"user{random.randint(10000, 99999)}@gmail.com"
    
    def generate_birthday(self):
        year = random.randint(1980, 2000)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year:04d}/{month:02d}/{day:02d}"
    
    def generate_gender(self):
        return random.choice(["男", "女"])
    
    def generate_address(self):
        """
        生成符合台灣地址格式的地址：3位郵遞區號+市(縣)+區+路+號
        
        範例：100 台北市中正區中山路1號
        """
        # 台灣主要城市的地址數據：(郵遞區號, 市/縣, 區, 路名, 號碼)
        addresses = [
            # 台北市 (100-109)
            ("100", "台北市", "中正區", "中山路", "1號"),
            ("101", "台北市", "中正區", "忠孝東路", "5號"),
            ("102", "台北市", "大同區", "南京東路", "10號"),
            ("103", "台北市", "中山區", "中山路", "50號"),
            ("104", "台北市", "松山區", "南京東路", "100號"),
            ("105", "台北市", "大安區", "敦化南路", "50號"),
            ("106", "台北市", "大安區", "仁愛路", "100號"),
            ("107", "台北市", "信義區", "信義路", "200號"),
            ("108", "台北市", "南港區", "南港路", "150號"),
            ("109", "台北市", "文山區", "木新路", "75號"),
            
            # 新北市 (220-226)
            ("220", "新北市", "板橋區", "中山路", "100號"),
            ("221", "新北市", "板橋區", "重慶路", "200號"),
            ("222", "新北市", "深坑區", "北深路", "50號"),
            ("223", "新北市", "汐止區", "新台五路", "300號"),
            ("224", "新北市", "新店區", "北新路", "123號"),
            ("225", "新北市", "永和區", "永和路", "50號"),
            ("226", "新北市", "中和區", "中正路", "100號"),
            
            # 桃園市 (320-328)
            ("320", "桃園市", "中壢區", "中山路", "100號"),
            ("321", "桃園市", "平鎮區", "中豐路", "200號"),
            ("322", "桃園市", "龍潭區", "龍潭路", "150號"),
            ("323", "桃園市", "楊梅區", "楊梅路", "75號"),
            ("324", "桃園市", "新屋區", "新屋路", "50號"),
            ("325", "桃園市", "觀音區", "觀音路", "100號"),
            ("326", "桃園市", "蘆竹區", "蘆竹路", "123號"),
            
            # 台中市 (400-409)
            ("400", "台中市", "中區", "中山路", "50號"),
            ("401", "台中市", "東區", "旱溪東路", "100號"),
            ("402", "台中市", "南區", "南屯路", "200號"),
            ("403", "台中市", "西區", "館前路", "150號"),
            ("404", "台中市", "港區", "台灣大道", "123號"),
            ("405", "台中市", "南屯區", "文心路", "50號"),
            ("406", "台中市", "北屯區", "軍功路", "100號"),
            ("407", "台中市", "西屯區", "台灣大道", "200號"),
            ("408", "台中市", "烏日區", "烏日路", "75號"),
            ("409", "台中市", "霧峰區", "新成路", "50號"),
            
            # 台南市 (700-709)
            ("700", "台南市", "中西區", "民權路", "100號"),
            ("701", "台南市", "東區", "大同路", "50號"),
            ("702", "台南市", "南區", "建平路", "50號"),
            ("704", "台南市", "北區", "公園路", "100號"),
            ("705", "台南市", "安平區", "安平路", "200號"),
            ("706", "台南市", "安南區", "安南路", "150號"),
            ("707", "台南市", "永康區", "永康路", "75號"),
            ("708", "台南市", "歸仁區", "歸仁路", "50號"),
            
            # 高雄市 (800-813)
            ("800", "高雄市", "前金區", "中山路", "100號"),
            ("801", "高雄市", "新興區", "五福路", "200號"),
            ("802", "高雄市", "苓雅區", "中正路", "50號"),
            ("803", "高雄市", "鹽埕區", "五福四路", "150號"),
            ("804", "高雄市", "鼓山區", "中山路", "50號"),
            ("805", "高雄市", "左營區", "博愛二路", "100號"),
            ("806", "高雄市", "三民區", "中山路", "200號"),
            ("807", "高雄市", "楠梓區", "南鼎路", "123號"),
            ("808", "高雄市", "小港區", "小港路", "75號"),
            ("809", "高雄市", "旗津區", "旗津路", "50號"),
            ("810", "高雄市", "前鎮區", "中山四路", "100號"),
            ("811", "高雄市", "茂港區", "茂港路", "200號"),
            ("812", "高雄市", "旗山區", "旗山路", "150號"),
        ]
        
        # 隨機選擇一個地址組合
        postal_code, city, district, road, number = random.choice(addresses)
        
        # 按格式組合：郵遞區號 + 市 + 區 + 路 + 號
        return f"{postal_code} {city}{district}{road}{number}"


class RegistrationWorker(QThread):
    """註冊工作線程"""
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    success = pyqtSignal(str)
    waiting_for_manual = pyqtSignal()  # 新增：通知GUI等待用戶操作
    
    def __init__(self, config: Dict):
        super().__init__()
        self.config = config
        self.generator = DataGenerator()
        self.running = True
    
    def run(self):
        """運行線程"""
        print("[線程] 開始運行...")
        try:
            asyncio.run(self.register())
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(f"[錯誤] {error_msg}")
            self.error.emit(str(e))
    
    async def register(self):
        """執行註冊"""
        try:
            # 準備數據
            name = self.generator.generate_name(self.config.get('name', ''))
            roc_id = self.generator.generate_roc_id()
            email = self.generator.generate_email()
            birthday = self.generator.generate_birthday()
            gender = self.generator.generate_gender()
            phone = self.config.get('phone', '3315003235')
            country_code = self.config.get('country_code', '+1')
            google_email = self.config.get('google_email', '')
            google_password = self.config.get('google_password', '')
            
            self.progress.emit(f"[數據] 生成: {name}, {roc_id}")
            
            # 啟動 Playwright
            self.progress.emit("[Playwright] 啟動瀏覽器...")
            async with async_playwright() as p:
                # 反檢測參數 - 讓 Chromium 看起來像真實的 Chrome 瀏覽器
                browser = await asyncio.wait_for(
                    p.chromium.launch(
                        headless=False,
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-dev-shm-usage',
                            '--no-sandbox',
                            '--disable-gpu',
                            '--disable-web-resources',
                            '--disable-component-extensions-with-background-pages',
                        ]
                    ),
                    timeout=60
                )
                page = await browser.new_page(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                # 添加隱藏 WebDriver 標誌
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                """)
                
                self.progress.emit("[Playwright] ✓ 瀏覽器已啟動（已應用反檢測）")
                
                try:
                    # 檢查登錄狀態
                    self.progress.emit("[登錄] 檢查 Tixcraft 登錄狀態...")
                    await asyncio.wait_for(page.goto("https://tixcraft.com/user"), timeout=15)
                    await asyncio.sleep(2)
                    
                    # 嘗試查找登出按鈕
                    is_logged_in = False
                    try:
                        logout_btn = page.locator("a:has-text('登出')").first
                        is_logged_in = await logout_btn.is_visible(timeout=2000)
                    except:
                        is_logged_in = False
                    
                    if not is_logged_in:
                        self.progress.emit("[登錄] 未登錄，導向 Google SSO...")
                        await asyncio.wait_for(page.goto("https://tixcraft.com/login"), timeout=15)
                        await asyncio.sleep(3)
                        
                        # 尋找和點擊 Google 按鈕
                        self.progress.emit("[登錄] 尋找 Google 登錄按鈕...")
                        
                        # 嘗試多種方式尋找按鈕
                        google_btn = None
                        
                        # 方式 1: 查找所有按鈕
                        all_buttons = await page.locator("button").all()
                        self.progress.emit(f"[登錄] 頁面有 {len(all_buttons)} 個按鈕")
                        
                        for i, btn in enumerate(all_buttons):
                            try:
                                text = await btn.text_content()
                                if text and 'Google' in text:
                                    google_btn = btn
                                    self.progress.emit(f"[登錄] ✓ 找到 Google 按鈕 (第 {i+1} 個)")
                                    break
                            except:
                                pass
                        
                        # 方式 2: 如果沒找到，用 CSS 選擇器
                        if not google_btn:
                            try:
                                google_btn = page.locator("button[onclick*='google'], a[href*='google']").first
                                self.progress.emit("[登錄] ✓ 用選擇器找到 Google 按鈕")
                            except:
                                pass
                        
                        # 點擊 Google 按鈕後，等待頁面導航
                        if google_btn:
                            self.progress.emit("[登錄] 點擊 Google 按鈕...")
                            try:
                                await google_btn.click(timeout=5000)
                                self.progress.emit("[登錄] ✓ 已點擊 Google 按鈕")
                                
                                # 重要: 等待頁面開始導航到 Google
                                self.progress.emit("[登錄] ⏳ 等待頁面導航到 Google...")
                                await asyncio.wait_for(
                                    page.wait_for_url("**/accounts.google.com/**"),
                                    timeout=15
                                )
                                self.progress.emit("[登錄] ✓ 已進入 Google 頁面")
                            except asyncio.TimeoutError:
                                self.progress.emit("[登錄] ⚠ 頁面導航超時，嘗試手動輸入...")
                            except Exception as e:
                                self.progress.emit(f"[登錄] ✗ 點擊失敗: {str(e)}")
                        else:
                            self.progress.emit("[登錄] ✗ 找不到按鈕，嘗試第二個")
                            if len(all_buttons) > 1:
                                try:
                                    await all_buttons[1].click()
                                    self.progress.emit("[登錄] ✓ 點擊第二個按鈕")
                                    await asyncio.sleep(5)
                                except:
                                    pass
                        
                        # 自動輸入 Google 帳號和密碼
                        self.progress.emit("[Google SSO] 準備自動登錄...")
                        
                        # 等待並輸入帳號
                        self.progress.emit("[Google SSO] ⏳ 等待帳號輸入字段加載...")
                        try:
                            # 先等待頁面完全加載
                            await page.wait_for_load_state("networkidle", timeout=10000)
                            self.progress.emit("[Google SSO] ✓ Google 頁面已加載")
                            
                            await asyncio.sleep(2)
                            
                            # 嘗試找到帳號輸入字段（多種選擇器）
                            email_selectors = [
                                "input[type='email']",
                                "input[name='email']",
                                "input[name='identifier']",
                                "input#identifierId",
                                "input[aria-label*='email']",
                                "input[aria-label*='帳號']",
                            ]
                            
                            email_field = None
                            for selector in email_selectors:
                                try:
                                    field = page.locator(selector).first
                                    if await field.is_visible(timeout=2000):
                                        email_field = field
                                        self.progress.emit(f"[Google SSO] ✓ 找到帳號字段 (選擇器: {selector})")
                                        break
                                except:
                                    pass
                            
                            if not email_field:
                                # 最後的備選方案：用 XPath 尋找所有輸入字段
                                all_inputs = await page.locator("input").all()
                                self.progress.emit(f"[Google SSO] ℹ 頁面有 {len(all_inputs)} 個輸入字段")
                                if len(all_inputs) > 0:
                                    email_field = all_inputs[0]
                                    self.progress.emit("[Google SSO] ✓ 使用第一個輸入字段")
                            
                            if email_field:
                                # 添加延遲確保字段完全可交互
                                await asyncio.sleep(1)
                                
                                # 輸入帳號
                                self.progress.emit(f"[Google SSO] 輸入帳號: {google_email}")
                                
                                # 使用多種方式輸入
                                try:
                                    # 方式 1: 先點擊，再清空，再輸入
                                    await email_field.click(timeout=2000)
                                    await asyncio.sleep(0.5)
                                    await email_field.fill("", timeout=2000)
                                    await asyncio.sleep(0.3)
                                except:
                                    pass
                                
                                # 逐字輸入
                                await email_field.type(google_email, delay=100)
                                self.progress.emit("[Google SSO] ✓ 帳號輸入成功")
                                
                                # 等待並點擊「下一步」
                                await asyncio.sleep(1)
                                self.progress.emit("[Google SSO] 點擊下一步...")
                                
                                next_selectors = [
                                    "button:has-text('下一步')",
                                    "button:has-text('Next')",
                                    "#identifierNext",
                                    "button[type='button']",
                                ]
                                
                                next_clicked = False
                                for selector in next_selectors:
                                    try:
                                        btn = page.locator(selector).first
                                        if await btn.is_visible(timeout=2000):
                                            await btn.click(timeout=5000)
                                            self.progress.emit(f"[Google SSO] ✓ 已點擊下一步")
                                            next_clicked = True
                                            break
                                    except:
                                        pass
                                
                                if not next_clicked:
                                    # 按 Enter 鍵
                                    await email_field.press("Enter")
                                    self.progress.emit("[Google SSO] ✓ 按 Enter 鍵")
                                
                                # 等待密碼頁面加載
                                await asyncio.sleep(4)
                                self.progress.emit("[Google SSO] ⏳ 等待密碼輸入字段加載...")
                                await page.wait_for_load_state("networkidle", timeout=10000)
                                self.progress.emit("[Google SSO] ✓ 密碼頁面已加載")
                                
                                await asyncio.sleep(2)
                                
                                # 尋找密碼輸入字段
                                password_selectors = [
                                    "input[type='password']",
                                    "input[name='password']",
                                    "input[name='passwd']",
                                    "input#password",
                                    "input[aria-label*='password']",
                                    "input[aria-label*='密碼']",
                                ]
                                
                                password_field = None
                                for selector in password_selectors:
                                    try:
                                        field = page.locator(selector).first
                                        if await field.is_visible(timeout=2000):
                                            password_field = field
                                            self.progress.emit(f"[Google SSO] ✓ 找到密碼字段 (選擇器: {selector})")
                                            break
                                    except:
                                        pass
                                
                                if not password_field:
                                    # 備選方案
                                    all_inputs = await page.locator("input").all()
                                    self.progress.emit(f"[Google SSO] ℹ 頁面有 {len(all_inputs)} 個輸入字段")
                                    if len(all_inputs) > 0:
                                        password_field = all_inputs[0]
                                        self.progress.emit("[Google SSO] ✓ 使用第一個輸入字段")
                                
                                if password_field:
                                    # 添加延遲確保字段完全可交互
                                    await asyncio.sleep(1)
                                    
                                    # 輸入密碼
                                    self.progress.emit("[Google SSO] 輸入密碼...")
                                    
                                    # 使用多種方式輸入
                                    try:
                                        await password_field.click(timeout=2000)
                                        await asyncio.sleep(0.5)
                                        await password_field.fill("", timeout=2000)
                                        await asyncio.sleep(0.3)
                                    except:
                                        pass
                                    
                                    # 逐字輸入
                                    await password_field.type(google_password, delay=100)
                                    self.progress.emit("[Google SSO] ✓ 密碼輸入成功")
                                    
                                    # 等待並點擊「下一步」
                                    await asyncio.sleep(1)
                                    self.progress.emit("[Google SSO] 點擊下一步...")
                                    
                                    next_clicked = False
                                    for selector in next_selectors:
                                        try:
                                            btn = page.locator(selector).first
                                            if await btn.is_visible(timeout=2000):
                                                await btn.click(timeout=5000)
                                                self.progress.emit(f"[Google SSO] ✓ 已點擊下一步")
                                                next_clicked = True
                                                break
                                        except:
                                            pass
                                    
                                    if not next_clicked:
                                        # 按 Enter 鍵
                                        await password_field.press("Enter")
                                        self.progress.emit("[Google SSO] ✓ 按 Enter 鍵")
                                    
                                    await asyncio.sleep(3)
                                else:
                                    self.progress.emit("[Google SSO] ✗ 找不到密碼輸入字段")
                                    self.progress.emit("[Google SSO] ⏳ 等待手動登錄 (120 秒)...")
                            else:
                                self.progress.emit("[Google SSO] ✗ 找不到帳號輸入字段")
                                self.progress.emit("[Google SSO] ⏳ 等待手動登錄 (120 秒)...")
                        except asyncio.TimeoutError as e:
                            self.progress.emit(f"[Google SSO] ✗ 超時: {str(e)}")
                            self.progress.emit("[Google SSO] ⏳ 等待手動登錄 (120 秒)...")
                        except Exception as e:
                            self.progress.emit(f"[Google SSO] ✗ 自動登錄失敗: {str(e)}")
                            import traceback
                            self.progress.emit(f"[Google SSO] 詳細: {traceback.format_exc()[:200]}")
                            self.progress.emit("[Google SSO] ⏳ 等待手動登錄 (120 秒)...")
                        
                        # [第1步] 等待返回 Tixcraft - 檢查完成後才繼續
                        self.progress.emit("[第1步] ⏳ 等待 Google 認證完成 (120 秒超時)...")
                        login_success = False
                        start_time = datetime.now()
                        while (datetime.now() - start_time).total_seconds() < 120:
                            try:
                                current_url = page.url
                                if "tixcraft.com" in current_url and "google" not in current_url.lower():
                                    self.progress.emit("[第1步] ✓ 已返回 Tixcraft，Google 登錄成功")
                                    login_success = True
                                    break
                            except:
                                pass
                            await asyncio.sleep(2)
                        
                        # 確認第 1 步完成
                        if not login_success:
                            self.progress.emit("[第1步] ✗ Google 登錄失敗，超時 120 秒")
                            self.error.emit("Google 登錄失敗")
                            return
                        
                        self.progress.emit("[第1步] ✓✓✓ 第 1 步完成: Google 登錄成功")
                        await asyncio.sleep(2)  # 確認延遲
                    else:
                        self.progress.emit("[第1步] ✓ 已登錄，跳過 Google 認證")
                        self.progress.emit("[第1步] ✓✓✓ 第 1 步完成: 無需登錄")
                    
                    # [第2步] 導航到表單 - 檢查完成後才繼續
                    self.progress.emit("[第2步] 導航到註冊頁面...")
                    try:
                        await asyncio.wait_for(page.goto("https://tixcraft.com/user/register", wait_until="load"), timeout=20)
                        self.progress.emit("[第2步] ✓ 頁面導航成功")
                    except Exception as e:
                        self.progress.emit(f"[第2步] ⚠ 頁面加載超時: {str(e)[:30]}")
                    
                    # 等待頁面完全加載 - 檢查完成
                    self.progress.emit("[第2步] ⏳ 等待表單頁面完全加載...")
                    await asyncio.sleep(3)
                    try:
                        await page.wait_for_load_state("networkidle", timeout=15000)
                        self.progress.emit("[第2步] ✓ 頁面完全加載")
                    except Exception as e:
                        self.progress.emit(f"[第2步] ⚠ 等待加載超時: {str(e)[:30]}")
                    
                    await asyncio.sleep(2)
                    
                    # 驗證表單頁面是否加載成功
                    page_valid = False
                    try:
                        form_content = await page.content()
                        if "register" not in form_content.lower() or len(form_content) < 1000:
                            self.progress.emit("[第2步] ✗ 致命錯誤：頁面內容不完整 → 停止流程")
                            return  # 直接停止
                        else:
                            self.progress.emit("[第2步] ✓ 表單頁面驗證通過")
                            page_valid = True
                    except Exception as e:
                        self.progress.emit(f"[第2步] ✗ 致命錯誤：無法驗證表單頁面 ({str(e)[:20]}) → 停止流程")
                        return  # 直接停止
                    
                    self.progress.emit("[第2步] ✓✓✓ 第 2 步完成: 表單頁面加載完成")
                    await asyncio.sleep(2)  # 確認延遲
                    
                    # [第3步] 填寫主要欄位 - 檢查完成後才繼續
                    self.progress.emit("[第3步] 開始填寫主要欄位...")
                    await self._fill_form(page, name, roc_id, birthday, email, gender)
                    self.progress.emit("[第3步] ✓ 主要欄位填寫完成")
                    await asyncio.sleep(2)  # 確認延遲
                    self.progress.emit("[第3步] ✓✓✓ 第 3 步完成: 主要欄位已填寫")
                    await asyncio.sleep(2)  # 確認延遲
                    
                    # [第4步] 自動填寫所有帶*的必填欄位 - 檢查完成後才繼續
                    self.progress.emit("[第4步] 開始填寫必填欄位...")
                    await asyncio.sleep(1)
                    
                    # 使用簡化版填寫（只填可見的欄位）
                    filled_required = await self._fill_required_fields(page)
                    
                    # 檢查是否成功填寫
                    if filled_required == 0:
                        self.progress.emit("[第4步] ℹ️  提示：無法自動填寫部分欄位")
                        await asyncio.sleep(1)
                    else:
                        self.progress.emit(f"[第4步] ✓ 成功填寫 {filled_required} 個欄位")
                        await asyncio.sleep(1)
                        self.progress.emit("[第4步] ✓✓✓ 第 4 步完成: 所有必填欄位已填寫")
                        await asyncio.sleep(2)  # 確認延遲
                    
                    # [第5步] 等待用戶手動操作 - 瀏覽器永遠保持開啟
                    self.progress.emit("[第5步] ✓ 自動填寫完成！")
                    self.progress.emit("[第5步] ")
                    self.progress.emit("[第5步] 🔄 現在請您在瀏覽器中手動操作：")
                    self.progress.emit("[第5步] 1️⃣  驗證所有自動填寫的欄位")
                    self.progress.emit("[第5步] 2️⃣  如需要，輸入驗證碼")
                    self.progress.emit("[第5步] 3️⃣  檢查地址和其他資訊")
                    self.progress.emit("[第5步] 4️⃣  點擊提交按鈕")
                    self.progress.emit("[第5步] ")
                    self.progress.emit("[第5步] ✅ 瀏覽器將保持開啟，請自行操作並關閉")
                    self.progress.emit(f"[成功] 帳號資訊: {name} - {roc_id}")
                    self.success.emit(f"✓ 自動填寫完成! {name} - {roc_id}")
                    self.waiting_for_manual.emit()  # 通知GUI
                    
                    # 瀏覽器保持開啟，等待用戶手動關閉或點停止
                    while self.running:
                        await asyncio.sleep(1)
                    
                finally:
                    # 關閉瀏覽器
                    if browser:
                        try:
                            await browser.close()
                        except:
                            pass
                    
        except asyncio.TimeoutError as e:
            self.progress.emit(f"[超時] {str(e)}")
            self.error.emit(f"超時: {str(e)}")
        except Exception as e:
            import traceback
            self.progress.emit(f"[錯誤] {traceback.format_exc()}")
            self.error.emit(str(e))
    
    async def _fill_form(self, page, name, roc_id, birthday, email, gender):
        """填寫表單 - 按特定順序操作"""
        try:
            # 等待頁面完全加載
            self.progress.emit("[填寫] ⏳ 等待頁面加載...")
            await asyncio.sleep(3)
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass
            await asyncio.sleep(2)
            
            # 獲取用戶的電話號碼
            phone = self.config.get("phone", "")
            if not phone:
                phone = f"09{random.randint(10000000, 99999999)}"
            
            def get_delay():
                """獲取 1.5-2.5 秒的隨機延遲"""
                return random.uniform(1.5, 2.5)
            
            # ========== 步驟 1: 選擇「中華民國國籍」 ==========
            self.progress.emit("[步驟1] 準備選擇國籍為「中華民國」...")
            
            domestic_clicked = False
            
            # 方法1: 直接尋找所有單選按鈕，找「中華民國」
            try:
                all_labels = await page.locator("label").all()
                for label in all_labels:
                    label_text = await label.text_content()
                    if label_text and "中華民國" in label_text:
                        # 嘗試找到關聯的 radio button
                        label_for = await label.get_attribute("for")
                        radio = None
                        
                        if label_for:
                            radio = page.locator(f"#{label_for}")
                        else:
                            # 在 label 內尋找 radio
                            radio = label.locator("input[type='radio']").first
                        
                        if radio:
                            try:
                                if await radio.is_visible(timeout=1000):
                                    await radio.click(timeout=1000)
                                    self.progress.emit("[步驟1] ✓ 已點擊「中華民國國籍」單選按鈕")
                                    domestic_clicked = True
                                    await asyncio.sleep(get_delay())
                                    break
                            except:
                                pass
            except Exception as e:
                pass
            
            # 方法2: 尋找第一個未被選中的「國籍」單選按鈕（通常是中華民國）
            if not domestic_clicked:
                try:
                    self.progress.emit("[步驟1] 嘗試尋找第一個國籍單選按鈕...")
                    # 找到所有國籍相關的單選按鈕
                    radios = await page.locator("input[type='radio'][name*='nation'], input[type='radio'][name*='country']").all()
                    if len(radios) > 0:
                        # 點擊第一個（通常是中華民國）
                        await radios[0].click(timeout=1000)
                        self.progress.emit("[步驟1] ✓ 已點擊第一個國籍單選按鈕（中華民國）")
                        domestic_clicked = True
                        await asyncio.sleep(get_delay())
                except Exception as e:
                    pass
            
            # 方法3: 通用方法 - 尋找任何帶有「中華民國」的可點擊元素
            if not domestic_clicked:
                try:
                    self.progress.emit("[步驟1] 嘗試通用方法...")
                    clickables = await page.locator("input[type='radio'], button, a, span").all()
                    for elem in clickables:
                        try:
                            text = await elem.text_content()
                            parent_text = await elem.locator("xpath=./..").text_content()
                            full_text = (text or "") + (parent_text or "")
                            
                            if "中華民國" in full_text:
                                await elem.click(timeout=1000)
                                self.progress.emit("[步驟1] ✓ 已點擊中華民國國籍")
                                domestic_clicked = True
                                await asyncio.sleep(get_delay())
                                break
                        except:
                            pass
                except:
                    pass
            
            if not domestic_clicked:
                self.progress.emit("[步驟1] ⚠ 找不到國籍選擇（可能已預設）")
            
            # ========== 步驟 1.5: 選擇性別（隨機男或女） ==========
            self.progress.emit("[步驟1.5] 準備選擇性別...")
            gender_selectors = [
                "input[type='radio'][name*='gender']",
                "input[type='radio'][name*='sex']",
                "input[type='radio'][id*='gender']",
                "input[type='radio']",  # 備選：所有 radio button
            ]
            
            gender_clicked = False
            for sel in gender_selectors:
                try:
                    radios = await page.locator(sel).all()
                    if len(radios) >= 1:
                        # 隨機選擇一個（男或女）
                        selected_radio = random.choice(radios)
                        if await selected_radio.is_visible(timeout=1000):
                            await selected_radio.click(timeout=1000)
                            # 嘗試獲取標籤文字
                            radio_label = await selected_radio.get_attribute("value")
                            if not radio_label:
                                radio_label = "性別"
                            self.progress.emit(f"[步驟1.5] ✓ 已選擇性別: {radio_label}")
                            gender_clicked = True
                            await asyncio.sleep(get_delay())
                            break
                except Exception as e:
                    pass
            
            if not gender_clicked:
                self.progress.emit("[步驟1.5] ⚠ 找不到性別選項")
            
            # ========== 步驟 2: 輸入姓名（點擊後輸入） ==========
            self.progress.emit(f"[步驟2] 準備輸入姓名: {name}")
            name_selectors = [
                "input[id*='name']",
                "input[placeholder*='名']",
                "input[placeholder*='Name']",
                "input[name*='name']",
                "input[name*='fullname']",
            ]
            
            name_filled = False
            for sel in name_selectors:
                try:
                    field = page.locator(sel).first
                    if await field.is_visible(timeout=1000):
                        await field.click(timeout=1000)
                        await asyncio.sleep(0.3)
                        await field.fill("", timeout=500)  # 清空
                        await field.type(name, delay=50)  # 逐字輸入
                        self.progress.emit(f"[步驟2] ✓ 已輸入姓名: {name}")
                        name_filled = True
                        await asyncio.sleep(get_delay())
                        break
                except Exception as e:
                    pass
            
            if not name_filled:
                self.progress.emit("[步驟2] ⚠ 姓名欄位未找到")
            
            # ========== 步驟 3: 輸入身分證號（點擊後輸入） ==========
            self.progress.emit(f"[步驟3] 準備輸入身分證: {roc_id}")
            id_selectors = [
                "input[id*='identity']",
                "input[id*='card']",
                "input[name*='identity']",
                "input[placeholder*='身分']",
                "input[placeholder*='ID']",
                "input[placeholder*='證']",
            ]
            
            id_filled = False
            for sel in id_selectors:
                try:
                    field = page.locator(sel).first
                    if await field.is_visible(timeout=1000):
                        await field.click(timeout=1000)
                        await asyncio.sleep(0.3)
                        await field.fill("", timeout=500)  # 清空
                        await field.type(roc_id, delay=50)  # 逐字輸入
                        self.progress.emit(f"[步驟3] ✓ 已輸入身分證: {roc_id}")
                        id_filled = True
                        await asyncio.sleep(get_delay())
                        break
                except Exception as e:
                    pass
            
            if not id_filled:
                self.progress.emit("[步驟3] ⚠ 身分證欄位未找到")
            
            # ========== 步驟 4: 輸入生日（點擊後輸入） ==========
            self.progress.emit(f"[步驟4] 準備輸入生日: {birthday}")
            bd_selectors = [
                "input[id*='birthday']",
                "input[name*='birthday']",
                "input[placeholder*='生日']",
                "input[placeholder*='Birth']",
                "input[type='date']",
                "input[placeholder*='出生']",
            ]
            
            bd_filled = False
            for sel in bd_selectors:
                try:
                    field = page.locator(sel).first
                    if await field.is_visible(timeout=1000):
                        await field.click(timeout=1000)
                        await asyncio.sleep(0.3)
                        await field.fill("", timeout=500)  # 清空
                        await field.type(birthday, delay=50)  # 逐字輸入
                        self.progress.emit(f"[步驟4] ✓ 已輸入生日: {birthday}")
                        bd_filled = True
                        await asyncio.sleep(get_delay())
                        break
                except Exception as e:
                    pass
            
            if not bd_filled:
                self.progress.emit("[步驟4] ⚠ 生日欄位未找到")
            
            # ========== 步驟 5: 輸入電話 ==========
            # （不使用國碼下拉鍵，直接輸入電話號碼）
            self.progress.emit(f"[步驟5] 準備輸入電話: {phone}")
            phone_selectors = [
                "input[name*='phone']",
                "input[id*='phone']",
                "input[placeholder*='電話']",
                "input[placeholder*='Phone']",
                "input[placeholder*='手機']",
                "input[type='tel']",
            ]
            
            phone_filled = False
            for sel in phone_selectors:
                try:
                    field = page.locator(sel).first
                    if await field.is_visible(timeout=1000):
                        await field.click(timeout=1000)
                        await asyncio.sleep(0.3)
                        await field.fill("", timeout=500)  # 清空
                        await field.type(phone, delay=50)  # 逐字輸入
                        self.progress.emit(f"[步驟5] ✓ 已輸入電話: {phone}")
                        phone_filled = True
                        await asyncio.sleep(get_delay())
                        break
                except Exception as e:
                    pass
            
            if not phone_filled:
                self.progress.emit("[步驟5] ⚠ 電話欄位未找到")
            
            self.progress.emit("[填寫] ✓ 主要欄位填寫完成")
        except Exception as e:
            import traceback
            self.progress.emit(f"[填寫] ✗ 錯誤: {str(e)}")
            self.progress.emit(f"[填寫] 詳細: {traceback.format_exc()[:100]}")
    
    
    async def _fill_required_fields(self, page):
        """自動填寫必填欄位：縣市、區市鄉鎮、地址、郵箱（含詳細日誌）"""
        try:
            self.progress.emit("[必填] 掃描必填欄位...")
            await asyncio.sleep(1)
            
            filled_count = 0
            processed_fields = set()  # 避免重複填寫
            
            # 首先列出所有 label
            labels = await page.locator("label").all()
            self.progress.emit(f"[必填] 🔍 掃描到 {len(labels)} 個 label 元素")
            
            # ========== 策略 1: 通過 label 和 * 符號掃描 ==========
            required_labels_found = []
            
            for idx, label in enumerate(labels):
                try:
                    text = await label.text_content()
                    if text and '*' in text:
                        field_label = text.replace('*', '').strip()
                        required_labels_found.append(field_label)
                except:
                    pass
            
            self.progress.emit(f"[必填] ⭐ 找到 {len(required_labels_found)} 個必填欄位: {', '.join(required_labels_found[:5])}")
            
            for label_idx, label in enumerate(labels):
                try:
                    text = await label.text_content()
                    if not text or '*' not in text:
                        continue
                    
                    field_label = text.replace('*', '').strip().lower()
                    self.progress.emit(f"[必填] 📋 [{label_idx+1}] 處理欄位: {field_label}")
                    
                    # 尋找關聯的輸入框
                    label_for = await label.get_attribute("for")
                    field = None
                    field_type = None
                    field_tag = None
                    
                    if label_for:
                        field = page.locator(f"#{label_for}")
                    else:
                        field = label.locator("input, select, textarea").first
                        if not field:
                            parent = label.locator("xpath=.//ancestor::div[1]")
                            field = parent.locator("input, select, textarea").first
                    
                    if field:
                        try:
                            # 改進：不再強制檢查 is_visible，改為直接嘗試交互
                            # （某些字段可能被 CSS 隱藏但仍可互動）
                            try:
                                is_visible = await field.is_visible(timeout=300)
                            except:
                                is_visible = False
                                self.progress.emit(f"[必填]   ⚠️  可見性檢查超時，嘗試直接交互")
                            
                            if not is_visible:
                                self.progress.emit(f"[必填]   ⚠️  字段不可見，但仍嘗試交互...")
                            
                            field_tag = await field.evaluate("el => el.tagName.toLowerCase()")
                            field_type = await field.get_attribute("type")
                            field_id = await field.get_attribute("id")
                            field_name = await field.get_attribute("name")
                            
                            self.progress.emit(f"[必填]   📌 找到欄位: tag={field_tag}, type={field_type}, id={field_id}, name={field_name}")
                            
                            # 避免重複填寫
                            field_key = (field_id, field_name)
                            if field_key in processed_fields:
                                self.progress.emit(f"[必填]   ⏭️  已填過，跳過")
                                continue
                            processed_fields.add(field_key)
                            
                            # ===== 縣市 下拉菜單 =====
                            if field_tag == "select" and ("縣市" in field_label or "county" in field_label or "city" in field_label):
                                try:
                                    options = await field.locator("option").all()
                                    self.progress.emit(f"[必填]   📍 縣市下拉: {len(options)} 個選項")
                                    
                                    if len(options) > 1:
                                        selected = random.choice(options[1:])
                                        opt_value = await selected.get_attribute("value")
                                        opt_text = await selected.text_content()
                                        await field.click(timeout=1000)
                                        await asyncio.sleep(0.3)
                                        await field.select_option(opt_value)
                                        self.progress.emit(f"[必填]   ✓ 縣市已選: {opt_text.strip()}")
                                        filled_count += 1
                                        await asyncio.sleep(0.5)
                                        continue
                                except Exception as e:
                                    self.progress.emit(f"[必填]   ✗ 縣市選擇失敗: {str(e)[:40]}")
                            
                            # ===== 區市鄉鎮 下拉菜單 =====
                            if field_tag == "select" and ("區市鄉鎮" in field_label or "district" in field_label or "township" in field_label):
                                try:
                                    options = await field.locator("option").all()
                                    self.progress.emit(f"[必填]   📍 區市下拉: {len(options)} 個選項")
                                    
                                    if len(options) > 1:
                                        selected = random.choice(options[1:])
                                        opt_value = await selected.get_attribute("value")
                                        opt_text = await selected.text_content()
                                        await field.click(timeout=1000)
                                        await asyncio.sleep(0.3)
                                        await field.select_option(opt_value)
                                        self.progress.emit(f"[必填]   ✓ 區市已選: {opt_text.strip()}")
                                        filled_count += 1
                                        await asyncio.sleep(0.3)
                                        continue
                                except Exception as e:
                                    self.progress.emit(f"[必填]   ✗ 區市選擇失敗: {str(e)[:40]}")
                            
                            # ===== 地址 / 收件地址 =====
                            if "地址" in field_label or "address" in field_label or "收件" in field_label:
                                try:
                                    self.progress.emit(f"[必填]   🏠 嘗試填寫地址/收件地址...")
                                    
                                    if field_tag == "select":
                                        options = await field.locator("option").all()
                                        self.progress.emit(f"[必填]   📍 地址下拉: {len(options)} 個選項")
                                        
                                        if len(options) > 1:
                                            selected = random.choice(options[1:])
                                            opt_value = await selected.get_attribute("value")
                                            opt_text = await selected.text_content()
                                            await field.click(timeout=1000)
                                            await asyncio.sleep(0.2)
                                            await field.select_option(opt_value)
                                            self.progress.emit(f"[必填]   ✓ 地址已選")
                                            filled_count += 1
                                        else:
                                            self.progress.emit(f"[必填]   ⚠️  沒有可選的地址選項")
                                    else:
                                        # 文本輸入
                                        address = self.generator.generate_address()
                                        try:
                                            await field.click(timeout=1000)
                                        except:
                                            pass
                                        await asyncio.sleep(0.2)
                                        try:
                                            await field.fill(address, timeout=2000)
                                        except:
                                            await field.clear()
                                            await field.type(address)
                                        self.progress.emit(f"[必填]   ✓ 地址已填: {address[:30]}")
                                        filled_count += 1
                                    continue
                                except Exception as e:
                                    self.progress.emit(f"[必填]   ✗ 地址填寫失敗: {str(e)[:40]}")
                            
                            # ===== 郵件 / 信箱 / 電子郵件 =====
                            if ("郵件" in field_label or "電子" in field_label or "email" in field_label or 
                                "信箱" in field_label or "mail" in field_label):
                                try:
                                    self.progress.emit(f"[必填]   📧 嘗試填寫郵件...")
                                    email = "qiuzien990618@gmail.com"
                                    
                                    try:
                                        await field.click(timeout=1000)
                                    except:
                                        pass
                                    
                                    await asyncio.sleep(0.2)
                                    
                                    # 嘗試多種填寫方式
                                    try:
                                        await field.fill(email, timeout=2000)
                                    except:
                                        try:
                                            await field.clear()
                                            await field.type(email, delay=50)
                                        except:
                                            # 最後的嘗試：通過 JavaScript 設置值
                                            await field.evaluate(f"el => el.value = '{email}'")
                                    
                                    self.progress.emit(f"[必填]   ✓ 郵箱已填: {email}")
                                    filled_count += 1
                                    continue
                                except Exception as e:
                                    self.progress.emit(f"[必填]   ✗ 郵箱填寫失敗: {str(e)[:40]}")
                            
                            # ===== 名字 =====
                            if "名字" in field_label or "姓名" in field_label or "name" in field_label:
                                try:
                                    name = self.config.get("name", f"User{random.randint(1000, 9999)}")
                                    await field.click(timeout=1000)
                                    await asyncio.sleep(0.2)
                                    await field.fill(name, timeout=2000)
                                    self.progress.emit(f"[必填]   ✓ 名字已填: {name}")
                                    filled_count += 1
                                    continue
                                except Exception as e:
                                    self.progress.emit(f"[必填]   ✗ 名字填寫失敗: {str(e)[:40]}")
                            
                            # ===== 身分字號 =====
                            if "身分" in field_label or "證件" in field_label or "id" in field_label:
                                try:
                                    roc_id = self.generator.generate_roc_id()
                                    await field.click(timeout=1000)
                                    await asyncio.sleep(0.2)
                                    await field.fill(roc_id, timeout=2000)
                                    self.progress.emit(f"[必填]   ✓ 身分字號已填: {roc_id}")
                                    filled_count += 1
                                    continue
                                except Exception as e:
                                    self.progress.emit(f"[必填]   ✗ 身分字號填寫失敗: {str(e)[:40]}")
                            
                            self.progress.emit(f"[必填]   ⏭️  未知欄位，跳過")
                        
                        except Exception as e:
                            self.progress.emit(f"[必填]   ✗ 欄位檢查失敗: {str(e)[:40]}")
                    else:
                        self.progress.emit(f"[必填]   ✗ 找不到關聯的輸入框")
                
                except Exception as e:
                    self.progress.emit(f"[必填] ✗ 処理 label 失敗: {str(e)[:40]}")
            
            self.progress.emit(f"[必填] ✅ 自動填寫完成: {filled_count} 個欄位")
            
            # ========== 如果沒有填寫到郵箱或地址，使用備選選擇器 ==========
            if filled_count == 0:
                self.progress.emit("[必填] 💡 嘗試備選策略：直接選擇器尋找...")
                
                # 嘗試直接尋找郵箱欄位
                email_selectors = [
                    "input[type='email']",
                    "input[name*='email']",
                    "input[name*='mail']",
                    "input[id*='email']",
                    "input[placeholder*='郵']",
                    "input[placeholder*='email']",
                    "input[placeholder*='信箱']",
                ]
                
                for sel in email_selectors:
                    try:
                        field = page.locator(sel).first
                        try:
                            if await field.is_visible(timeout=300):
                                await field.click(timeout=1000)
                                await asyncio.sleep(0.2)
                                await field.fill("qiuzien990618@gmail.com", timeout=2000)
                                self.progress.emit("[必填] ✓ 郵箱已填 (備選): qiuzien990618@gmail.com")
                                filled_count += 1
                                break
                        except:
                            # 即使不可見也嘗試
                            try:
                                await field.fill("qiuzien990618@gmail.com", timeout=2000)
                                self.progress.emit("[必填] ✓ 郵箱已填 (備選): qiuzien990618@gmail.com")
                                filled_count += 1
                                break
                            except:
                                pass
                    except:
                        pass
                
                # 嘗試直接尋找地址欄位
                address_selectors = [
                    "select[name*='address']",
                    "select[id*='address']",
                    "input[name*='address']",
                    "input[id*='address']",
                    "textarea[name*='address']",
                    "textarea[id*='address']",
                ]
                
                for sel in address_selectors:
                    try:
                        field = page.locator(sel).first
                        try:
                            if await field.is_visible(timeout=300):
                                field_tag = await field.evaluate("el => el.tagName.toLowerCase()")
                                if field_tag == "select":
                                    options = await field.locator("option").all()
                                    if len(options) > 1:
                                        selected = random.choice(options[1:])
                                        await field.select_option(await selected.get_attribute("value"))
                                        self.progress.emit("[必填] ✓ 地址已選 (備選)")
                                        filled_count += 1
                                        break
                                else:
                                    address = self.generator.generate_address()
                                    await field.fill(address, timeout=2000)
                                    self.progress.emit("[必填] ✓ 地址已填 (備選)")
                                    filled_count += 1
                                    break
                        except:
                            # 即使不可見也嘗試
                            try:
                                field_tag = await field.evaluate("el => el.tagName.toLowerCase()")
                                if field_tag != "select":
                                    address = self.generator.generate_address()
                                    await field.fill(address, timeout=2000)
                                    self.progress.emit("[必填] ✓ 地址已填 (備選)")
                                    filled_count += 1
                                    break
                            except:
                                pass
                    except:
                        pass
                
                self.progress.emit(f"[必填] 備選策略完成: 額外填寫 {filled_count} 個欄位")
            
            return filled_count
            
        except Exception as e:
            import traceback
            self.progress.emit(f"[必填] ✗ 致命錯誤: {str(e)}")
            self.progress.emit(f"[必填] 詳細: {traceback.format_exc()[:200]}")
            return 0


class TixcraftGUI(QMainWindow):
    """主 GUI 窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tixcraft 自動註冊工具 v2.0 簡化版")
        self.setGeometry(100, 100, 800, 600)
        
        self.worker = None
        self.config = self._load_config()
        
        self._init_ui()
    
    def _load_config(self) -> Dict:
        """加載配置"""
        try:
            if os.path.exists("gui_config.json"):
                with open("gui_config.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {
            'phone': '3315003235',
            'country_code': '+1',
            'name': '',
            'count': 1,
            'google_email': '',
            'google_password': ''
        }
    
    def _save_config(self):
        """保存配置"""
        try:
            with open("gui_config.json", 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存失敗: {e}")
    
    def _init_ui(self):
        """初始化 UI"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        
        # 設定區
        layout.addWidget(QLabel("=== Google 帳號設定 ==="))
        
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Google 帳號:"))
        self.email_input = QLineEdit()
        self.email_input.setText(self.config.get('google_email', ''))
        self.email_input.setPlaceholderText("example@gmail.com")
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)
        
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel("Google 密碼:"))
        self.password_input = QLineEdit()
        self.password_input.setText(self.config.get('google_password', ''))
        self.password_input.setPlaceholderText("輸入密碼")
        self.password_input.setEchoMode(QLineEdit.Password)
        pwd_layout.addWidget(self.password_input)
        layout.addLayout(pwd_layout)
        
        layout.addWidget(QLabel("=== 註冊設定 ==="))
        
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("電話號碼:"))
        self.phone_input = QLineEdit()
        self.phone_input.setText(self.config.get('phone', ''))
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("姓名 (留空隨機):"))
        self.name_input = QLineEdit()
        self.name_input.setText(self.config.get('name', ''))
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 進度區
        layout.addWidget(QLabel("=== 進度 ==="))
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setMaximumHeight(250)
        layout.addWidget(self.progress_text)
        
        # 按鈕區
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("開始註冊")
        self.start_btn.setStyleSheet("background-color: green; color: white; font-weight: bold; padding: 10px;")
        self.start_btn.clicked.connect(self._start_registration)
        btn_layout.addWidget(self.start_btn)
        
        self.finish_btn = QPushButton("停止程序（關閉瀏覽器）")
        self.finish_btn.setStyleSheet("background-color: orange; color: white; font-weight: bold; padding: 10px;")
        self.finish_btn.clicked.connect(self._finish_manual_operation)
        self.finish_btn.setEnabled(False)  # 初始時禁用
        btn_layout.addWidget(self.finish_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setStyleSheet("background-color: red; color: white; padding: 10px;")
        self.stop_btn.clicked.connect(self._stop_registration)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        central.setLayout(layout)
        
        self._log("[啟動] GUI 初始化完成")
    
    def _start_registration(self):
        """開始註冊"""
        self._log("[開始] 正在啟動註冊工作...")
        
        # 檢查 Google 帳號和密碼
        google_email = self.email_input.text()
        google_password = self.password_input.text()
        
        if not google_email or not google_password:
            self.progress_text.setStyleSheet("background-color: #ffcccc;")
            self._log("[警告] ⚠ 請先輸入 Google 帳號和密碼!")
            QMessageBox.warning(self, "警告", "請先輸入 Google 帳號和密碼")
            return
        
        # 保存設定
        self.config['phone'] = self.phone_input.text()
        self.config['name'] = self.name_input.text()
        self.config['google_email'] = google_email
        self.config['google_password'] = google_password
        self._save_config()
        
        # 創建工作線程
        self.worker = RegistrationWorker(self.config)
        self.worker.progress.connect(self._log)
        self.worker.error.connect(self._on_error)
        self.worker.success.connect(self._on_success)
        self.worker.waiting_for_manual.connect(self._on_waiting_for_manual)  # 新增
        self.worker.start()
        
        self.start_btn.setEnabled(False)
    
    def _stop_registration(self):
        """停止註冊"""
        if self.worker:
            self.worker.running = False
            self._log("[停止] 正在停止...")
    
    def _on_waiting_for_manual(self):
        """Worker 通知等待用戶手動操作"""
        self.finish_btn.setEnabled(True)
        self._log("")
        self._log("💡 提示：手動操作完成後，點擊『停止程序』按鈕關閉瀏覽器")
        self._log("")
    
    def _finish_manual_operation(self):
        """用戶點擊『停止程序』按鈕"""
        if self.worker:
            self.worker.running = False
            self.finish_btn.setEnabled(False)
            self._log("[停止] 程序正在停止，瀏覽器將關閉...")
    
    def _on_error(self, error):
        """錯誤回調"""
        QMessageBox.critical(self, "錯誤", f"註冊失敗:\n{error}")
        self.start_btn.setEnabled(True)
    
    def _on_success(self, msg):
        """成功回調"""
        QMessageBox.information(self, "成功", msg)
        self.start_btn.setEnabled(True)
    
    def _log(self, msg):
        """添加日誌"""
        print(msg)
        self.progress_text.append(msg)
        # 自動滾到底
        self.progress_text.verticalScrollBar().setValue(
            self.progress_text.verticalScrollBar().maximum()
        )


if __name__ == "__main__":
    print("[啟動] 初始化 GUI...")
    
    if not GUI_AVAILABLE:
        print("[錯誤] PyQt5 不可用")
        sys.exit(1)
    
    try:
        print("[啟動] 創建應用...")
        app = QApplication(sys.argv)
        print("[啟動] ✓ 應用已創建")
        
        print("[啟動] 創建主窗口...")
        window = TixcraftGUI()
        window.resize(1000, 700)
        print("[啟動] ✓ 窗口已創建")
        
        print("[啟動] 顯示窗口...")
        window.show()
        app.processEvents()
        print("[啟動] ✓ 窗口已顯示")
        
        print("[啟動] 進入事件循環...")
        sys.stdout.flush()
        
        # 直接進入事件循環，不返回
        exit_code = app.exec_()
        print(f"[完成] 程序退出，代碼: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"[致命錯誤] {error_msg}")
        sys.exit(1)
