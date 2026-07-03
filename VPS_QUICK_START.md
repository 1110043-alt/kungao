# 🖥️ VPS 快速開始

> **你購買VPS後立即執行這個指南**

---

## ⚡ 5分鐘快速部署

### 第1步：SSH連接到VPS

**Windows 10/11 (PowerShell):**
```powershell
ssh root@你的VPS_IP
# 輸入密碼
```

**Mac/Linux:**
```bash
ssh root@你的VPS_IP
```

### 第2步：下載部署腳本

在VPS終端執行：

```bash
# 下載腳本
curl -O https://raw.githubusercontent.com/你的用戶名/taiwan-stock-predictor/main/vps_deploy.sh

# 給予執行權限
chmod +x vps_deploy.sh

# 執行部署
sudo ./vps_deploy.sh
```

### 第3步：配置Bot

部署腳本完成後，編輯配置：

```bash
nano /opt/discord-bot/monitor_config.json
```

修改以下項目：

```json
{
    "bot_token": "你的Bot Token",
    "channel_id": "你的頻道ID",
    "check_interval": 30,
    "targets": [
        {
            "name": "Tixcraft",
            "url": "https://tixcraft.com",
            "selector": ".game-item"
        }
    ]
}
```

保存: **Ctrl+X** → **Y** → **Enter**

### 第4步：啟動Bot

```bash
# 啟用自動啟動
systemctl enable discord-bot

# 立即啟動
systemctl start discord-bot

# 檢查狀態
systemctl status discord-bot
```

### 第5步：驗證

在你的Discord頻道輸入：

```
!status
```

Bot應該回應你的監控狀態 ✅

---

## 📋 配置文件快速指南

### Bot Token

```bash
# 獲取方法:
1. 訪問 https://discord.com/developers/applications
2. 選擇你的應用
3. 左側 Bot → Copy Token
```

### 頻道ID

```bash
# 獲取方法:
1. Discord 設定 → 進階 → 開發者模式 (開啟)
2. 右鍵頻道 → 複製頻道ID
```

### CSS選擇器

```bash
# 網頁上檢查元素
1. 按 F12 開啟開發者工具
2. 找到目標元素
3. 複製它的 class 或 id

# 例子:
".ticket-status"      # class選擇器
"#countdown"          # id選擇器
".game-item, .active" # 多個選擇器
```

---

## 🔧 常用命令

### 查看日誌

```bash
# 實時查看
journalctl -u discord-bot -f

# 查看最近100行
journalctl -u discord-bot -n 100

# 查看特定時間
journalctl -u discord-bot --since "2024-01-01 10:00:00"
```

### 管理Bot

```bash
# 查看狀態
systemctl status discord-bot

# 重啟Bot
systemctl restart discord-bot

# 停止Bot
systemctl stop discord-bot

# 停用自動啟動
systemctl disable discord-bot
```

### 查看系統資源

```bash
# 實時監控
top

# 或使用htop (更好看)
apt install htop -y
htop

# 查看磁碟
df -h

# 查看記憶體
free -h

# 查看進程
ps aux | grep discord_bot
```

---

## 🆘 常見問題排解

### ❌ SSH連接失敗

**症狀**: 無法連接到VPS

**解決**:
```bash
# 1. 確認IP地址正確
# 2. 檢查SSH端口是否開放
# 3. 檢查防火牆設定

# 在Linode控制台:
# → Linodes → 你的Linode → LISH Console
# 使用Web終端連接
```

### ❌ 部署腳本失敗

**症狀**: vps_deploy.sh 執行出錯

**解決**:
```bash
# 1. 確認使用root身份
sudo ./vps_deploy.sh

# 2. 更新系統
sudo apt update && sudo apt upgrade -y

# 3. 檢查網路連接
ping google.com

# 4. 查看詳細錯誤
bash -x vps_deploy.sh
```

### ❌ Bot無法啟動

**症狀**: systemctl start discord-bot 失敗

**解決**:
```bash
# 1. 檢查配置檔
cat /opt/discord-bot/monitor_config.json

# 2. 查看詳細錯誤
journalctl -u discord-bot -n 50 -e

# 3. 手動運行測試
cd /opt/discord-bot
source venv/bin/activate
python3 discord_bot_monitor.py

# Ctrl+C 停止
```

### ❌ Bot在線但無回應

**症狀**: Bot在Discord顯示在線，但 !status 無回應

**解決**:
```bash
# 1. 檢查Bot是否在監聽事件
journalctl -u discord-bot -f

# 2. 驗證Bot在服務器中
# Discord → 伺服器 → 成員 → 搜索Bot名稱

# 3. 檢查Bot權限
# Discord → 伺服器設定 → 角色 → Bot角色
# 確保Bot有"傳送訊息"權限

# 4. 重啟Bot
systemctl restart discord-bot
```

### ❌ 記憶體不足

**症狀**: Bot經常崩潰或變慢

**解決**:
```bash
# 1. 查看記憶體使用
free -h

# 2. 增加Swap (虛擬記憶體)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 3. 檢查後台進程
ps aux --sort=-%mem | head

# 4. 升級VPS配置
# Linode控制台 → 選擇Linode → Resize Disk
```

---

## 📊 部署檢查清單

### 購買階段
- [ ] 購買VPS (推薦 Linode $5/月)
- [ ] 記下VPS IP
- [ ] 設定root密碼
- [ ] SSH連接成功

### 準備階段
- [ ] Bot Token 已取得
- [ ] Channel ID 已取得
- [ ] 代碼已上傳GitHub
- [ ] monitor_config.json 已準備

### 部署階段
- [ ] SSH連接到VPS
- [ ] 下載 vps_deploy.sh
- [ ] 執行 sudo ./vps_deploy.sh
- [ ] 腳本執行完成

### 配置階段
- [ ] 編輯 monitor_config.json
- [ ] Bot Token 已填入
- [ ] Channel ID 已填入
- [ ] 至少1個監控目標

### 啟動階段
- [ ] systemctl start discord-bot
- [ ] systemctl status 顯示 active
- [ ] 日誌無錯誤
- [ ] !status 有回應

### 上線階段
- [ ] !list-targets 正常
- [ ] !check-now 正常
- [ ] 監控正常運行
- [ ] 日誌無警告

---

## 🚀 下一步

### 連接VPS後告訴我

提供:
```
- VPS IP: XXX.XXX.XXX.XXX
- SSH用戶名: root (通常)
- VPS系統: Ubuntu 20.04 (或其他)
```

我會幫你:
```
✅ 一鍵部署所有依賴
✅ 配置自動啟動
✅ 測試Bot連接
✅ 優化性能
✅ 設定監控告警
```

---

## 📞 支援

如遇到問題:

1. **查看日誌**
   ```bash
   journalctl -u discord-bot -f
   ```

2. **查看詳細日誌**
   ```bash
   journalctl -u discord-bot -n 200
   ```

3. **手動測試**
   ```bash
   cd /opt/discord-bot
   source venv/bin/activate
   python3 discord_bot_monitor.py
   ```

4. **重啟VPS**
   ```bash
   sudo reboot
   ```

---

**祝你部署順利！** 🎉

有任何問題，我都在這裡幫助！💪
