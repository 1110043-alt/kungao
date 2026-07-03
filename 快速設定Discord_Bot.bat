@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════╗
echo ║   🤖 Discord Bot 監控 - 快速設定      ║
echo ║     建立自己的Bot，經營伺服器監控      ║
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
echo 🚀 啟動Bot設定向導...
echo.
python setup_discord_bot.py

if errorlevel 0 (
    echo.
    echo ✅ 設定完成！
    echo.
    echo 🔍 下一步:
    echo   1. 查看 monitor_config.json 確認設定
    echo   2. 測試Bot運行: python discord_bot_monitor.py
    echo   3. 在Discord頻道輸入 !status 檢查
    echo   4. 查看 DISCORD_BOT_GUIDE.md 瞭解命令
    echo.
)

pause
