@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════╗
echo ║   🚀 伺服器部署 - 快速部署工具        ║
echo ║      將Bot部署到雲端24/7運行          ║
echo ╚════════════════════════════════════════╝
echo.

REM 檢查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 找不到Python
    pause
    exit /b 1
)

REM 檢查部署就緒情況
echo 🔍 檢查部署就緒情況...
echo.
python check_deployment_ready.py

echo.
echo ╔════════════════════════════════════════╗
echo ║   📌 下一步                            ║
echo ╚════════════════════════════════════════╝
echo.
echo 1️⃣  確保代碼已上傳到GitHub:
echo    git add .
echo    git commit -m "Ready for deployment"
echo    git push origin main
echo.
echo 2️⃣  選擇部署平台:
echo    • Zeabur (推薦) https://zeabur.com/zh-TW
echo    • Railway https://railway.app
echo    • Replit https://replit.com
echo.
echo 3️⃣  按照 SERVER_DEPLOYMENT_GUIDE.md 部署
echo.
echo 4️⃣  在Discord輸入 !status 驗證
echo.

pause
