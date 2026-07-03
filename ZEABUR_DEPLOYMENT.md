# 🚀 Zeabur 部署指南 - Taiwan Stock Predictor

> ⚠️ **Render 有 502 問題，改用 Zeabur 台灣服務器部署**

## 📋 前置準備

✅ GitHub 仓库已配置：`https://github.com/1110043-alt/kungao`
✅ Flask 应用已完成：`simple_app.py`
✅ 本機測試成功：http://localhost:8080 正常運行

---

## 🔧 部署步驟

### **第 1 步：訪問 Zeabur 官網**
1. 打開 https://zeabur.com/zh-TW
2. 点击右上角「登入」或「開始使用」
3. 用 **GitHub 账户** 登入

### **第 2 步：連接 GitHub 倉庫**
1. 登入后，点击 **「+ 新增專案」**
2. 選擇 **「從 GitHub 導入」**
3. 找到并选择 `1110043-alt/kungao` 倉庫
4. 授予 Zeabur 訪問權限

### **第 3 步：配置應用設定**
1. 選擇 **Web 服務** 類型
2. 設定環境變數：
   ```
   HOST=0.0.0.0
   PORT=8080
   DEBUG=False
   ```
3. 設定啟動命令：
   ```
   pip install -r requirements.txt && python simple_app.py
   ```

### **第 4 步：部署**
1. 点击 **「部署」** 按鈕
2. 等待 2-3 分鐘完成部署
3. 獲取公共 URL（例如：`https://taiwan-stock-predictor-xxx.zeabur.app`）

---

## 📱 部署後驗證

✅ **訪問首頁**：https://your-zeabur-url/

✅ **測試 API**：
```bash
curl https://your-zeabur-url/api/all-stocks
curl https://your-zeabur-url/api/top-stocks
```

✅ **手機訪問**：直接用手機瀏覽器打開公網 URL

---

## 🆚 Zeabur vs Render 對比

| 功能 | Zeabur | Render |
|------|--------|--------|
| **地點** | 台灣 🇹🇼 | 美國 🇺🇸 |
| **速度** | ⚡ 快（台灣用戶） | 普通 |
| **免費額度** | 5 GB/月 | 有限 |
| **部署方式** | GitHub 自動 | GitHub 自動 |
| **支持** | 台灣支持 | 英文支持 |

---

## 🐛 常見問題

### 1️⃣ 部署失敗顯示 502？
- ✅ 檢查 `requirements.txt` 是否齊全
- ✅ 確認 `simple_app.py` 中的 PORT 使用環境變數
- ✅ 查看 Zeabur 部署日誌找出具體錯誤

### 2️⃣ 數據顯示為 0？
- ✅ 檢查 yfinance 是否能連接（可能網絡限制）
- ✅ 查看服務器日誌中的 DEBUG 輸出
- ✅ 本機測試確認 API 工作

### 3️⃣ 手機訪問顯示不正常？
- ✅ 清除瀏覽器緩存（Ctrl+Shift+Delete）
- ✅ 檢查 CSS 版本號已更新：`style.css?v=20260621d`
- ✅ 確認視口元標籤存在：`<meta name="viewport" ...>`

---

## 💡 優化建議

### 如果 Zeabur 也有問題，可嘗試：

1. **Railway**（https://railway.app）
   - 支持 GitHub 連接
   - 新手友好
   - 每月 $5 免費額度

2. **Vercel**（https://vercel.com）
   - 專注前端，但支持 API 路由
   - 非常快速

3. **本地 WiFi 共享**（最穩定 ✅）
   ```
   手機連接同一 WiFi
   訪問：http://192.168.X.X:8080
   ```

---

## 📝 部署清單

- [ ] GitHub 倉庫已準備好
- [ ] Zeabur 帳户已創建
- [ ] 倉庫已連接到 Zeabur
- [ ] 環境變數已設定
- [ ] 應用已部署
- [ ] 公網 URL 已確認
- [ ] API 測試成功
- [ ] 手機訪問成功

---

## 🎯 最終結果

部署完成後，你的應用將：
- ✅ 24/7 在線運行
- ✅ 所有用戶都能訪問（無需同一 WiFi）
- ✅ 自動同步 GitHub 更新
- ✅ 完整的股票數據和移動響應式設計

祝部署順利！🚀
