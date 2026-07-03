#!/usr/bin/env python3
"""
Google Sheets OAuth 設置嚮導
自動生成認證並保存為 gspread_credentials.json
"""

import json
import os
import sys
import webbrowser
from pathlib import Path

def setup_oauth():
    """設置 Google OAuth"""
    
    print("=" * 60)
    print("Google Sheets 認證設置嚮導")
    print("=" * 60)
    
    print("""
本工具會幫助您設置 Google Sheets 存取權限。

步驟概述：
1. 打開 Google Cloud Console
2. 創建 OAuth 2.0 認證
3. 下載 credentials.json
4. 本程式會完成剩下的授權

""")
    
    response = input("是否要現在開始設置? (y/n): ").strip().lower()
    if response != 'y':
        print("取消設置")
        return False
    
    # 第1步：提示用戶前往 Google Cloud Console
    print("\n" + "=" * 60)
    print("第 1 步：前往 Google Cloud Console")
    print("=" * 60)
    print("""
請按以下步驟操作：

1. 點擊以下鏈結打開 Google Cloud Console：
   https://console.cloud.google.com
   
2. 如果沒有項目，點擊「建立項目」
   - 輸入項目名稱: "Tixcraft Registration"
   - 點擊「建立」

3. 在搜尋框搜尋 "Google Sheets API"
   - 點擊第一個結果
   - 點擊「啟用」

4. 點擊左邊「認證」→ 建立認證 → OAuth 用戶端 ID
   - 應用程式類型選「桌面應用」
   - 點擊「建立」

5. 點擊已建立的認證旁邊的「下載」按鈕
   - 儲存檔案為 credentials.json

6. 將 credentials.json 複製到本目錄
   """)
    
    # 提示打開 Console
    open_console = input("\n要現在打開 Google Cloud Console 嗎? (y/n): ").strip().lower()
    if open_console == 'y':
        webbrowser.open("https://console.cloud.google.com")
    
    # 第2步：確認 credentials.json 已放置
    print("\n" + "=" * 60)
    print("第 2 步：確認 credentials.json")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    credentials_path = project_root / "credentials.json"
    
    print(f"\n請確保 credentials.json 位於: {credentials_path}\n")
    
    max_attempts = 3
    for attempt in range(max_attempts):
        if credentials_path.exists():
            print(f"✓ 找到 credentials.json!")
            print(f"  位置: {credentials_path}")
            return True
        else:
            remaining = max_attempts - attempt - 1
            if remaining > 0:
                print(f"✗ 找不到 credentials.json")
                print(f"  還有 {remaining} 次嘗試機會...")
                input("請複製 credentials.json 到本目錄後，按 Enter 繼續...")
            else:
                print(f"✗ 無法找到 credentials.json")
                return False
    
    return False


if __name__ == "__main__":
    if setup_oauth():
        print("\n" + "=" * 60)
        print("✓ 設置完成!")
        print("=" * 60)
        print("\n現在您可以執行 GUI 應用程式了：")
        print("  python tixcraft_auto_register_gui.py")
    else:
        print("\n✗ 設置失敗")
        sys.exit(1)
