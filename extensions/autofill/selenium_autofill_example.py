"""
Selenium 自動結帳填表完整範例
展示如何在實際網頁上使用多帳號自動結帳填表擴充包
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 匯入擴充包
from extensions.autofill import manager
from extensions.autofill.selenium_filler import AutoFiller


def example_checkout_automation():
    """完整結帳自動化流程範例"""
    
    # ========== 初始設定 ==========
    driver = webdriver.Chrome()
    
    try:
        # 導航到結帳頁面
        driver.get("https://example.com/checkout")
        time.sleep(2)
        
        # ========== 第一步：組合資料 ==========
        print("\n🔄 步驟 1: 組合資料和信用卡")
        print("-" * 50)
        
        # 使用資料 A 和卡號 C 組合
        combined = manager.combine("A", "C")
        
        if not combined:
            print("❌ 資料組合失敗！")
            return
        
        manager.show_status()
        
        # ========== 第二步：自動填表 ==========
        print("🔄 步驟 2: 自動掃描並填表")
        print("-" * 50)
        
        # 等待表單加載
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
        )
        
        # 執行自動填表
        filler = AutoFiller(driver)
        filled_count = filler.fill_form(manager)
        
        # ========== 第三步：手動確認 ==========
        print("🔄 步驟 3: 等待手動確認")
        print("-" * 50)
        print("✅ 表單已自動填入完成！")
        print("🔴 請在瀏覽器中確認所有欄位內容無誤")
        print("🔴 然後手動點擊『送出』或『確認付款』按鈕\n")
        
        # 等待使用者手動操作
        input("⏳ 確認完成後按 Enter 鍵...\n")
        
        print("✅ 流程完成！")
        
    finally:
        # 關閉瀏覽器
        time.sleep(2)
        driver.quit()


def example_multiple_checkouts():
    """多帳號連續結帳範例"""
    
    # 定義要結帳的組合
    combinations = [
        ("A", "A"),  # 資料 A + 卡號 A
        ("B", "B"),  # 資料 B + 卡號 B
        ("C", "A"),  # 資料 C + 卡號 A
    ]
    
    driver = webdriver.Chrome()
    filler = AutoFiller(driver)
    
    try:
        for profile_id, card_id in combinations:
            print(f"\n{'='*50}")
            print(f"正在處理: 資料 {profile_id} + 卡號 {card_id}")
            print('='*50)
            
            # 組合資料
            manager.combine(profile_id, card_id)
            manager.show_status()
            
            # 導航到結帳頁面
            driver.get("https://example.com/checkout")
            time.sleep(2)
            
            # 自動填表
            filler.fill_form(manager)
            
            # 等待使用者確認
            print("🔴 請確認並手動送出此組帳號的訂單\n")
            input("✓ 完成後按 Enter 鍵...\n")
    
    finally:
        driver.quit()


def example_custom_data_workflow():
    """自訂資料工作流範例"""
    
    print("="*50)
    print("自訂資料工作流")
    print("="*50)
    
    # 列出現有資料
    print("\n1️⃣ 現有資料:")
    existing_profiles = manager.list_available_data()
    existing_cards = manager.list_available_cards()
    
    # 新增自訂資料
    print("\n2️⃣ 新增自訂資料:")
    manager.add_new_data(
        "CUSTOM1",
        name="自訂用戶",
        phone="0912345678",
        id_number="A123456789",
        email="custom@example.com"
    )
    
    manager.add_new_card(
        "CUSTOM1",
        card_number="4111111111111111",
        exp_month="12",
        exp_year="2025",
        cvv="123"
    )
    
    # 使用新增的自訂資料
    print("\n3️⃣ 使用自訂資料:")
    combined = manager.combine("CUSTOM1", "CUSTOM1")
    manager.show_status()
    
    # 刪除自訂資料
    print("4️⃣ 清理自訂資料:")
    manager.remove_data("CUSTOM1")
    manager.remove_card("CUSTOM1")


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║   多帳號自動結帳填表擴充包 - Selenium 範例  ║
    ╚════════════════════════════════════════════╝
    
    選擇要執行的範例:
    1. 單一結帳自動化 (example_checkout_automation)
    2. 多帳號連續結帳 (example_multiple_checkouts)
    3. 自訂資料工作流 (example_custom_data_workflow)
    """)
    
    # 預設執行自訂資料工作流
    example_custom_data_workflow()
