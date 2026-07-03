@echo off
chcp 65001 >nul
title 🚀 台股預測儀表板 自動啟動器
echo 正在幫您啟動台股預測儀表板服務，請稍候...
echo.

:: 1. 自動切換到你的專案資料夾
cd /d "C:\Users\USER\Desktop\taiwan-stock-predictor"
if errorlevel 1 (
    echo ❌ 錯誤：無法切換到專案資料夾
    pause
    exit /b 1
)

:: 2. 設定通訊埠為 5555
set PORT=5555
set HOST=0.0.0.0

:: 3. 激活虛擬環境
call .\venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 錯誤：虛擬環境激活失敗
    pause
    exit /b 1
)

echo ✅ 虛擬環境已激活
echo 📍 服務將運行於 http://localhost:5555/
echo.

:: 4. 等待 2 秒再開啟瀏覽器（確保服務器準備好）
start /b python simple_app.py

timeout /t 2 /nobreak

:: 5. 自動在瀏覽器打開網頁
start http://localhost:5555/

:: 保持窗口開啟
pause