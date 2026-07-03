@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║      🖥️  VPS部署準備工具                  ║
echo ║      幫助你準備VPS上傳檔案                ║
echo ╚════════════════════════════════════════════╝
echo.

echo 📋 檢查必要檔案...
echo.

REM 檢查Python檔案
echo 檢查Python檔案:
if exist "discord_bot_monitor.py" (
    echo   ✅ discord_bot_monitor.py
) else (
    echo   ❌ 缺少 discord_bot_monitor.py
)

if exist "web_monitor.py" (
    echo   ✅ web_monitor.py
) else (
    echo   ❌ 缺少 web_monitor.py
)

if exist "discord_notifier.py" (
    echo   ✅ discord_notifier.py
) else (
    echo   ❌ 缺少 discord_notifier.py
)

REM 檢查配置檔
echo.
echo 檢查配置檔:
if exist "monitor_config.json" (
    echo   ✅ monitor_config.json
) else (
    echo   ❌ 缺少 monitor_config.json
)

if exist "requirements.txt" (
    echo   ✅ requirements.txt
) else (
    echo   ❌ 缺少 requirements.txt
)

REM 檢查部署檔
echo.
echo 檢查部署檔:
if exist "vps_deploy.sh" (
    echo   ✅ vps_deploy.sh
) else (
    echo   ❌ 缺少 vps_deploy.sh
)

if exist "Dockerfile.monitor" (
    echo   ✅ Dockerfile.monitor
) else (
    echo   ❌ 缺少 Dockerfile.monitor
)

echo.
echo ════════════════════════════════════════════
echo.

echo 📝 VPS部署清單:
echo.
echo 1️⃣  購買VPS
echo   推薦: Linode (https://www.linode.com/)
echo   配置: Ubuntu 20.04 LTS, 1GB RAM, $5/月
echo   位置: Tokyo (東京)
echo.

echo 2️⃣  記下VPS信息
echo   □ VPS IP地址
echo   □ Root密碼
echo.

echo 3️⃣  SSH連接VPS
echo   Windows PowerShell:
echo     ssh root@你的VPS_IP
echo   Mac/Linux:
echo     ssh root@你的VPS_IP
echo.

echo 4️⃣  上傳部署檔到VPS
echo   選項A - 通過SCP上傳:
echo     scp vps_deploy.sh root@你的VPS_IP:/root/
echo     scp -r . root@你的VPS_IP:/root/discord-bot/
echo.
echo   選項B - Git克隆:
echo     git clone https://你的倉庫 /opt/discord-bot
echo.

echo 5️⃣  在VPS執行部署
echo   chmod +x /root/vps_deploy.sh
echo   sudo /root/vps_deploy.sh
echo.

echo 6️⃣  配置Bot
echo   nano /opt/discord-bot/monitor_config.json
echo   修改 bot_token 和 channel_id
echo.

echo 7️⃣  啟動Bot
echo   systemctl start discord-bot
echo   systemctl status discord-bot
echo.

echo 8️⃣  驗證
echo   在Discord輸入: !status
echo.

echo ════════════════════════════════════════════
echo.

echo 🚀 快速步驟:
echo.
echo 1. Python vps_setup.py      # 交互式配置
echo 2. git add . && git commit  # 上傳代碼
echo 3. git push origin main     # 推送到GitHub
echo 4. 購買VPS (Linode $5/月)
echo 5. SSH連接 VPS
echo 6. 執行 vps_deploy.sh
echo 7. 在Discord測試 !status
echo.

echo ════════════════════════════════════════════
echo.

echo 📚 文檔:
echo   □ VPS_PURCHASE_GUIDE.md     - 購買和部署指南
echo   □ VPS_QUICK_START.md        - 快速開始
echo   □ SERVER_DEPLOYMENT_GUIDE.md - 伺服器部署
echo.

echo 準備好了嗎？(按任意鍵繼續)
pause >nul

echo.
echo 🎉 開始部署!
echo.

REM 提示配置
echo 建議按此順序操作:
echo.
echo 1️⃣  配置Bot:
echo      python vps_setup.py
echo.
echo 2️⃣  上傳到GitHub:
echo      git add .
echo      git commit -m "VPS deployment ready"
echo      git push origin main
echo.
echo 3️⃣  購買VPS (Linode):
echo      https://www.linode.com/
echo.
echo 4️⃣  連接VPS並部署:
echo      ssh root@你的VPS_IP
echo      curl -O https://raw.githubusercontent.com/用戶名/台股預測/main/vps_deploy.sh
echo      chmod +x vps_deploy.sh
echo      sudo ./vps_deploy.sh
echo.
echo 5️⃣  在Discord驗證:
echo      !status
echo.

echo.
echo ════════════════════════════════════════════
echo 準備完成！🚀 開始購買VPS並部署吧！
echo ════════════════════════════════════════════
echo.

pause
