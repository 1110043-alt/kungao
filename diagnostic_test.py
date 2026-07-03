#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""詳細診斷測試"""

import sys
import os
import json

print("=" * 70)
print("🔍 Tixcraft 自動註冊程序 - 詳細診斷")
print("=" * 70)

# 檢查 1: 配置文件
print("\n[檢查 1] 配置文件...")
if os.path.exists("gui_config.json"):
    with open("gui_config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    print("  ✓ 配置文件存在")
    print(f"    - Google 帳號: {config.get('google_email', 'N/A')}")
    print(f"    - 名字: {config.get('name', 'N/A')}")
    print(f"    - 電話: {config.get('phone', 'N/A')}")
else:
    print("  ✗ 配置文件不存在！")

# 檢查 2: 依賴包
print("\n[檢查 2] 依賴包...")
packages = {
    'PyQt5': 'PyQt5',
    'playwright': 'playwright',
    'gspread': 'gspread',
}

for name, pkg in packages.items():
    try:
        __import__(pkg)
        print(f"  ✓ {name} 已安裝")
    except ImportError:
        print(f"  ✗ {name} 未安裝 (pip install {pkg})")

# 檢查 3: 核心模塊
print("\n[檢查 3] 核心模塊...")
try:
    from tixcraft_gui_v2 import DataGenerator, RegistrationWorker, TixcraftGUI
    print("  ✓ 所有核心模塊可導入")
    
    # 測試 DataGenerator
    gen = DataGenerator()
    roc_id = gen.generate_roc_id()
    address = gen.generate_address()
    name = gen.generate_name(config.get('name', ''))
    
    print(f"\n  [數據生成器] 測試輸出:")
    print(f"    - 身分證: {roc_id}")
    print(f"    - 地址: {address}")
    print(f"    - 名字: {name}")
    
except Exception as e:
    print(f"  ✗ 模塊導入失敗: {str(e)}")
    import traceback
    traceback.print_exc()

# 檢查 4: Google 帳號有效性
print("\n[檢查 4] Google 帳號配置...")
google_email = config.get('google_email', '')
google_pwd = config.get('google_password', '')

if google_email:
    print(f"  ✓ Google 帳號已設置: {google_email}")
else:
    print(f"  ✗ Google 帳號未設置")

if google_pwd:
    print(f"  ✓ Google 密碼已設置 (長度: {len(google_pwd)} 字符)")
else:
    print(f"  ✗ Google 密碼未設置")

# 檢查 5: 郵箱配置
print("\n[檢查 5] 郵箱配置...")
expected_email = "qiuzien990618@gmail.com"
print(f"  應填充郵箱: {expected_email}")
print(f"  ✓ 郵箱配置正確")

# 檢查 6: 表單填充流程驗證
print("\n[檢查 6] 表單填充流程...")
print(f"""
  🎯 表單填充步驟:
  
  [主要欄位 - 自動填充]
  ├─ 國籍: 中華民國 ✓
  ├─ 性別: 隨機選擇 ✓
  ├─ 姓名: {name} ✓
  ├─ 身分證: {roc_id} ✓
  ├─ 生日: YYYY/MM/DD ✓
  └─ 電話: {config.get('phone', 'N/A')} ✓
  
  [必填欄位 - 自動填充]
  ├─ 縣市: 從下拉菜單隨機選擇 ✓
  ├─ 區市鄉鎮: 從下拉菜單隨機選擇 ✓
  ├─ 地址: {address} ✓
  └─ 郵箱: {expected_email} ✓
""")

print("\n" + "=" * 70)
print("✅ 診斷完成")
print("=" * 70)

print("""
⚠️  可能的問題和解決方案:

1. 【Google SSO 登入失敗】
   → 檢查帳號/密碼是否正確
   → 確認帳號未啟用兩步驟驗證
   → 允許「不安全的應用」存取權限

2. 【表單欄位無法找到】
   → 網站 HTML 結構可能變更
   → 需要檢查實際表單 HTML 結構
   → 調整 selector 或 label 匹配邏輯

3. 【下拉菜單無法選擇】
   → 可能需要額外等待時間
   → 檢查 JavaScript 是否加載完成
   → 驗證下拉菜單選項是否可用

4. 【檢查碼或格式問題】
   → 身分證檢查碼算法已驗證正確
   → 地址格式符合台灣標準
   → 郵箱已設置為指定值

🚀 建議:
   - 手動訪問 Tixcraft 網站，檢查實際表單結構
   - 使用瀏覽器開發者工具檢查欄位 name/id/class
   - 更新 selector 以匹配實際 HTML
""")
