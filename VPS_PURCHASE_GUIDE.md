# 🖥️ VPS 購買與部署指南

> **目標**: 購買VPS並部署24/7監控Bot

---

## 💰 推薦VPS服務商

### 🥇 推薦：Linode（高性價比）

**特點**:
- 💵 最便宜: $5/月 (1GB RAM)
- 🌍 全球伺服器
- ⚡ 速度快
- 📊 管理面板友善

**官網**: https://www.linode.com/

**適合你的配置**:
```
Linode 5GB 方案
• CPU: 1 Core
• RAM: 1GB
• 存儲: 25GB SSD
• 帶寬: 1TB/月
• 價格: $5/月
```

### 🥈 次選：DigitalOcean

**特點**:
- 💵 價格: $4/月 (也有$5/月更穩定)
- 🌍 亞洲伺服器 (新加坡)
- ⚡ 很快
- 📱 手機App管理

**官網**: https://www.digitalocean.com/

**適合你的配置**:
```
Droplet 基礎方案
• CPU: 1 Core
• RAM: 512MB
• 存儲: 10GB SSD
• 價格: $4/月
```

### 🥉 經濟選擇：Vultr

**特點**:
- 💵 按小時計費: $0.004/小時 (~$2.4/月)
- 🌍 有東京/新加坡節點
- ⚡ 高速
- 💳 支援信用卡

**官網**: https://www.vultr.com/

---

## 🛒 購買步驟（以Linode為例）

### 第1步：註冊帳號

1. 訪問 https://www.linode.com/
2. 點擊 「Sign Up」
3. 填寫郵箱、密碼、姓名
4. 驗證郵箱
5. ✅ 帳號建立完成

### 第2步：添加支付方式

1. 登入Linode
2. 左側菜單 → 「Account」
3. 「Billing Info」→ 「Payment Method」
4. 添加信用卡（Visa/Mastercard）
5. ✅ 支付方式已設定

### 第3步：建立Linode實例

1. 點擊 「Linodes」
2. 「Create Linode」
3. **選擇映像**:
   ```
   Ubuntu 20.04 LTS (推薦)
   或 Ubuntu 22.04 LTS
   ```

4. **選擇方案**:
   ```
   Linode 5GB ($5/月)
   或更高配置
   ```

5. **選擇位置**:
   ```
   Tokyo (東京) - 離台灣最近
   或 Singapore (新加坡)
   ```

6. **根密碼**:
   ```
   設定一個強密碼，保存好！
   ```

7. 點擊 「Create」
8. ⏳ 等待 2-5 分鐘

### 第4步：連接到VPS

#### 使用SSH連接（推薦）

**Windows:**
```bash
# 安裝 PuTTY 或 使用 Windows Terminal
# 如果用 Windows Terminal:
ssh root@你的_VPS_IP
# 輸入密碼
```

**Mac/Linux:**
```bash
ssh root@你的_VPS_IP
```

#### 使用Web Console（備選）

1. 在Linode控制台
2. 選擇你的Linode
3. 點擊 「Glish」(LISH)
4. 在線終端打開

---

## 🚀 VPS部署（自動化腳本）

### 方式1：一鍵安裝（推薦）

在你的VPS上執行：

```bash
# 1. 下載部署腳本
curl -O https://raw.githubusercontent.com/你的用戶名/taiwan-stock-predictor/main/vps_deploy.sh

# 2. 給予執行權限
chmod +x vps_deploy.sh

# 3. 執行部署
./vps_deploy.sh
```

### 方式2：手動部署

如果一鍵腳本不工作，手動執行以下命令：

```bash
# 1. 更新系統
sudo apt update
sudo apt upgrade -y

# 2. 安裝Python和pip
sudo apt install python3 python3-pip git -y

# 3. 克隆倉庫
git clone https://github.com/你的用戶名/taiwan-stock-predictor.git
cd taiwan-stock-predictor

# 4. 安裝依賴
pip3 install -r requirements.txt

# 5. 編輯配置
nano monitor_config.json
# 修改:
# - bot_token: 你的Bot Token
# - channel_id: 你的頻道ID
# 保存: Ctrl+X → Y → Enter

# 6. 使用screen後台運行（推薦）
screen -S discord-bot
python3 discord_bot_monitor.py

# 7. 分離screen（保持運行）
# 按 Ctrl+A 然後按 D

# 8. 後續重新連接
# screen -r discord-bot
```

---

## 📁 我為你準備的部署腳本

### `vps_deploy.sh` - 一鍵安裝

```bash
#!/bin/bash
set -e

echo "🚀 開始VPS部署..."

# 1. 更新系統
echo "📦 更新系統..."
sudo apt update
sudo apt upgrade -y

# 2. 安裝依賴
echo "📥 安裝Python和Git..."
sudo apt install python3 python3-pip git curl -y

# 3. 克隆倉庫
echo "📥 克隆代碼倉庫..."
if [ ! -d "taiwan-stock-predictor" ]; then
    git clone https://github.com/YOUR_USERNAME/taiwan-stock-predictor.git
fi

cd taiwan-stock-predictor

# 4. 安裝Python依賴
echo "📦 安裝Python依賴..."
pip3 install -r requirements.txt

# 5. 建立目錄
mkdir -p snapshots logs

# 6. 提示配置
echo ""
echo "✅ 安裝完成！"
echo ""
echo "📝 下一步："
echo "1. 編輯配置: nano monitor_config.json"
echo "   - bot_token: 你的Bot Token"
echo "   - channel_id: 你的頻道ID"
echo ""
echo "2. 運行Bot:"
echo "   screen -S discord-bot"
echo "   python3 discord_bot_monitor.py"
echo ""
echo "3. 分離screen (Ctrl+A 然後 D)"
echo ""
echo "4. 檢查日誌:"
echo "   tail -f logs/bot.log"
```

---

## 🔧 VPS後續管理

### 查看Bot狀態

```bash
# 查看screen會話
screen -ls

# 重新連接
screen -r discord-bot

# 查看日誌
tail -f logs/bot.log

# 查看進程
ps aux | grep discord_bot_monitor.py
```

### 重啟Bot

```bash
# 連接到screen
screen -r discord-bot

# 停止Bot (Ctrl+C)

# 重啟
python3 discord_bot_monitor.py
```

### 自動重啟（systemd）

建立 `/etc/systemd/system/discord-bot.service`:

```ini
[Unit]
Description=Discord Bot Monitor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/taiwan-stock-predictor
ExecStart=/usr/bin/python3 /root/taiwan-stock-predictor/discord_bot_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

啟用自動啟動：

```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl start discord-bot

# 查看狀態
sudo systemctl status discord-bot

# 查看日誌
sudo journalctl -u discord-bot -f
```

---

## 🔐 VPS安全設定

### 1. 禁用密碼登入，使用SSH鑰匙

```bash
# 生成SSH鑰匙對（本地機器）
ssh-keygen -t rsa -b 4096

# 複製公鑰到VPS
ssh-copy-id -i ~/.ssh/id_rsa.pub root@你的_VPS_IP

# 禁用密碼登入
sudo nano /etc/ssh/sshd_config

# 找到並改為：
# PermitRootLogin prohibit-password
# PasswordAuthentication no

# 重啟SSH
sudo systemctl restart ssh
```

### 2. 安裝防火牆

```bash
# 安裝UFW
sudo apt install ufw -y

# 允許SSH
sudo ufw allow 22/tcp

# 允許HTTP/HTTPS（如果有Web服務）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 啟用防火牆
sudo ufw enable

# 查看狀態
sudo ufw status
```

### 3. 設定Fail2Ban防止暴力攻擊

```bash
# 安裝
sudo apt install fail2ban -y

# 啟動
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

---

## 💡 效能優化

### 增加Swap記憶體

```bash
# 檢查當前Swap
free -h

# 創建2GB Swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久啟用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 監控系統資源

```bash
# 實時監控
top

# 或使用htop（更好看）
sudo apt install htop -y
htop

# 查看磁碟使用
df -h

# 查看記憶體
free -h
```

---

## 🚨 故障排除

### ❌ 無法SSH連接

**症狀**: SSH超時

**解決**:
1. 檢查IP地址是否正確
2. 檢查防火牆設定
3. 在Linode控制台用Glish重新連接
4. 檢查密鑰權限: `chmod 600 ~/.ssh/id_rsa`

### ❌ Bot無法啟動

**症狀**: ImportError或其他錯誤

**解決**:
```bash
# 檢查Python版本
python3 --version

# 重新安裝依賴
pip3 install --upgrade -r requirements.txt

# 查看完整錯誤
python3 discord_bot_monitor.py
```

### ❌ 記憶體不足

**症狀**: Bot經常崩潰

**解決**:
1. 增加Swap (見上方)
2. 增加VPS配置
3. 減少監控目標數量

### ❌ Bot離線

**症狀**: 長時間無回應

**解決**:
```bash
# 檢查bot是否還在運行
ps aux | grep discord_bot_monitor.py

# 查看日誌
tail -100 logs/bot.log

# 重啟
screen -r discord-bot
# Ctrl+C 停止
python3 discord_bot_monitor.py
```

---

## 📊 成本對比

| VPS服務 | 月費 | CPU | RAM | SSD | 位置 |
|--------|------|-----|-----|-----|------|
| Linode 5GB | $5 | 1核 | 1GB | 25GB | 全球 |
| DigitalOcean | $5 | 1核 | 1GB | 25GB | 全球 |
| Vultr | $2.4 | 1核 | 512MB | 10GB | 全球 |
| AWS EC2 | $2.8 | 1核 | 512MB | 8GB | 全球 |

**推薦**: Linode ($5/月) - 性價比最好

---

## 🎯 VPS部署清單

### 購買階段
- [ ] 選擇VPS服務商
- [ ] 購買最低配置方案
- [ ] 記下VPS IP地址和密碼
- [ ] 驗證可以SSH連接

### 準備階段
- [ ] 確認Bot Token已配置
- [ ] 確認Channel ID已配置
- [ ] 代碼已上傳GitHub

### 部署階段
- [ ] SSH連接到VPS
- [ ] 執行一鍵部署腳本
- [ ] 編輯monitor_config.json
- [ ] 啟動Bot

### 驗證階段
- [ ] Bot成功啟動
- [ ] 在Discord輸入 !status 有回應
- [ ] 日誌無錯誤
- [ ] 配置自動重啟

### 上線後
- [ ] 設定防火牆
- [ ] 配置SSH鑰匙認證
- [ ] 定期檢查日誌
- [ ] 監控系統資源

---

## 🎉 下一步

### 立即行動

```
1️⃣  選擇VPS (推薦 Linode)
   https://www.linode.com/

2️⃣  購買方案 ($5/月)

3️⃣  記下IP和密碼

4️⃣  SSH連接

5️⃣  執行一鍵部署

6️⃣  配置Bot並啟動

7️⃣  在Discord測試

✅ 完成！24/7自動監控
```

### 購買後聯繫我

提供:
- VPS IP地址
- SSH用戶名 (通常是root)

我會幫你:
- ✅ 一鍵部署Bot
- ✅ 配置自動啟動
- ✅ 設定防火牆
- ✅ 優化效能

---

**選擇Linode，享受穩定的VPS服務！** 🚀

有任何問題，我都在這裡幫助！
