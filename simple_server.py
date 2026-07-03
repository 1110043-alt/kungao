#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超簡單 - 僅用 Python 內置 http.server，不依賴任何第三方
前端 + API 都在一個進程
"""

import http.server
import socketserver
import threading
import time
import json
import os
import webbrowser
from pathlib import Path

# ============ 前端配置 ============
FRONTEND_PORT = 9000
TEMPLATES_DIR = Path(__file__).parent / 'templates'

# ============ API 配置（簡化版）============
API_PORT = 5001
API_DATA = {
    "stocks": [
        {
            "code": "2330", "name": "台積電", "category": "電子/半導體",
            "current_price": 2410.0, "day_change_pct": 1.05,
            "ma5": 2376.0, "ma10": 2332.55, "ma20": 2329.67, "ma50": 2225.62, "ma200": 1711.26,
            "rsi": 60.52, "volatility": 2.13, "support": 2198.95, "resistance": 2445.68
        },
        {
            "code": "2454", "name": "聯發科", "category": "電子/半導體",
            "current_price": 1185.0, "day_change_pct": -0.84,
            "ma5": 1192.4, "ma10": 1198.2, "ma20": 1205.33, "ma50": 1150.5, "ma200": 920.5,
            "rsi": 45.3, "volatility": 1.95, "support": 1100.0, "resistance": 1250.0
        }
    ]
}

class SimpleAPIHandler(http.server.SimpleHTTPRequestHandler):
    """處理 API 請求"""
    def do_GET(self):
        if self.path == '/api/all-stocks':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(API_DATA["stocks"]).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"🔌 API [{self.log_date_time_string()}] {format % args}")

class SimpleFrontendHandler(http.server.SimpleHTTPRequestHandler):
    """處理前端請求"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(TEMPLATES_DIR), **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()
    
    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        return super().do_GET()
    
    def log_message(self, format, *args):
        print(f"🌐 前端 [{self.log_date_time_string()}] {format % args}")

def run_api_server():
    """在單獨線程運行 API"""
    with socketserver.TCPServer(("127.0.0.1", API_PORT), SimpleAPIHandler) as httpd:
        print(f"✅ API 服務器啟動 (Port {API_PORT})")
        httpd.serve_forever()

def run_frontend_server():
    """主線程運行前端"""
    with socketserver.TCPServer(("127.0.0.1", FRONTEND_PORT), SimpleFrontendHandler) as httpd:
        print(f"✅ 前端服務器啟動 (Port {FRONTEND_PORT})")
        
        # 打開瀏覽器
        time.sleep(1)
        webbrowser.open(f'http://127.0.0.1:{FRONTEND_PORT}/')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ 服務器已停止")

if __name__ == '__main__':
    print("╔════════════════════════════════════════════════╗")
    print("║   🚀 台股預測儀表板 - 超簡單版              ║")
    print("╚════════════════════════════════════════════════╝")
    print()
    
    # 啟動 API 服務器（後台線程）
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()
    time.sleep(1)
    
    print()
    print("📍 訪問地址:")
    print(f"   • 前端: http://127.0.0.1:{FRONTEND_PORT}/")
    print(f"   • API:  http://127.0.0.1:{API_PORT}/api/all-stocks")
    print()
    print("💡 提示:")
    print("   • 按 Ctrl+C 停止所有服務")
    print()
    
    # 運行前端服務器（主線程）
    run_frontend_server()
