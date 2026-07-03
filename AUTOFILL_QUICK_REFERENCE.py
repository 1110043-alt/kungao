"""
多帳號自動結帳填表擴充包 - 快速參考卡

╔════════════════════════════════════════════════════════════════╗
║               擴充包目錄結構                                     ║
╚════════════════════════════════════════════════════════════════╝

extensions/
└── autofill/
    ├── __init__.py                    # 擴充包入點
    ├── data_profiles.py               # 📋 個人資訊資料庫
    ├── payment_cards.py               # 💳 信用卡資料庫
    ├── data_manager.py                # 🎮 核心管理器
    ├── selenium_filler.py             # 🤖 Selenium 自動填表
    ├── USAGE_EXAMPLE.py               # 📖 基本使用範例
    ├── selenium_autofill_example.py   # 🚀 完整實戰範例
    └── README.txt                     # ❓ 詳細文檔

test_autofill_extension.py            # ✅ 測試腳本

════════════════════════════════════════════════════════════════

【使用方式一】最簡單快速

    from extensions.autofill import manager
    
    # 組合任意資料 + 任意卡號
    manager.combine("A", "B")
    
    # 取得填表值
    name = manager.get_field_value("name")
    card = manager.get_field_value("card")

════════════════════════════════════════════════════════════════

【使用方式二】與 Selenium 自動填表

    from extensions.autofill import manager
    from extensions.autofill.selenium_filler import AutoFiller
    from selenium import webdriver
    
    driver = webdriver.Chrome()
    driver.get("https://example.com/checkout")
    
    manager.combine("A", "B")
    filler = AutoFiller(driver)
    filler.fill_form(manager)
    
    # 🔴 由你手動確認並送出

════════════════════════════════════════════════════════════════

【內建預設資料】

資料組 (data_profiles.py):
  A: 王小明 | 0912345678 | A123456789 | wang@example.com
  B: 李美琪 | 0987654321 | B987654321 | li@example.com
  C: 張大衛 | 0956789012 | C456789012 | chang@example.com

卡號組 (payment_cards.py):
  A: 4111111111111111 | 12/2025 | CVV: 123
  B: 5555555555554444 | 08/2026 | CVV: 456
  C: 378282246310005  | 03/2027 | CVV: 789

════════════════════════════════════════════════════════════════

【常用指令】

# 查看所有可用資料
manager.list_available_data()     → ['A', 'B', 'C']
manager.list_available_cards()    → ['A', 'B', 'C']

# 組合資料
manager.combine("A", "B")         → 資料 A + 卡號 B

# 新增自訂資料
manager.add_new_data("D", name="...", phone="...", id_number="...", email="...")
manager.add_new_card("D", card_number="...", exp_month="...", exp_year="...", cvv="...")

# 刪除資料
manager.remove_data("D")
manager.remove_card("D")

# 查看狀態
manager.show_status()

════════════════════════════════════════════════════════════════

【支援的欄位自動偵測】

✅ 姓名: name, 姓名, 聯絡人, 收件人, fullname
✅ 手機: phone, 手機, 電話, mobile, cell, 聯絡電話
✅ 身分證: id, 身分證, 證件號碼, id_number, 身分證字號
✅ Email: email, 信箱, 電子郵件, mail, e-mail
✅ 卡號: card, 卡號, cardnumber, cc-number
✅ 月份: month, 月份, exp-month, mm
✅ 年份: year, 年份, exp-year, yyyy, yy
✅ CVV: cvv, cvc, 安全碼, 驗證碼, security

════════════════════════════════════════════════════════════════

【核心特性】

✓ 資料和卡號完全獨立管理
✓ 自由組合任意資料 + 任意卡號
✓ 支援無限擴充新增資料
✓ 自動表單欄位偵測（中英文支援）
✓ Selenium 完全整合
✓ 🔴 安全機制：填完後需手動確認送出

════════════════════════════════════════════════════════════════

【快速實戰】

第一步：測試擴充包
  $ python test_autofill_extension.py

第二步：查看範例
  - 簡單範例: extensions/autofill/USAGE_EXAMPLE.py
  - 完整範例: extensions/autofill/selenium_autofill_example.py

第三步：整合到你的指令碼
  from extensions.autofill import manager
  manager.combine("A", "B")
  ...

════════════════════════════════════════════════════════════════

【重要提醒】

🔴 所有填表完成後保持靜態
🔴 最後確認必須由你手動操作
🔴 絕對不會自動點擊「送出」或「確認付款」

════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(__doc__)
