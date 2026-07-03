# Tixcraft 自動註冊系統完整指南

## 📋 系統流程概述

```
開始
  ↓
啟動 PyQt5 GUI 窗口
  ↓
輸入 Google 帳號 + 密碼 + 電話 + 名字
  ↓
點擊「開始註冊」按鈕
  ↓
打開無頭 Chromium 瀏覽器（隱藏 WebDriver 特徵）
  ↓
[第1步] Google 登入 (120秒超時)
  ├─ 自動找 Google 按鈕
  ├─ 自動輸入帳號 (逐字輸入，延遲 100ms)
  ├─ 點擊「下一步」or 按 Enter (間隔 1 秒)
  ├─ 等待密碼頁面加載 (4 秒)
  ├─ 自動輸入密碼 (逐字輸入，延遲 100ms)
  ├─ 點擊「下一步」or 按 Enter (間隔 1 秒)
  ├─ 等待返回 Tixcraft (120秒超時，每2秒檢查一次)
  └─ ✓ 返回 Tixcraft 即為登入成功
  ↓
[第2步] 導航到表單
  ├─ 訪問 https://tixcraft.com/user/register
  ├─ 等待頁面完全加載 (3 秒)
  └─ 等待網絡空閒 (15 秒超時)
  ↓
[第3步] 填寫表單 (_fill_form)
  ├─ 國籍: 自動選「中華民國」(1.5-2.5秒隨機延遲)
  ├─ 性別: 隨機選男或女 (1.5-2.5秒隨機延遲)
  ├─ 姓名: 逐字輸入 (1.5-2.5秒隨機延遲)
  ├─ 身分證: 逐字輸入 (1.5-2.5秒隨機延遲)
  ├─ 生日: 輸入 YYYY/MM/DD (1.5-2.5秒隨機延遲)
  ├─ 國碼+電話: 選 +1，輸入電話 (1.5-2.5秒隨機延遲)
  └─ 等待 1 秒
  ↓
[第4步] 自動填寫所有必填欄位 (_fill_required_fields)
  ├─ 掃描所有帶「*」標記的欄位
  ├─ 國籍: 選「中華民國」
  ├─ 性別: 隨機選男或女
  ├─ 電話: 使用設定值
  ├─ 地址: 城市 → 區 → 街道號碼 (各間隔 0.5-2.5 秒)
  ├─ 郵遞區號: 隨機 5 位數字
  ├─ 電子郵件: 使用你的 Google 帳號 ✨
  └─ 其他欄位: 隨機數據
  ↓
[第5步] 表單完成
  ├─ 保持瀏覽器打開 300 秒 (5 分鐘)
  ├─ 用戶手動：驗證欄位、輸入驗證碼、點擊提交
  └─ 300 秒後自動關閉瀏覽器
```

---

## ⏱️ 延遲間隔詳細表

### Google 登入階段

| 步驟 | 操作 | 延遲時間 | 目的 |
|------|------|---------|------|
| 1 | 帳號輸入完成後 | 1秒 | 確保帳號已輸入 |
| 2 | 帳號頁面加載完成 | 2秒 | 確保「下一步」按鈕可點擊 |
| 3 | 帳號頁面到密碼頁面 | 4秒 | 等待密碼欄位加載 |
| 4 | 密碼頁面加載完成 | 2秒 | 確保密碼欄位可交互 |
| 5 | 密碼輸入完成後 | 1秒 | 確保密碼已輸入 |
| 6 | 返回 Tixcraft 檢查 | 每2秒檢查一次 | 監測登入進度 |

**重要延遲邏輯：**
```python
# 帳號提交後等待密碼頁面
await asyncio.sleep(4)  # ← 關鍵！避免密碼欄位未加載

# 密碼提交後等待返回 Tixcraft
while (datetime.now() - start_time).total_seconds() < 120:
    if "tixcraft.com" in current_url:
        break  # ✓ 檢測到返回 Tixcraft
    await asyncio.sleep(2)  # ← 每 2 秒檢查一次
```

---

### 表單填寫階段

#### 第一次填寫 (_fill_form)
```python
# 填寫 7 個主要欄位的延遲

隨機延遲 = random.uniform(1.5, 2.5)  # 1.5-2.5 秒

每個欄位流程：
1. 點擊欄位
2. 清空（如果有舊內容）
3. 等待 0.2 秒
4. 輸入新資料
5. 等待 隨機延遲(1.5-2.5秒)
6. 下一個欄位
```

**代碼示例：**
```python
await field.click(timeout=1000)
await asyncio.sleep(0.2)
await field.fill(value, timeout=2000)
await asyncio.sleep(random.uniform(1.5, 2.5))  # ← 隨機延遲
```

#### 第二次填寫 (_fill_required_fields)
```python
# 自動掃描並填寫所有必填欄位（帶「*」標記）

for each required_field:
    1. 根據標籤判斷欄位類型
    2. 相應的延遲：
       - 下拉選單: 點擊後 0.5 秒，選項後 1.5-2.5 秒
       - 文本欄位: 點擊後 0.2 秒，輸入後 1.5-2.5 秒
       - 單選按鈕: 直接點擊後 0.3 秒
    3. 進行到下一個欄位
```

---

## 📝 關鍵代碼段落

### 1️⃣ 帳號輸入與提交
```python
# 找帳號欄位
await email_field.click(timeout=2000)
await asyncio.sleep(0.5)
await email_field.fill("", timeout=2000)
await asyncio.sleep(0.3)

# 逐字輸入（每字符 100ms 延遲）
await email_field.type(google_email, delay=100)
self.progress.emit("[Google SSO] ✓ 帳號輸入成功")

# 等待確保輸入完成
await asyncio.sleep(1)  # ← 關鍵延遲

# 點擊下一步或按 Enter
await next_button.click()
```

### 2️⃣ 密碼提交後等待
```python
# 輸入密碼
await password_field.type(google_password, delay=100)

# 點擊下一步
await password_button.click()

# 等待密碼頁面處理
await asyncio.sleep(3)  # ← 重要！給 Google 時間驗證密碼

# 然後開始檢查是否返回 Tixcraft (最多 120 秒)
```

### 3️⃣ 表單欄位填寫
```python
# 對於每個需要填寫的欄位

# 點擊
await field.click(timeout=1000)
await asyncio.sleep(0.2)  # 短暫延遲確保欄位獲得焦點

# 輸入
await field.fill(value, timeout=2000)

# 隨機延遲（模擬真人操作）
delay = random.uniform(1.5, 2.5)
await asyncio.sleep(delay)
```

### 4️⃣ 地址選擇（特殊邏輯）
```python
# 地址是兩層下拉選單

# 第 1 層：選擇城市
await city_dropdown.click()
await asyncio.sleep(0.5)
await city_option.click()  # 選城市
await asyncio.sleep(1.5)  # ← 等待第 2 層加載

# 第 2 層：選擇區
await district_dropdown.click()
await asyncio.sleep(0.5)
await district_option.click()  # 選區
await asyncio.sleep(1.5)  # ← 等待欄位更新

# 第 3 層：輸入詳細地址（XX路YY號）
await address_field.fill("中山路123號")
await asyncio.sleep(1.5)
```

---

## 🔍 步驟驗證邏輯

### Google 登入驗證
```python
# ✓ 驗證成功: 檢測 URL 是否返回 tixcraft.com
start_time = datetime.now()
while (datetime.now() - start_time).total_seconds() < 120:
    current_url = page.url
    if "tixcraft.com" in current_url and "google" not in current_url.lower():
        self.progress.emit("[登錄] ✓ 已返回 Tixcraft，登錄成功")
        break
    await asyncio.sleep(2)  # 每 2 秒檢查一次
```

### 頁面加載驗證
```python
# ✓ 驗證頁面完全加載
try:
    await page.wait_for_load_state("networkidle", timeout=15000)
    self.progress.emit("[表單] ✓ 表單頁面已完全加載")
except:
    self.progress.emit("[表單] ⚠ 頁面加載超時，繼續...")
```

### 欄位填寫驗證
```python
# ✓ 驗證欄位值是否正確
try:
    filled_value = await field.input_value()
    if filled_value == expected_value:
        self.progress.emit(f"[必填] ✓ 已填寫 {field_label} = {filled_value}")
        filled_count += 1
    else:
        self.progress.emit(f"[必填] ⚠ 填寫值不符: {filled_value}")
except Exception as e:
    self.progress.emit(f"[必填] ⚠ 欄位填寫失敗: {str(e)}")
```

---

## 🚨 錯誤處理

### 如果 Google 登入失敗
```
→ 顯示「等待手動登錄 (120 秒)」
→ 給用戶 120 秒手動輸入
→ 120 秒後檢查是否返回 Tixcraft
→ 如果仍未返回 → 結束程式
```

### 如果表單頁面加載失敗
```
→ 使用 asyncio.wait_for(..., timeout=20)
→ 如果超時，仍然繼續（不中止）
→ 嘗試填寫欄位
→ 如果欄位找不到 → 跳過該欄位
```

### 如果欄位填寫失敗
```
→ 記錄警告訊息
→ 跳過該欄位
→ 繼續下一個欄位
```

---

## 📊 完整延遲時間軸

```
[0秒] 點擊「開始註冊」
  ↓
[瞬間] 打開瀏覽器
  ↓
[1-2秒] 導航到 Tixcraft 首頁
  ↓
[2-3秒] 找 Google 按鈕並點擊
  ↓
[3-5秒] 導航到 Google 登入頁面
  ↓
[5-7秒] 頁面加載，輸入帳號
  ↓
[7-8秒] 點擊「下一步」(1秒延遲)
  ↓
[8-12秒] 等待密碼頁面 (4秒延遲)
  ↓
[12-14秒] 輸入密碼
  ↓
[14-15秒] 點擊「下一步」(1秒延遲)
  ↓
[15-18秒] 等待驗證 (3秒延遲)
  ↓
[18-138秒] 檢查是否返回 Tixcraft (120秒超時，每2秒檢查)
  ↓
[138-141秒] 導航到表單頁面
  ↓
[141-149秒] 填寫 7 個主要欄位
             (每個欄位 1.5-2.5秒延遲)
  ↓
[149-299秒] 自動填寫其他必填欄位
  ↓
[299-599秒] 保持瀏覽器打開 (300秒 = 5分鐘)
             用戶手動完成驗證碼、提交等
  ↓
[599秒] 自動關閉瀏覽器並結束
```

---

## ✨ 新增改進 - 電子郵件欄位

**改動內容：** 電子郵件欄位現在使用你提供的 Google 帳號，而不是生成隨機郵件

```python
# 舊版本（錯誤）
email = self.generator.generate_email()  # ❌ 生成 user12345@gmail.com

# 新版本（正確）
email = self.config.get("google_email", "")  # ✅ 使用你的 Google 帳號
```

---

## 🎯 最佳實踐

### ✅ DO (應該做)
- 使用隨機延遲 (1.5-2.5秒) 模擬真人操作
- 在每個步驟完成後等待 (不要連續點擊)
- 檢查 URL 和頁面加載狀態確認進度
- 使用多種選擇器尋找元素 (備選方案)
- 提供清晰的進度訊息給用戶

### ❌ DON'T (不應該做)
- 使用固定延遲 (容易觸發反爬蟲)
- 不等待頁面加載就操作元素
- 忽視超時異常 (應該有降級方案)
- 在同一個欄位重複點擊
- 快速連續提交多個表單

---

## 📱 GUI 使用步驟

### 1. 啟動應用
```bash
python tixcraft_gui_v2.py
```

### 2. 輸入資訊
- **Google 帳號**: 你的 Gmail 地址
- **Google 密碼**: 你的 Gmail 密碼
- **電話號碼**: 台灣格式 (09xxxxxxxx)
- **姓名**: 名字 (可留空自動生成)
- **註冊數量**: 要註冊多少個帳號

### 3. 點擊「開始註冊」
- 程式自動執行所有操作
- 監看左側「進度」面板了解進展
- 如果卡在 Google 登入，可手動操作

### 4. 手動完成
- 表單自動填寫後，瀏覽器保持打開
- 手動輸入驗證碼 (如需要)
- 手動點擊「提交」按鈕
- 完成註冊！

---

## 🔧 設定檔 (gui_config.json)

```json
{
  "google_email": "你的Gmail@gmail.com",
  "google_password": "你的密碼",
  "phone": "09xxxxxxxx",
  "name": "你的名字",
  "country_code": "+1",
  "count": 1
}
```

所有設定會自動保存，下次啟動時會自動載入。

---

## 📞 常見問題

### Q: Google 登入一直失敗？
**A:** 檢查：
1. 帳號/密碼是否正確
2. 是否開啟了 2FA (雙重認證)
3. 帳號是否被鎖定
4. 給予足夠的手動登入時間 (120秒)

### Q: 表單欄位沒有填寫？
**A:** 可能原因：
1. 網站更新了 HTML 結構
2. 頁面加載未完成
3. 欄位選擇器已過期

解決：通知開發者更新選擇器。

### Q: 如何加快速度？
**A:** 
1. 減少延遲時間（但可能觸發反爬蟲）
2. 增加「註冊數量」以批量處理
3. 使用更快的網路連接

### Q: 可以填寫多個帳號嗎？
**A:** 不行。目前系統一次只能填一個。迴圈功能等待開發。

---

## 📦 檔案結構

```
tixcraft_gui_v2.py          # 主 GUI 應用
gui_config.json             # 設定檔
啟動Tixcraft自動註冊.bat     # 快速啟動按鈕
TIXCRAFT_AUTOMATION_GUIDE.md # 本文件 ✓
```

---

**最後更新**: 2026-06-29  
**版本**: 2.0 (改進電子郵件欄位，優化流程控制)
