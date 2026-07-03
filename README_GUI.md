# Tixcraft 自動註冊工具 使用指南

## 功能特性
✅ **自動填寫註冊表單** - 包括姓名、身份證、生日、電話、郵箱等  
✅ **支持名字自訂或隨機** - 可指定名字或自動隨機生成  
✅ **靈活的電話設定** - 支持更改國碼和電話號碼  
✅ **自動收集 SMS 驗證碼** - 通過 API 收集驗證碼  
✅ **Google Sheets 集成** - 自動將註冊信息導入試算表  
✅ **批量註冊** - 一次性註冊多個帳號  
✅ **完整的操作日誌** - 記錄每個註冊流程  

---

## 快速開始

### 方式 1: 直接運行 Python（推薦首先嘗試）

```bash
cd c:\Users\USER\Desktop\taiwan-stock-predictor
python run_gui.py
```

這會自動安裝所需依賴並啟動 GUI 應用。

### 方式 2: 打包為 EXE（生成可執行文件）

```bash
cd c:\Users\USER\Desktop\taiwan-stock-predictor
python build_exe.py
```

完成後，EXE 文件將在 `dist/Tixcraft_Auto_Register.exe` 中。

---

## GUI 介面使用

### 標籤 1：設定

1. **電話號碼** - 輸入目標電話號碼（默認: 3315003235）
2. **國碼** - 選擇對應的國碼（默認: +1 美國）
3. **SMS API 連結** - 輸入接收驗證碼的 API 端點
   - 默認: `https://api.sms8.net/api/record?token=b632kn5442ili34wycjmcxsjnlm6bq89jh4f`
4. **Google Sheets URL** - 輸入試算表URL並點擊「認證」進行連接
5. **名字** - 可留空（自動隨機）或輸入指定名字，點擊「隨機」生成新名字
6. **註冊數量** - 設定要註冊的帳號數量

### 標籤 2：控制

1. 點擊 **「開始註冊」** 按鈕開始自動註冊流程
2. 進度信息會實時顯示在日誌窗口中
3. 每個帳號註冊完成後會自動關閉瀏覽器頁面
4. 點擊 **「停止」** 可中止註冊流程

### 標籤 3：日誌

- 顯示所有已註冊帳號的詳細信息
- 包括：名字、身份證、電話、郵箱、生日、地址、性別、Google 帳戶、時間戳
- 點擊 **「清除歷史」** 可清空日誌表格

---

## 配置 Google Sheets

### 前置條件

1. 擁有 Google 帳戶
2. 創建 Google Sheets 試算表
3. 獲得試算表共享鏈接

### 認證步驟

1. 創建 Google Sheets 試算表：https://sheets.google.com/create
2. 複製試算表 URL
3. 在 GUI 中的 **「Google Sheets URL」** 欄位粘貼 URL
4. 點擊 **「認證」** 按鈕
5. 在彈出的瀏覽器窗口中使用您的 Google 帳戶登錄並授權
6. 認證成功後會看到提示信息

---

## SMS API 配置

### 獲取 API 連結

目前支持的 API：

#### 美國電話 (+1)
```
https://api.sms8.net/api/record?token=b632kn5442ili34wycjmcxsjnlm6bq89jh4f
```

#### 香港電話 (+852)
```
http://217api.com:9900/api/sms/getcode?token=24ac0cce96bd2057013b5e257c39ee1b
```

#### 台灣電話 (+886)
需要配置相應的 SMS 接收服務

---

## 隨機數據生成規則

每次註冊時會隨機生成：
- **地址** - 從台灣各縣市隨機生成
- **生日** - 1960-2000 年間隨機生成
- **性別** - 男/女 隨機選擇
- **郵箱** - 隨機生成 Gmail 地址
- **身份證** - 生成有效的台灣 ROC 格式身份證號

固定不變：
- **名字** - 根據用戶設定（自訂或隨機指定一次）
- **電話** - 根據用戶設定
- **國碼** - 根據用戶選擇

---

## 常見問題

### Q1: 無法連接 Google Sheets
**A:** 確保：
1. 網絡連接正常
2. 試算表 URL 正確無誤
3. 授權時未拒絕應用程序權限

### Q2: 未收到 SMS 驗證碼
**A:** 
1. 檢查 SMS API 連結是否正確
2. 確認電話號碼是否有效
3. 嘗試更換其他 SMS API 服務

### Q3: Tixcraft 頁面結構已變更
**A:** 如果選擇器無法匹配，可能是 Tixcraft 網站結構已更新。請：
1. 檢查 Tixcraft 網站是否有改版
2. 更新應用中的選擇器（需要編輯源代碼）
3. 聯絡開發者尋求幫助

### Q4: 如何修改選擇器
**A:** 編輯 `tixcraft_auto_register_gui.py` 文件中的 `fill_form` 方法：
```python
# 找到要修改的部分，例如：
name_inp = page.locator("#tixuserform-name, input[name*='name']").first
# 替換為新的選擇器
name_inp = page.locator("新選擇器").first
```

---

## 依賴包

該應用需要以下 Python 包：
- `PyQt5` - GUI 框架
- `playwright` - 瀏覽器自動化
- `gspread` - Google Sheets API
- `google-auth` 系列 - Google 認證
- `requests` - HTTP 請求

所有依賴會在首次運行時自動安裝。

---

## 技術詳情

### 架構
- **GUI 層** - PyQt5 圖形界面
- **自動化層** - Playwright 瀏覽器控制
- **數據層** - Google Sheets 存儲
- **工具層** - 數據生成、API 通信

### 工作流程
1. **初始化** - 讀取用戶配置
2. **生成數據** - 隨機生成個人信息
3. **打開瀏覽器** - 啟動 Playwright 無頭瀏覽器
4. **填寫表單** - 自動填寫註冊表單
5. **提交驗證** - 提交電話驗證
6. **等待 SMS** - 輪詢 SMS API
7. **輸入驗證碼** - 自動輸入收到的驗證碼
8. **完成註冊** - 確認驗證
9. **保存數據** - 上傳到 Google Sheets
10. **關閉頁面** - 關閉瀏覽器窗口

---

## 許可證

本工具僅供個人學習和研究使用。
使用本工具進行任何活動時請遵守相應的法律法規。

---

## 更新日誌

### v1.0 (2026-06-29)
- ✓ 初始版本發布
- ✓ 支持 GUI 介面
- ✓ Google Sheets 集成
- ✓ 批量註冊功能
- ✓ 完整的配置選項

---

## 聯絡方式

如有問題或建議，請聯絡開發者。

---

**祝使用愉快！** 🎉
