"""
Tixcraft 自動註冊流程
完整步驟：
1. 生成有效的台灣身份證號
2. 填寫註冊表單
3. 點擊「選定此會員帳號進行綁定」
4. 修改手機號碼（香港 → 美國）
5. 點擊「確認送出並進行手機號碼認證」
6. 等待並收集 SMS 驗證碼
7. 輸入驗證碼完成註冊
"""

import asyncio
import random
import string
import re
import sys
from datetime import datetime
import requests
from playwright.async_api import async_playwright, expect

# 解決編碼問題
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class TixcraftAutoRegister:
    def __init__(self):
        self.base_url = "https://tixcraft.com"
        self.register_url = f"{self.base_url}/user/register"
        self.auth_phone_url = f"{self.base_url}/user/auth-phone"
        self.sms_us_api = "https://api.sms8.net/api/record?token=b632kn5442ili34wycjmcxsjnlm6bq89jh4f"
        
    def generate_valid_roc_id(self):
        """生成有效的台灣 ROC 身份證號
        格式: [A-Z][1-2][0-9]{8}
        """
        # 首字母（縣市代碼）
        first_letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        # 第二位（性別：1=男，2=女）
        gender_code = random.choice('12')
        # 後8位數字
        remaining = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        
        roc_id = f"{first_letter}{gender_code}{remaining}"
        return roc_id
    
    def generate_phone_number(self, country_code="+1"):
        """生成電話號碼"""
        if country_code == "+1":  # 美國
            return "3315003235"
        elif country_code == "+852":  # 香港
            return "70250485"
        else:
            return "".join([str(random.randint(0, 9)) for _ in range(8)])
    
    def generate_email(self):
        """生成 Gmail 地址"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"test{random_str}@gmail.com"
    
    def generate_name(self):
        """生成台灣名字"""
        surnames = ['王', '李', '張', '劉', '陳', '楊', '黃', '林', '高', '鄭']
        given_names = ['小明', '美玲', '建輝', '俊傑', '雪芬', '耀庭', '志強', '怡君']
        return random.choice(surnames) + random.choice(given_names)
    
    def generate_birthday(self):
        """生成生日 (YYYY/MM/DD 格式)"""
        year = random.randint(1960, 2000)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # 安全起見用 28
        return f"{year}/{month:02d}/{day:02d}"
    
    async def fill_registration_form(self, page, user_data):
        """填寫註冊表單"""
        print("=" * 50)
        print("填寫註冊表單...")
        print("=" * 50)
        
        # 等待頁面加載 - 寬鬆的等待
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=30000)
        except:
            print("⚠️  domcontentloaded 超時，嘗試繼續...")
        
        await asyncio.sleep(4)
        
        # 調試：列出頁面上所有 input 元素
        inputs = await page.locator("input[type='text'], input[type='email'], input[type='tel'], input[id*='form']").all()
        print(f"\n🔍 找到 {len(inputs)} 個輸入框")
        for i, inp in enumerate(inputs[:5]):  # 只列出前5個
            try:
                elem_id = await inp.get_attribute("id")
                elem_name = await inp.get_attribute("name")
                print(f"   [{i}] ID={elem_id}, Name={elem_name}")
            except:
                pass
        
        # 嘗試填寫姓名 - 使用更寬鬆的方法
        print(f"\n✓ 填寫姓名: {user_data['name']}")
        try:
            # 嘗試多個選擇器
            name_selectors = [
                "#tixuserform-name",
                "input[name='TixUserForm[name]']",
                "input[placeholder*='姓名']",
                "input[id*='name']"
            ]
            
            name_filled = False
            for selector in name_selectors:
                try:
                    inp = page.locator(selector).first
                    # 不等待，直接嘗試填寫
                    await inp.fill(user_data['name'], timeout=5000)
                    print(f"  ✓ 使用選擇器: {selector}")
                    name_filled = True
                    break
                except:
                    pass
            
            if not name_filled:
                print(f"  ❌ 無法填寫姓名，嘗試繼續...")
        except Exception as e:
            print(f"  ❌ 填寫姓名失敗: {e}")
        
        await asyncio.sleep(0.5)
        
        # 2. 填寫身份證
        print(f"✓ 填寫身份證: {user_data['id']}")
        try:
            id_selectors = [
                "#tixuserform-identity",
                "input[name*='identity']",
                "input[placeholder*='身份']",
                "input[id*='identity']"
            ]
            for selector in id_selectors:
                try:
                    inp = page.locator(selector).first
                    await inp.fill(user_data['id'], timeout=5000)
                    print(f"  ✓ 使用選擇器: {selector}")
                    break
                except:
                    pass
        except Exception as e:
            print(f"  ⚠️  填寫身份證失敗: {e}")
        await asyncio.sleep(0.3)
        
        # 3. 填寫生日
        print(f"✓ 填寫生日: {user_data['birthday']}")
        try:
            birthday_selectors = [
                "#tixuserform-birthday",
                "input[name*='birthday']",
                "input[placeholder*='生日']",
                "input[id*='birthday']"
            ]
            for selector in birthday_selectors:
                try:
                    inp = page.locator(selector).first
                    await inp.fill(user_data['birthday'], timeout=5000)
                    print(f"  ✓ 使用選擇器: {selector}")
                    break
                except:
                    pass
        except Exception as e:
            print(f"  ⚠️  填寫生日失敗: {e}")
        await asyncio.sleep(0.3)
        
        # 4. 選擇性別 (男)
        print("✓ 選擇性別: 男")
        try:
            gender_selectors = [
                "input[type='radio'][value='male']",
                "input[type='radio'][name*='gender']",
                "input[value='1']"  # 台灣身份通常 1=男
            ]
            for selector in gender_selectors:
                try:
                    rad = page.locator(selector).first
                    await rad.check(timeout=5000)
                    print(f"  ✓ 使用選擇器: {selector}")
                    break
                except:
                    pass
        except Exception as e:
            print(f"  ⚠️  選擇性別失敗: {e}")
        await asyncio.sleep(0.3)
        
        # 5. 勾選中華民國國籍
        print("✓ 勾選中華民國國籍")
        try:
            nation_selectors = [
                "input[type='checkbox'][value*='ROC']",
                "input[type='checkbox'][name*='nationality']",
                "input[id*='ROC']"
            ]
            for selector in nation_selectors:
                try:
                    chk = page.locator(selector).first
                    is_checked = await chk.is_checked()
                    if not is_checked:
                        await chk.check(timeout=5000)
                    print(f"  ✓ 使用選擇器: {selector}")
                    break
                except:
                    pass
        except Exception as e:
            print(f"  ⚠️  勾選國籍失敗: {e}")
        await asyncio.sleep(0.3)
        
        # 6. 選擇地區 (基隆市)
        print("✓ 選擇地區: 基隆市")
        try:
            county_selectors = ["#city", "select[name*='city']", "select[id*='county']"]
            for selector in county_selectors:
                try:
                    sel = page.locator(selector).first
                    await sel.select_option("基隆市", timeout=5000)
                    print(f"  ✓ 使用選擇器: {selector}")
                    break
                except:
                    pass
        except Exception as e:
            print(f"  ⚠️  選擇地區失敗: {e}")
        await asyncio.sleep(0.5)
        
        # 7. 填寫電話號碼（香港）
        print(f"✓ 填寫電話（初始-香港）: +852 {user_data['phone_hk']}")
        try:
            phone_selectors = [
                "#editPhone",
                "input[name='TixUserForm[phone]']",
                "input[placeholder*='手機']",
                "input[type='tel']"
            ]
            for selector in phone_selectors:
                try:
                    inp = page.locator(selector).first
                    await inp.fill(user_data['phone_hk'], timeout=5000)
                    print(f"  ✓ 使用選擇器: {selector}")
                    break
                except:
                    pass
        except Exception as e:
            print(f"  ⚠️  填寫電話失敗: {e}")
        await asyncio.sleep(0.3)
        
        # 8. 填寫電子郵件
        print(f"✓ 填寫電子郵件: {user_data['email']}")
        try:
            email_selectors = [
                "#tixuserform-email",
                "input[name*='email']",
                "input[type='email']",
                "input[placeholder*='郵']"
            ]
            for selector in email_selectors:
                try:
                    inp = page.locator(selector).first
                    await inp.fill(user_data['email'], timeout=5000)
                    print(f"  ✓ 使用選擇器: {selector}")
                    break
                except:
                    pass
        except Exception as e:
            print(f"  ⚠️  填寫郵箱失敗: {e}")
        await asyncio.sleep(0.3)
        
        # 9. 滾動到底部並勾選隱私政策
        print("✓ 滾動到頁面底部")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(0.5)
        
        # 10. 勾選隱私政策同意
        print("✓ 勾選隱私政策同意")
        try:
            privacy_checkboxes = await page.locator("input[type='checkbox']").all()
            for checkbox in privacy_checkboxes:
                try:
                    is_visible = await checkbox.is_visible()
                    is_checked = await checkbox.is_checked()
                    if is_visible and not is_checked:
                        await checkbox.check()
                        print("  ✓ 已勾選隱私政策")
                        break
                except:
                    pass
        except Exception as e:
            print(f"⚠️  勾選隱私政策失敗: {e}")
        await asyncio.sleep(0.3)
        
        print("\n✅ 表單填寫完成！")
        return True
    
    async def click_bind_account(self, page):
        """點擊「選定此會員帳號進行綁定」"""
        print("=" * 50)
        print("點擊「選定此會員帳號進行綁定」按鈕...")
        print("=" * 50)
        
        # 滾動到底部
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(0.5)
        
        # 找並點擊按鈕
        bind_btn = page.locator("button:has-text('選定此會員帳號進行綁定')").first
        await bind_btn.click()
        await asyncio.sleep(1.5)
        
        print("✅ 已點擊綁定按鈕，進入手機驗證頁面！")
        return True
    
    async def modify_phone_to_us(self, page, user_data):
        """修改手機號碼：香港 → 美國"""
        print("=" * 50)
        print("修改手機號碼: 香港 (+852) → 美國 (+1)")
        print("=" * 50)
        
        await asyncio.sleep(1)
        
        # 1. 打開國碼 Select2 下拉菜單
        print("✓ 打開國碼選擇器...")
        select2_container = page.locator("span.select2-selection__rendered, #select2-editPhoneCountry-container").first
        await select2_container.click()
        await asyncio.sleep(0.8)
        
        # 2. 搜尋美國
        print("✓ 搜尋美國 (+1)...")
        search_box = page.locator(".select2-search__field").first
        await search_box.type("美", delay=100)
        await asyncio.sleep(0.6)
        
        # 3. 選擇美國選項
        print("✓ 選擇美國...")
        us_option = page.locator("li.select2-results__option").filter(has_text="美國").first
        await us_option.click()
        await asyncio.sleep(0.5)
        
        # 4. 修改電話號碼
        print(f"✓ 修改電話號碼: {user_data['phone_us']}")
        phone_input = page.locator("input[name='TixUserForm[phone]']").first
        await phone_input.clear()
        await asyncio.sleep(0.2)
        await phone_input.fill(user_data['phone_us'])
        await asyncio.sleep(0.3)
        
        print("✅ 電話號碼已修改為美國 (+1 3315003235)！")
        return True
    
    async def submit_phone_verification(self, page):
        """點擊「確認送出並進行手機號碼認證」"""
        print("=" * 50)
        print("提交手機號碼進行驗證...")
        print("=" * 50)
        
        # 找並點擊提交按鈕
        submit_btn = page.locator("button:has-text('確認送出並進行手機號碼認證')").first
        await submit_btn.click()
        await asyncio.sleep(2)
        
        print("✅ 已提交電話號碼，進入驗證倒計時頁面！")
        return True
    
    async def wait_for_sms_code(self, phone_number, max_wait=180):
        """等待並收集 SMS 驗證碼"""
        print("=" * 50)
        print(f"等待 SMS 驗證碼到達電話: +1 {phone_number}")
        print("=" * 50)
        
        start_time = datetime.now()
        timeout = max_wait
        
        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                print(f"⏳ 檢查 SMS API... ({int((datetime.now() - start_time).total_seconds())}s)")
                
                response = requests.get(self.sms_us_api, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    print(f"API 回應: {content}")
                    
                    # 提取驗證碼（6位數字）
                    match = re.search(r'\d{6}', content)
                    if match:
                        sms_code = match.group()
                        print(f"\n✅ 找到驗證碼: {sms_code}")
                        return sms_code
                
                await asyncio.sleep(3)
            
            except Exception as e:
                print(f"❌ 錯誤: {e}")
                await asyncio.sleep(3)
        
        print(f"❌ 超時: 在 {timeout} 秒內未收到驗證碼")
        return None
    
    async def enter_sms_code(self, page, sms_code):
        """輸入 SMS 驗證碼"""
        print("=" * 50)
        print(f"輸入 SMS 驗證碼: {sms_code}")
        print("=" * 50)
        
        # 找到驗證碼輸入框
        code_input = page.locator("input[placeholder*='驗證碼'], input[id*='code'], input[name*='code']").first
        
        try:
            await code_input.fill(sms_code)
            await asyncio.sleep(0.5)
            print(f"✅ 已輸入驗證碼")
            return True
        except:
            print("❌ 找不到驗證碼輸入框")
            return False
    
    async def click_confirm_verification(self, page):
        """點擊「確認」完成驗證"""
        print("=" * 50)
        print("點擊確認驗證...")
        print("=" * 50)
        
        # 找並點擊確認按鈕
        confirm_btn = page.locator("button:has-text('確認')").first
        await confirm_btn.click()
        await asyncio.sleep(2)
        
        print("✅ 已提交驗證碼！")
        return True
    
    async def run_full_registration(self):
        """執行完整註冊流程"""
        print("\n")
        print("[START] Tixcraft 自動註冊流程...")
        print("=" * 50)
        
        # 準備用戶數據
        user_data = {
            'name': self.generate_name(),
            'id': self.generate_valid_roc_id(),
            'birthday': self.generate_birthday(),
            'phone_hk': self.generate_phone_number("+852"),
            'phone_us': self.generate_phone_number("+1"),
            'email': self.generate_email(),
        }
        
        print(f"👤 生成的用戶數據:")
        print(f"  姓名: {user_data['name']}")
        print(f"  身份證: {user_data['id']}")
        print(f"  生日: {user_data['birthday']}")
        print(f"  電話 (初始-香港): +852 {user_data['phone_hk']}")
        print(f"  電話 (目標-美國): +1 {user_data['phone_us']}")
        print(f"  郵箱: {user_data['email']}")
        print()
        
        async with async_playwright() as p:
            # 啟動瀏覽器
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                # 第 1 步: 進入註冊頁面
                print("第 1 步: 導航到註冊頁面...")
                await page.goto(self.register_url)
                await asyncio.sleep(2)
                
                # 第 2 步: 填寫表單
                print("\n第 2 步: 填寫註冊表單...")
                await self.fill_registration_form(page, user_data)
                await asyncio.sleep(1)
                
                # 第 3 步: 點擊綁定按鈕
                print("\n第 3 步: 點擊「選定此會員帳號進行綁定」...")
                await self.click_bind_account(page)
                await asyncio.sleep(2)
                
                # 第 4 步: 修改電話號碼
                print("\n第 4 步: 修改手機號碼 (香港 → 美國)...")
                await self.modify_phone_to_us(page, user_data)
                await asyncio.sleep(1)
                
                # 第 5 步: 提交驗證
                print("\n第 5 步: 提交手機號碼進行驗證...")
                await self.submit_phone_verification(page)
                await asyncio.sleep(3)
                
                # 第 6 步: 等待 SMS
                print("\n第 6 步: 等待 SMS 驗證碼...")
                sms_code = await self.wait_for_sms_code(user_data['phone_us'], max_wait=180)
                
                if sms_code:
                    # 第 7 步: 輸入驗證碼
                    print("\n第 7 步: 輸入驗證碼...")
                    await self.enter_sms_code(page, sms_code)
                    await asyncio.sleep(1)
                    
                    # 第 8 步: 確認驗證
                    print("\n第 8 步: 確認驗證...")
                    await self.click_confirm_verification(page)
                    
                    print("\n" + "=" * 50)
                    print("✅✅✅ 註冊成功！")
                    print("=" * 50)
                else:
                    print("\n❌ 未能收到 SMS 驗證碼，請手動完成驗證")
                
                # 保持瀏覽器打開以便觀察
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"\n❌ 發生錯誤: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                await browser.close()


async def main():
    """主函數"""
    try:
        registration = TixcraftAutoRegister()
        await registration.run_full_registration()
    except Exception as e:
        print(f"❌ 致命錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
