"""
使用範例 - 如何使用多帳號自動結帳填表擴充包
"""

# ========== 方式 1: 基本使用 ==========
# from extensions.autofill import manager

# # 列出所有可用的資料和卡號
# manager.list_available_data()   # 資料 A, B, C, ...
# manager.list_available_cards()  # 卡號 A, B, C, ...

# # 組合資料 A 和卡號 B（一次性載入）
# combined_data = manager.combine("A", "B")

# # 查看當前狀態
# manager.show_status()


# ========== 方式 2: 分開載入 ==========
# from extensions.autofill import manager

# manager.load_data("A")    # 載入個人資訊 A
# manager.load_card("B")    # 載入信用卡 B

# # 取得特定欄位的值
# name = manager.get_field_value("name")
# phone = manager.get_field_value("phone")
# card = manager.get_field_value("card")
# cvv = manager.get_field_value("cvv")


# ========== 方式 3: 新增自己的資料 ==========
# from extensions.autofill import manager

# # 新增個人資訊
# manager.add_new_data(
#     "D",
#     name="陳小姐",
#     phone="0956789012",
#     id_number="D123456789",
#     email="chen@example.com"
# )

# # 新增信用卡
# manager.add_new_card(
#     "D",
#     card_number="6011111111111117",
#     exp_month="06",
#     exp_year="2024",
#     cvv="123"
# )


# ========== 方式 4: 與 Selenium 整合（自動填表） ==========
# from selenium import webdriver
# from extensions.autofill import manager
# from extensions.autofill.selenium_filler import AutoFiller

# # 初始化瀏覽器
# driver = webdriver.Chrome()
# driver.get("https://example.com/checkout")

# # 組合資料和卡號
# manager.combine("A", "C")

# # 自動填表
# filler = AutoFiller(driver)
# filler.fill_form(manager)

# # 🔴 重要：由你手動確認並點擊「送出」按鈕
# input("請手動確認所有欄位無誤，然後按 Enter 送出...")


# ========== 方式 5: 刪除資料 ==========
# from extensions.autofill import manager

# manager.remove_data("D")  # 刪除個人資訊 D
# manager.remove_card("D")  # 刪除信用卡 D


print("✅ 使用範例已載入")
print("請參考 selenium_autofill_example.py 瞭解詳細使用方式")
