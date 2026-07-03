#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""表單結構診斷工具 - 導出實際 HTML 結構用於調試"""

import asyncio
import json
from playwright.async_api import async_playwright

async def diagnose_form_structure():
    """診斷表單結構並導出 HTML"""
    
    print("=" * 80)
    print("🔧 Tixcraft 表單結構診斷工具")
    print("=" * 80)
    
    # Google 帳號（從 gui_config.json 讀取）
    try:
        with open('gui_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        print("❌ 找不到 gui_config.json")
        return
    
    google_email = config.get('google_email', '')
    google_password = config.get('google_password', '')
    
    if not google_email or not google_password:
        print("❌ Google 帳號或密碼未設置")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 隱藏 WebDriver
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
        """)
        
        try:
            print("\n[1/5] 訪問 Tixcraft...")
            await page.goto("https://tixcraft.com", timeout=30000)
            await asyncio.sleep(3)
            
            print("[2/5] 點擊 Google SSO 按鈕...")
            # 尋找 Google 登入按鈕
            google_buttons = await page.locator("button:has-text('Google'), a:has-text('Google')").all()
            if google_buttons:
                await google_buttons[0].click(timeout=5000)
                await asyncio.sleep(2)
            
            print("[3/5] 輸入 Google 帳號...")
            await page.fill("input[type='email']", google_email)
            await page.press("input[type='email']", "Enter")
            await asyncio.sleep(2)
            
            print("[4/5] 輸入 Google 密碼...")
            await page.fill("input[type='password']", google_password)
            await page.press("input[type='password']", "Enter")
            await asyncio.sleep(5)
            
            print("[5/5] 等待重定向...")
            await page.wait_for_load_state("networkidle", timeout=10000)
            await asyncio.sleep(3)
            
            # 尋找註冊表單
            print("\n🔍 掃描註冊表單...")
            
            # 向下滾動以確保所有內容可見
            print("   → 向下滾動頁面...")
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            await page.evaluate("window.scrollTo(0, 0)")  # 回到頂部
            await asyncio.sleep(1)
            
            # 檢查 iframe
            print("   → 檢查 iframe...")
            iframes = await page.locator("iframe").all()
            print(f"   → 找到 {len(iframes)} 個 iframe")
            
            # 獲取所有表單字段信息
            print("\n📋 表單字段詳細列表：\n")
            
            fields_info = []
            
            # 掃描所有 input
            inputs = await page.locator("input").all()
            print(f"[INPUT 字段] 找到 {len(inputs)} 個\n")
            for idx, inp in enumerate(inputs[:30], 1):
                try:
                    inp_type = await inp.get_attribute("type")
                    inp_name = await inp.get_attribute("name")
                    inp_id = await inp.get_attribute("id")
                    inp_placeholder = await inp.get_attribute("placeholder")
                    inp_class = await inp.get_attribute("class")
                    
                    # 找相關的 label
                    label_text = ""
                    if inp_id:
                        try:
                            label = await page.locator(f"label[for='{inp_id}']").text_content()
                            label_text = label.strip() if label else ""
                        except:
                            pass
                    
                    # 父元素文本
                    parent_text = ""
                    try:
                        parent_text = await inp.evaluate("el => el.parentElement.textContent").strip()
                        parent_text = parent_text[:80]  # 限制長度
                    except:
                        pass
                    
                    visible = await inp.is_visible(timeout=300) if inp else False
                    
                    info = {
                        'tag': 'input',
                        'type': inp_type,
                        'name': inp_name,
                        'id': inp_id,
                        'placeholder': inp_placeholder,
                        'label': label_text,
                        'visible': visible,
                        'parent_text': parent_text
                    }
                    fields_info.append(info)
                    
                    # 輸出關鍵信息
                    if label_text or inp_placeholder or inp_name:
                        vis_icon = "✓" if visible else "✗"
                        print(f"  [{idx:2d}] {vis_icon} type={inp_type:8s} | label={label_text:15s} | name={inp_name}")
                        if inp_placeholder:
                            print(f"       placeholder: {inp_placeholder}")
                        if not visible:
                            print(f"       ⚠️  不可見")
                except Exception as e:
                    pass
            
            # 掃描所有 select
            selects = await page.locator("select").all()
            print(f"\n[SELECT 字段] 找到 {len(selects)} 個\n")
            for idx, sel in enumerate(selects[:15], 1):
                try:
                    sel_name = await sel.get_attribute("name")
                    sel_id = await sel.get_attribute("id")
                    
                    label_text = ""
                    if sel_id:
                        try:
                            label = await page.locator(f"label[for='{sel_id}']").text_content()
                            label_text = label.strip() if label else ""
                        except:
                            pass
                    
                    options = await sel.locator("option").all()
                    visible = await sel.is_visible(timeout=300) if sel else False
                    
                    vis_icon = "✓" if visible else "✗"
                    print(f"  [{idx:2d}] {vis_icon} label={label_text:15s} | name={sel_name} | options={len(options)}")
                    
                    if not visible:
                        print(f"       ⚠️  不可見")
                except Exception as e:
                    pass
            
            # 掃描所有 textarea
            textareas = await page.locator("textarea").all()
            print(f"\n[TEXTAREA 字段] 找到 {len(textareas)} 個\n")
            for idx, ta in enumerate(textareas[:10], 1):
                try:
                    ta_name = await ta.get_attribute("name")
                    ta_id = await ta.get_attribute("id")
                    ta_placeholder = await ta.get_attribute("placeholder")
                    
                    label_text = ""
                    if ta_id:
                        try:
                            label = await page.locator(f"label[for='{ta_id}']").text_content()
                            label_text = label.strip() if label else ""
                        except:
                            pass
                    
                    visible = await ta.is_visible(timeout=300) if ta else False
                    
                    vis_icon = "✓" if visible else "✗"
                    print(f"  [{idx:2d}] {vis_icon} label={label_text:15s} | name={ta_name} | placeholder={ta_placeholder}")
                    
                    if not visible:
                        print(f"       ⚠️  不可見")
                except Exception as e:
                    pass
            
            # 導出完整 HTML 結構到文件
            print("\n💾 導出 HTML 結構到文件...")
            html_content = await page.content()
            
            with open("form_structure.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("   ✓ 已保存到: form_structure.html")
            
            # 導出字段信息到 JSON
            with open("form_fields.json", "w", encoding="utf-8") as f:
                json.dump(fields_info, f, ensure_ascii=False, indent=2)
            print("   ✓ 已保存到: form_fields.json")
            
            # 列出所有帶 * 的標籤（必填欄位）
            print("\n⭐ 必填欄位（帶 * 的標籤）:\n")
            labels = await page.locator("label").all()
            required_count = 0
            for label in labels:
                text = await label.text_content()
                if text and '*' in text:
                    required_count += 1
                    print(f"  • {text.strip()}")
            
            print(f"\n總共 {required_count} 個必填欄位")
            
            print("\n" + "=" * 80)
            print("✅ 診斷完成")
            print("=" * 80)
            print("""
📌 下一步:
   1. 打開 form_structure.html 查看完整頁面結構
   2. 查看 form_fields.json 查看所有字段詳情
   3. 搜索「收件地址」和「電子郵件」找到它們的 name/id
   4. 檢查為什麼它們被標記為不可見
   5. 告訴我找到的 name/id，我會針對性地修復
""")
            
        except Exception as e:
            import traceback
            print(f"❌ 錯誤: {str(e)}")
            print(traceback.format_exc())
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(diagnose_form_structure())
