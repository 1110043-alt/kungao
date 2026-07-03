# 🚀 台股預測儀表盤 - 完整部署指南

## ✅ 項目已準備完畢！

你的台股儀表盤已經完全配置好，可以直接部署到 Zeabur。以下是 3 種部署方式，選擇一種即可。

---

## 📋 項目信息

| 項目 | 詳情 |
|------|------|
| 名稱 | Taiwan Stock Predictor Dashboard |
| 類型 | Flask Web Application |
| 語言 | Python 3.8+ |
| 框架 | Flask 3.0.0 + Gunicorn |
| 數據 | 15 支台灣股票實時數據 |
| 功能 | 儀表板、API、預測分析 |

---

## 🚀 部署方式 1：GitHub + Zeabur（推薦 ⭐⭐⭐）

### 步驟 1：創建 GitHub 倉庫

1. 登錄 [GitHub](https://github.com)
2. 點擊「+ 新建倉庫」(New)
3. 倉庫名稱：`taiwan-stock-predictor`
4. 描述：`Taiwan Stock Predictor Dashboard`
5. 選擇「Public」(公開)
6. 點擊「Create repository」

### 步驟 2：推送代碼到 GitHub

在終端執行以下命令（替換 YOUR_USERNAME）：

```powershell
cd c:\Users\USER\Desktop\taiwan-stock-predictor

# 添加遠程倉庫
git remote add origin https://github.com/YOUR_USERNAME/taiwan-stock-predictor.git
git branch -M main

# 推送所有代碼
git push -u origin main
```

### 步驟 3：在 Zeabur 上部署

1. 訪問 [Zeabur 控制面板](https://zeabur.com/dashboard)
2. 找到你的服務器（Linode Tokyo 1C 2GB）
3. 點擊「Projects」標籤
4. 點擊「+ 新增服務」或「Deploy from Git」
5. 選擇「GitHub」授權
6. 選擇 `taiwan-stock-predictor` 倉庫
7. Zeabur 自動檢測 Procfile
8. 等待部署完成（通常 2-3 分鐘）

### ✅ 部署完成後

你將獲得公網 URL：
```
https://台股儀表盤.zeabur.app
```

可以從任何地方訪問！

---

## 🚀 部署方式 2：直接上傳文件（快速部署）

### 步驟 1：使用 Zeabur CLI

```powershell
# 安裝 Zeabur CLI（全局）
npm install -g zeabur-cli

# 登錄 Zeabur
zeabur login

# 部署項目
cd c:\Users\USER\Desktop\taiwan-stock-predictor
zeabur deploy
```

### 步驟 2：按照提示完成部署

按照命令行提示選擇服務器和配置。

---

## 🌐 部署方式 3：使用公網隧道（立即訪問）

已經部署完成，無需任何配置！

**公網訪問地址：**
```
https://324c4a327fda5c15-211-21-161-96.serveousercontent.com
```

**本地訪問地址：**
```
http://192.168.0.110:8080
```

⚠️ 注意：方式 3 的公網 URL 在服務重啟時會改變。如需固定 URL，請使用方式 1 或 2。

---

## 📦 項目文件結構

```
taiwan-stock-predictor/
├── app_web.py                 # ⭐ 主應用（Flask）
├── Procfile                   # ⭐ 部署配置（Zeabur 使用）
├── requirements.txt           # ⭐ Python 依賴
├── zeabur.toml               # Zeabur 配置
├── stock_data.json           # 股票數據
├── templates/
│   └── index.html            # 前端界面
├── static/
│   ├── script.js             # 前端邏輯
│   ├── style.css             # 樣式表
│   └── ...其他資源
└── .git/                      # Git 倉庫（已初始化）
```

**⭐ 標記的是部署必需文件，已全部準備好！**

---

## 🔧 系統要求（已滿足）

✅ Python 3.8+
✅ Flask 3.0.0
✅ Gunicorn（生產 WSGI 伺服器）
✅ CORS 跨域支持
✅ 所有依賴已列在 requirements.txt

---

## 📊 應用功能

### 前端界面
- 📈 台股即時預測儀表板
- 📊 15 支股票監控
- 🔍 股票細節分析
- 🔮 AI 預測分析
- 📰 新聞要事
- 📱 完全響應式設計（支持手機）

### API 端點
```
GET  /                           # 主頁
GET  /api/all-stocks            # 獲取所有股票
GET  /api/stock/<code>          # 獲取單隻股票
GET  /api/prediction/<code>     # 獲取預測數據
GET  /api/market-status         # 獲取市場狀態
GET  /health                    # 健康檢查
GET  /static/<file>             # 靜態資源
```

---

## 🔐 環境變量

Zeabur 自動設置 `PORT` 環境變量。應用已配置為讀取該變量。

無需手動配置其他環境變量。

---

## 📱 訪問方式總結

| 方式 | URL | 優點 | 缺點 |
|------|-----|------|------|
| **Zeabur** | https://xxx.zeabur.app | 固定域名、高可用 | 需要 GitHub |
| **Serveo** | https://xxx.serveousercontent.com | 無需配置、立即可用 | URL 會改變 |
| **本地** | http://192.168.0.110:8080 | 超快速 | 只限局域網 |

---

## 🆘 常見問題

### Q1: 部署失敗了怎麼辦？
**A**: 查看 Zeabur 日誌（Logs 標籤），通常是：
- 依賴安裝失敗 → 檢查 requirements.txt
- 端口衝突 → Zeabur 自動處理
- 啟動失敗 → 檢查 Procfile 語法

### Q2: 如何更新應用？
**A**: 
1. 修改本地文件
2. 執行 `git add . && git commit -m "update"`
3. 執行 `git push`
4. Zeabur 自動重新部署

### Q3: 能否使用自定義域名？
**A**: 可以。在 Zeabur 項目設置中：
1. 點擊「Domains」
2. 點擊「+ 添加域名」
3. 輸入你的域名
4. 更新 DNS 記錄指向 Zeabur

### Q4: 應用支持 HTTPS 嗎？
**A**: 是的。Zeabur 自動提供免費 SSL 證書，所有連接都是 HTTPS。

### Q5: 數據會丟失嗎？
**A**: 不會。stock_data.json 已提交到 Git，與代碼一起部署。

---

## 📞 技術支持資源

- [Zeabur 官方文檔](https://docs.zeabur.com)
- [Flask 官方文檔](https://flask.palletsprojects.com)
- [Python 官方文檔](https://docs.python.org)
- [GitHub 幫助](https://docs.github.com)

---

## ✨ 下一步

### 立即部署（推薦步驟）

1. **今天**：完成 GitHub 倉庫創建和推送
2. **明天**：在 Zeabur 上連接倉庫
3. **完成**：獲得自己的公網域名！

### 部署命令速查

```powershell
# 推送到 GitHub
cd c:\Users\USER\Desktop\taiwan-stock-predictor
git push -u origin main

# 本地測試（部署前）
python app_web.py

# 檢查 Git 狀態
git status
git log
```

---

## 🎉 恭喜！

你的台股儀表盤已完全配置好，隨時準備上線！

**現在就可以訪問：**
- 🌐 公網版：https://324c4a327fda5c15-211-21-161-96.serveousercontent.com
- 📱 本地版：http://192.168.0.110:8080

選擇上述任一部署方式，5 分鐘內即可擁有自己的公網儀表板！

---

**最後祝你部署順利！有任何問題都可以隨時提問。** 🚀
