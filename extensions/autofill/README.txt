"""
多帳號自動結帳填表擴充包 - 快速開始指南

文件結構:
├── __init__.py                    # 擴充包初始化
├── data_profiles.py               # 個人資訊資料庫（可擴充）
├── payment_cards.py               # 信用卡資料庫（可擴充）
├── data_manager.py                # 核心管理器
├── selenium_filler.py             # Selenium 自動填表模組
├── USAGE_EXAMPLE.py               # 基本使用範例（註解版）
├── selenium_autofill_example.py   # 完整實戰範例
└── README.txt                     # 本文件

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【核心特性】

✅ 資料和卡號完全分開管理
✅ 可自由組合任意資料 + 任意卡號
✅ 支援無限擴充（新增自訂資料和卡號）
✅ Selenium 自動表單偵測和填表
✅ 自動標籤比對（中英文支援）
✅ 安全機制：填表完成後必須手動確認送出

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【快速開始】

1. 匯入管理器:
   from extensions.autofill import manager

2. 查看可用資料:
   manager.list_available_data()   # 資料 A, B, C
   manager.list_available_cards()  # 卡號 A, B, C

3. 組合資料和卡號:
   manager.combine("A", "B")  # 資料 A + 卡號 B

4. 檢查狀態:
   manager.show_status()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【與 Selenium 整合】

from extensions.autofill import manager
from extensions.autofill.selenium_filler import AutoFiller
from selenium import webdriver

# 初始化
driver = webdriver.Chrome()
driver.get("https://example.com/checkout")

# 組合資料
manager.combine("A", "C")

# 自動填表
filler = AutoFiller(driver)
filler.fill_form(manager)

# 🔴 手動確認並送出
input("確認完成後按 Enter...")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【新增自訂資料】

# 新增個人資訊
manager.add_new_data(
    "D",  # 資料 ID
    name="新增姓名",
    phone="0912345678",
    id_number="A123456789",
    email="email@example.com"
)

# 新增信用卡
manager.add_new_card(
    "D",  # 卡號 ID
    card_number="4111111111111111",
    exp_month="12",
    exp_year="2025",
    cvv="123"
)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【刪除資料】

# 刪除個人資訊
manager.remove_data("D")

# 刪除信用卡
manager.remove_card("D")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【支援的欄位類型偵測】

個人資訊欄位:
  ✓ name, 姓名, 聯絡人, 收件人, full name
  ✓ phone, 手機, 電話, mobile, cell, 聯絡電話
  ✓ id, 身分證, 證件號碼, id_number, 身分證字號
  ✓ email, 信箱, 電子郵件, mail, e-mail

信用卡欄位:
  ✓ card, 卡號, cardnumber, cc-number
  ✓ month, 月份, exp month, mm
  ✓ year, 年份, exp year, yyyy
  ✓ cvv, cvc, 安全碼, 驗證碼, security

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【重要安全說明】

🔴 本擴充包設計為「填表助手」，不會自動送出：
   1. 所有填表完成後保持靜態狀態
   2. 所有的最後確認必須由使用者手動操作
   3. 避免誤操作造成的重複訂單或錯誤支付

✅ 使用流程:
   1. 自動填表
   2. 確認欄位內容無誤
   3. 手動點擊「送出」按鈕

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【API 參考】

DataManager 方法:
  - combine(profile_id, card_id)      # 組合資料和卡號
  - load_data(profile_id)             # 載入個人資訊
  - load_card(card_id)                # 載入信用卡
  - get_combined()                    # 取得已組合的資料
  - get_field_value(field_type)       # 根據類型取得值
  - list_available_data()             # 列出所有可用資料
  - list_available_cards()            # 列出所有可用卡號
  - add_new_data(...)                 # 新增個人資訊
  - add_new_card(...)                 # 新增信用卡
  - remove_data(profile_id)           # 刪除個人資訊
  - remove_card(card_id)              # 刪除信用卡
  - show_status()                     # 顯示當前狀態

AutoFiller 方法:
  - fill_form(manager)                # 自動掃描表單並填表
  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【常見問題】

Q: 如何新增第四組資料?
A: manager.add_new_data("D", name="...", phone="...", ...)

Q: 可以混搭不同組合嗎?
A: 可以！combine("A", "B") 表示資料A + 卡號B

Q: 為什麼不自動送出?
A: 為了安全性，防止誤操作。最後確認必須由你手動操作。

Q: 支援多幣別/多國家的卡號嗎?
A: 支援！只需在 payment_cards.py 中新增即可

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# 當此檔案被執行時，顯示幫助資訊
if __name__ == "__main__":
    import sys
    print(__doc__)
    print("\n💡 提示: 請查看 USAGE_EXAMPLE.py 和 selenium_autofill_example.py 瞭解詳細用法")
