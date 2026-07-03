@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════╗
echo ║   🌐 24小時網頁變化監控 - 快速設定    ║
echo ║      將網頁變化通知到你的Discord       ║
echo ╚════════════════════════════════════════╝
echo.

REM 檢查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 找不到Python，請先安裝Python
    echo 下載: https://www.python.org
    pause
    exit /b 1
)

REM 安裝依賴
echo 📦 安裝依賴中...
pip install -r requirements.txt

REM 運行設定向導
echo.
echo 🚀 啟動設定向導...
echo.
python setup_monitor.py

if errorlevel 0 (
    echo.
    echo ✅ 設定完成！
    echo.
    echo 🔍 下一步:
    echo   1. 編輯 monitor_config.json 調整設定
    echo   2. 測試本地運行: python cloud_monitor_server.py
    echo   3. 部署到Zeabur (見CLOUD_MONITOR_GUIDE.md)
    echo.
)

pause
