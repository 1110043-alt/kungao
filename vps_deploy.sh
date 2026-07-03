#!/bin/bash

# 🚀 VPS 一鍵部署腳本
# 使用: chmod +x vps_deploy.sh && ./vps_deploy.sh

set -e

echo "╔════════════════════════════════════════════════╗"
echo "║        🤖 Discord Bot VPS 一鍵部署             ║"
echo "║        24/7自動監控 + 網頁通知               ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# 檢查是否是root
if [ "$EUID" -ne 0 ]; then
    echo "❌ 請以root身份運行此腳本"
    echo "   執行: sudo ./vps_deploy.sh"
    exit 1
fi

echo "📋 部署環境檢查..."
echo ""

# 1. 檢查系統
echo "🔍 檢查系統信息..."
DISTRO=$(lsb_release -si)
VERSION=$(lsb_release -sr)
echo "  系統: $DISTRO $VERSION"

if [[ "$DISTRO" != "Ubuntu" ]]; then
    echo "⚠️  本腳本針對Ubuntu優化"
    echo "   其他系統可能需要調整"
fi

echo ""
echo "📦 更新系統..."
apt update > /dev/null 2>&1
apt upgrade -y > /dev/null 2>&1
echo "  ✅ 系統已更新"

echo ""
echo "📥 安裝依賴包..."

# Python 3
if ! command -v python3 &> /dev/null; then
    echo "  安裝 Python3..."
    apt install python3 python3-pip python3-venv -y > /dev/null 2>&1
fi
echo "  ✅ Python3: $(python3 --version)"

# Git
if ! command -v git &> /dev/null; then
    echo "  安裝 Git..."
    apt install git -y > /dev/null 2>&1
fi
echo "  ✅ Git: $(git --version | cut -d' ' -f3)"

# Screen (用於後台運行)
if ! command -v screen &> /dev/null; then
    echo "  安裝 Screen..."
    apt install screen -y > /dev/null 2>&1
fi
echo "  ✅ Screen已安裝"

# curl
if ! command -v curl &> /dev/null; then
    echo "  安裝 Curl..."
    apt install curl -y > /dev/null 2>&1
fi
echo "  ✅ Curl已安裝"

echo ""
echo "📁 設定項目目錄..."

# 建立部署目錄
if [ ! -d "/opt/discord-bot" ]; then
    mkdir -p /opt/discord-bot
    echo "  ✅ 建立 /opt/discord-bot"
else
    echo "  ℹ️  目錄已存在"
fi

cd /opt/discord-bot

echo ""
echo "📥 克隆代碼倉庫..."

# 克隆倉庫
if [ ! -d ".git" ]; then
    echo "  ⏳ 等待中... (第一次可能較慢)"
    git clone https://github.com/YOUR_GITHUB_USERNAME/taiwan-stock-predictor.git . 2>&1 | grep -v "^Cloning" | tail -5
    echo "  ✅ 代碼已克隆"
else
    echo "  ℹ️  更新現有代碼..."
    git pull > /dev/null 2>&1
    echo "  ✅ 代碼已更新"
fi

echo ""
echo "📦 安裝Python依賴..."

# 建立虛擬環境（可選）
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    echo "  ✅ 虛擬環境已建立"
else
    source venv/bin/activate
    echo "  ℹ️  使用現有虛擬環境"
fi

# 升級pip
pip install --upgrade pip > /dev/null 2>&1

# 安裝依賴
pip install -r requirements.txt > /dev/null 2>&1
echo "  ✅ 依賴已安裝"

echo ""
echo "📁 建立必要目錄..."

mkdir -p snapshots
mkdir -p logs
mkdir -p data

echo "  ✅ 目錄已建立"

echo ""
echo "🔐 檢查配置檔案..."

if [ ! -f "monitor_config.json" ]; then
    echo "  ⚠️  monitor_config.json 不存在"
    echo ""
    echo "  請在以下位置編輯配置:"
    echo "    nano /opt/discord-bot/monitor_config.json"
    echo ""
    echo "  必須配置:"
    echo "    - bot_token: 你的Discord Bot Token"
    echo "    - channel_id: 目標頻道ID"
    echo "    - targets: 監控目標清單"
else
    echo "  ✅ 配置檔案已存在"
    echo ""
    echo "  請確認以下項:"
    echo "    □ bot_token 已設定"
    echo "    □ channel_id 已設定"
    echo "    □ 至少有1個監控目標"
fi

echo ""
echo "🔄 設定自動啟動..."

# 建立systemd服務
cat > /etc/systemd/system/discord-bot.service << 'EOF'
[Unit]
Description=Discord Bot Monitor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/discord-bot
ExecStart=/opt/discord-bot/venv/bin/python3 /opt/discord-bot/discord_bot_monitor.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload > /dev/null 2>&1
echo "  ✅ Systemd服務已建立"

echo ""
echo "════════════════════════════════════════════════"
echo "✅ 部署完成！"
echo "════════════════════════════════════════════════"
echo ""

echo "📝 後續步驟:"
echo ""
echo "1️⃣  編輯配置檔:"
echo "   nano /opt/discord-bot/monitor_config.json"
echo ""
echo "   必須修改:"
echo "   - \"bot_token\": \"你的Bot Token\""
echo "   - \"channel_id\": \"你的頻道ID\""
echo ""

echo "2️⃣  測試執行:"
echo "   cd /opt/discord-bot"
echo "   source venv/bin/activate"
echo "   python3 discord_bot_monitor.py"
echo ""
echo "   按 Ctrl+C 停止測試"
echo ""

echo "3️⃣  啟用自動啟動:"
echo "   systemctl enable discord-bot"
echo "   systemctl start discord-bot"
echo ""

echo "4️⃣  檢查狀態:"
echo "   systemctl status discord-bot"
echo "   journalctl -u discord-bot -f"
echo ""

echo "5️⃣  在Discord驗證:"
echo "   在頻道輸入: !status"
echo "   Bot應該有回應"
echo ""

echo "📚 更多命令:"
echo "  systemctl restart discord-bot    # 重啟Bot"
echo "  systemctl stop discord-bot       # 停止Bot"
echo "  systemctl disable discord-bot    # 禁用自動啟動"
echo "  journalctl -u discord-bot -n 50  # 查看最近50行日誌"
echo ""

echo "════════════════════════════════════════════════"
echo "祝你部署順利！🚀"
echo "════════════════════════════════════════════════"
