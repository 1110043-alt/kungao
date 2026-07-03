"""
Google Sheets 快速設置工具
幫助您快速建立並獲取 Google Sheets URL
"""

import webbrowser
import time
import sys

def main():
    print("=" * 60)
    print("  Google Sheets 快速設置工具")
    print("=" * 60)
    print()
    
    print("🔗 快速步驟：")
    print()
    print("1️⃣  打開 Google Sheets 首頁...")
    print()
    
    # 打開 Google Sheets 建立新試算表的頁面
    url = "https://sheets.google.com/create"
    webbrowser.open(url)
    
    time.sleep(2)
    
    print("2️⃣  請在瀏覽器中：")
    print("   ✓ 用您的 Google 帳戶登入")
    print("   ✓ 輸入試算表名稱（例如：Tixcraft 註冊記錄）")
    print("   ✓ 點擊「建立」")
    print()
    
    input("⏳ 按 Enter 繼續...")
    print()
    
    print("3️⃣  現在試算表已建立，複製 URL：")
    print()
    print("   方法 A - 從位址欄複製：")
    print("   ✓ 看著瀏覽器的位址欄")
    print("   ✓ 應該看起來像：https://docs.google.com/spreadsheets/d/[ID]/edit")
    print("   ✓ 按 Ctrl+L 選中整個 URL")
    print("   ✓ 按 Ctrl+C 複製")
    print()
    print("   方法 B - 從分享連結複製：")
    print("   ✓ 點擊右上「分享」")
    print("   ✓ 確保設定為「所有知道連結的人 - 編輯者」")
    print("   ✓ 點擊「複製連結」")
    print()
    
    url_input = input("📋 請貼上您複製的 Google Sheets URL: ").strip()
    
    if not url_input:
        print("❌ 您沒有輸入 URL")
        return
    
    # 驗證 URL 格式
    if "docs.google.com/spreadsheets" not in url_input:
        print("❌ URL 格式不正確")
        return
    
    # 提取 ID
    try:
        id_start = url_input.find("/d/") + 3
        id_end = url_input.find("/", id_start)
        sheet_id = url_input[id_start:id_end]
        
        print()
        print("=" * 60)
        print("✅ Google Sheets 已設置！")
        print("=" * 60)
        print()
        print("📌 您的 Google Sheets 資訊：")
        print()
        print(f"  URL: {url_input}")
        print()
        print(f"  ID: {sheet_id}")
        print()
        print("=" * 60)
        print()
        print("📌 現在請在 GUI 應用中：")
        print("  1. 在「Google Sheets URL」欄位貼上上方的 URL")
        print("  2. 點擊「認證」按鈕")
        print("  3. 在彈出的瀏覽器窗口中登入您的 Google 帳戶")
        print("  4. 授權應用程序訪問您的 Google Drive")
        print()
        print("就完成了！✨")
        
    except Exception as e:
        print(f"❌ 解析 URL 失敗: {e}")

if __name__ == "__main__":
    main()
