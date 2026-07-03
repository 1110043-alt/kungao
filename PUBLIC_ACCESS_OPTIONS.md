# 🌐 公網訪問方案

Serveo 隧道不夠穩定。以下是更可靠的選擇：

## 推薦方案：Zeabur（最穩定 ⭐⭐⭐）

### 為什麼選擇 Zeabur？
- ✅ 固定公網域名（不會改變）
- ✅ 自動 HTTPS 和免費 SSL
- ✅ 99.9% 可用性保證
- ✅ 自動部署和更新
- ✅ 支持自定義域名
- ✅ 完全免費（新用戶可免費試用）

### 5 分鐘快速部署

#### 第 1 步：推送到 GitHub（3 分鐘）
```powershell
cd c:\Users\USER\Desktop\taiwan-stock-predictor

# 創建 GitHub 倉庫後執行
git remote add origin https://github.com/YOUR_USERNAME/taiwan-stock-predictor.git
git branch -M main
git push -u origin main
```

#### 第 2 步：在 Zeabur 部署（2 分鐘）
1. 訪問 https://zeabur.com
2. 使用 GitHub 賬號登錄
3. 點擊「Deploy from Git」
4. 授權 GitHub
5. 選擇 `taiwan-stock-predictor` 倉庫
6. 點擊「部署」
7. 等待 2-3 分鐘自動部署完成

#### 第 3 步：獲得公網 URL ✅
```
https://taiwan-stock-predictor.zeabur.app
```

---

## 備選方案 1：Cloudflare Tunnel（免費、穩定）

### 優點
- ✅ 完全免費
- ✅ 穩定可靠
- ✅ 支持自定義域名
- ✅ 自動 HTTPS

### 設置步驟
```powershell
# 1. 下載 cloudflared
# 訪問: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# 2. 創建隧道
cloudflared tunnel create taiwan-stock

# 3. 啟動隧道
cloudflared tunnel run --url http://localhost:8080 taiwan-stock

# 4. 訪問
# https://taiwan-stock.[你的域名].workers.dev
```

---

## 備選方案 2：Railway（免費 $5 額度）

### 優點
- ✅ 簡單快速
- ✅ 免費 $5/月 額度
- ✅ 自動部署
- ✅ 完全免費試用

### 部署步驟
1. 訪問 https://railway.app
2. 點擊「Deploy」
3. 選擇「Deploy from GitHub」
4. 選擇 `taiwan-stock-predictor` 倉庫
5. 自動部署完成

---

## 備選方案 3：本地網絡共享

### 優點
- ✅ 超快速
- ✅ 完全免費
- ✅ 固定地址

### 設置步驟
```powershell
# 應用已在運行：
http://192.168.0.110:8080

# 在同一網絡的其他設備上訪問
# 從手機/平板通過 WiFi 訪問同一地址
```

---

## 快速決策表

| 方案 | 設置時間 | 成本 | 穩定性 | 推薦度 |
|------|---------|------|--------|--------|
| **Zeabur** | 5 分鐘 | 免費 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Railway** | 3 分鐘 | 免費 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cloudflare** | 10 分鐘 | 免費 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Serveo** | 1 分鐘 | 免費 | ⭐⭐ | ⭐ |
| **本地網絡** | 0 分鐘 | 免費 | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## 📱 立即試用

在同一網絡上立即訪問：
```
http://192.168.0.110:8080
```

---

## 🎯 建議流程

### 今天（第 1 天）
1. 在本地網絡上測試：`http://192.168.0.110:8080`
2. 創建 GitHub 帳戶（如無）
3. 推送代碼到 GitHub

### 明天（第 2 天）
1. 登錄 Zeabur
2. 連接 GitHub 倉庫
3. 獲得公網 URL
4. 全球訪問 ✅

---

## 快速命令

```powershell
# GitHub 推送
git remote add origin https://github.com/YOUR_USERNAME/taiwan-stock-predictor.git
git push -u origin main

# 本地訪問
# http://192.168.0.110:8080

# Zeabur 訪問（部署後）
# https://taiwan-stock-predictor.zeabur.app
```

---

## 有任何問題？

- [Zeabur 文檔](https://docs.zeabur.com)
- [Railway 文檔](https://docs.railway.app)
- [Cloudflare 文檔](https://developers.cloudflare.com)

---

**推薦：立即使用 Zeabur！5 分鐘內獲得穩定的公網訪問。**
