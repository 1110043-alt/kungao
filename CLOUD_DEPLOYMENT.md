<!--
🚀 台股預測儀表板 - 雲端部署設定指南
使用於: Zeabur、Render、Heroku 等平台
-->

# 雲端部署配置指南

## 📋 目錄結構
```
taiwan-stock-predictor/
├── cloud_ready_app.py          # 雲端就緒主應用
├── simple_app.py               # Flask API 後端
├── requirements.txt            # Python 依賴
├── templates/
│   └── index.html              # 前端頁面
├── static/
│   ├── script.js               # 前端邏輯
│   ├── style.css               # 樣式
│   └── ...其他靜態文件
└── CLOUD_DEPLOYMENT.md         # 本檔案
```

---

## 🚀 部署到 Zeabur

### 1️⃣ 連接 Git 倉庫
- 將項目推送到 GitHub
- 在 Zeabur 中選擇「新建服務」
- 選擇「GitHub」連接您的倉庫

### 2️⃣ 配置服務
- **運行時**: Python 3.10+
- **啟動命令**: `python cloud_ready_app.py`
- **Python 版本**: 3.10

### 3️⃣ 環境變數設置
在 Zeabur 中添加以下環境變數：
```
PORT=5555
HOST=0.0.0.0
DEBUG=False
```

### 4️⃣ 部署
- Zeabur 會自動檢測 `requirements.txt`
- 自動安裝依賴
- 自動部署應用

---

## 🎯 部署到 Render

### 1️⃣ 創建新服務
- 登入 Render.com
- 選擇「New +」 → 「Web Service」
- 連接 GitHub 倉庫

### 2️⃣ 配置
- **Name**: taiwan-stock-predictor
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python cloud_ready_app.py`

### 3️⃣ 環境變數
```
PORT=5555
HOST=0.0.0.0
DEBUG=False
```

### 4️⃣ 部署
- Render 會自動檢測 Python 項目
- 自動構建和部署
- 提供公開 URL

---

## 🐳 部署到 Docker

### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 暴露端口（Zeabur/Render 會設置 PORT 環境變數）
EXPOSE 5555

# 啟動應用
CMD ["python", "cloud_ready_app.py"]
```

### 構建和運行
```bash
# 本地測試
docker build -t taiwan-stock-predictor .
docker run -p 5555:5555 -e PORT=5555 taiwan-stock-predictor

# 推送到 Docker Hub（可選）
docker tag taiwan-stock-predictor username/taiwan-stock-predictor
docker push username/taiwan-stock-predictor
```

---

## 📍 環境變數詳解

| 變數名 | 預設值 | 說明 | 範例 |
|--------|--------|------|------|
| **PORT** | 5555 | 服務監聽端口 | `5555`, `8080`, `3000` |
| **HOST** | 0.0.0.0 | 監聽地址 (0.0.0.0 = 所有網絡) | `0.0.0.0`, `127.0.0.1` |
| **DEBUG** | False | 調試模式 (開發才用 True) | `False`, `true` |

### 為什麼要用 0.0.0.0？
- `127.0.0.1`: 只能本地訪問
- `0.0.0.0`: 允許所有網絡接口訪問（雲端必須）

---

## 💻 本地測試（模擬雲端環境）

### 測試 1: 使用預設端口
```bash
python cloud_ready_app.py
# 訪問: http://localhost:5555
```

### 測試 2: 使用自定義端口
```bash
PORT=8080 python cloud_ready_app.py
# 訪問: http://localhost:8080
```

### 測試 3: 生產模式（使用 Waitress）
```bash
DEBUG=False python cloud_ready_app.py
```

### 測試 4: 開發模式（自動重載）
```bash
DEBUG=True python cloud_ready_app.py
```

---

## 🔧 生產級部署最佳實踐

### ✅ 已配置
- ✅ 環境變數支持（PORT、HOST、DEBUG）
- ✅ CORS 已啟用（允許跨域請求）
- ✅ Waitress 服務器（高性能）
- ✅ 自動重載開發模式
- ✅ 完整的日誌輸出

### 📝 部署檢查清單
- [ ] 將 `DEBUG=False` 設置在生產環境
- [ ] 確保 `PORT` 環境變數被正確設置
- [ ] 驗證 `requirements.txt` 包含所有依賴
- [ ] 測試 API 是否返回數據
- [ ] 檢查前端是否正常加載
- [ ] 監控日誌以檢查錯誤

### 🚨 常見問題

**Q: 為什麼要用 Waitress？**
A: Flask 內置服務器不適合生產。Waitress 是輕量級、穩定的 WSGI 服務器。

**Q: 雲端平台如何分配端口？**
A: 通過 PORT 環境變數。應用應讀取此變數而不是硬編碼。

**Q: 0.0.0.0 是什麼意思？**
A: 監聽所有可用的網絡接口。在容器化環境中必須使用。

**Q: 前端和後端如何通信？**
A: 前端在 JavaScript 中動態構建 API URL，自動適應任何端口。

---

## 📊 部署後驗證

### 1️⃣ 檢查 API 連接
```bash
curl https://your-domain.com/api/all-stocks
# 應該返回 JSON 格式的股票數據
```

### 2️⃣ 檢查前端
- 訪問 `https://your-domain.com/`
- 查看瀏覽器控制台 (F12) 是否有錯誤

### 3️⃣ 檢查日誌
在雲端平台的日誌面板查看：
- 應用是否成功啟動
- API 是否正常運行
- 是否有錯誤堆棧跟蹤

---

## 🎓 更多資源

- [Zeabur 文檔](https://zeabur.com/docs)
- [Render 文檔](https://render.com/docs)
- [Waitress 文檔](https://docs.pylonsproject.org/projects/waitress/)
- [Flask 部署指南](https://flask.palletsprojects.com/deployment/)

---

## 📞 支援

遇到問題？檢查：
1. ✅ 環境變數是否正確設置
2. ✅ `requirements.txt` 是否完整
3. ✅ Python 版本是否 3.8+
4. ✅ 雲端平台的構建日誌
5. ✅ 本地測試是否成功

祝部署順利！ 🚀
