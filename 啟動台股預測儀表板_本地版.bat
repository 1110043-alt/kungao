@echo off
chcp 65001 >nul
color 0B
title 台股預測儀表板 - 本地數據版

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                 台股預測儀表板啟動中...                    ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

cd /d "c:\Users\USER\Desktop\taiwan-stock-predictor"

REM 檢查虛擬環境
if not exist ".venv\Scripts\activate.bat" (
    echo ⚠️  虛擬環境不存在，正在創建...
    python -m venv .venv
)

REM 啟用虛擬環境
call .venv\Scripts\activate.bat

REM 安裝依賴
echo 📦 檢查依賴...
pip install flask flask-cors -q

REM 設定 UTF-8 編碼
set PYTHONIOENCODING=utf-8

echo.
echo ✅ 啟動完成！
echo.
echo 📊 主儀表板: http://localhost:8080
echo 🛠️  數據管理: http://localhost:8081
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  啟動方式:                                                 ║
echo ║  1. 主預測儀表板 (已啟動下面):                              ║
echo ║     python simple_app.py                                  ║
echo ║                                                            ║
echo ║  2. 數據管理工具 (另開終端執行):                            ║
echo ║     python data_manager.py                                ║
echo ║                                                            ║
echo ║  Ctrl+C 停止服務                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

python simple_app.py
