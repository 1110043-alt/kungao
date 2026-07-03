#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""獨立前端服務器 - 生產級雲端部署配置"""

import http.server
import socketserver
import os
import json
import mimetypes
import urllib.request
import urllib.error
from pathlib import Path

# 🚀 環境變數配置（適合雲端平台）
PORT = int(os.environ.get('FRONTEND_PORT', 8888))
HOST = os.environ.get('FRONTEND_HOST', '127.0.0.1')
API_PORT = int(os.environ.get('API_PORT', 8080))
API_HOST = os.environ.get('API_HOST', '127.0.0.1')
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'templates')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')
API_BASE_URL = f'http://{API_HOST}:{API_PORT}'

class FrontendHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # 將目錄設置為 TEMPLATES_DIR，這樣可以服務 templates 下的文件
        super().__init__(*args, directory=TEMPLATES_DIR, **kwargs)
    
    def end_headers(self):
        """添加 CORS 和快取禁用頭"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_OPTIONS(self):
        """處理 CORS preflight 請求"""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """自定義日誌格式"""
        print(f"🌐 [{self.log_date_time_string()}] {format % args}")
    
    def translate_path(self, path):
        """翻譯請求路徑為實際文件路徑"""
        # 移除查詢字符串
        if '?' in path:
            path = path.split('?')[0]
        
        # 根目錄映射到 index.html
        if path == '/':
            path = '/index.html'
        
        # 處理 /static/ 路由：映射到項目根目錄的 static 目錄
        if path.startswith('/static/'):
            # 移除 /static 前綴，在項目根目錄的 static 目錄中尋找
            file_path = os.path.join(PROJECT_ROOT, path.lstrip('/'))
            return file_path
        
        # 其他文件在 templates 目錄中尋找
        file_path = os.path.join(TEMPLATES_DIR, path.lstrip('/'))
        return file_path
    
    def do_GET(self):
        """處理 GET 請求"""
        try:
            # 檢查是否是 API 請求，代理到 Flask
            if self.path.startswith('/api/'):
                return self.proxy_api_request()
            return super().do_GET()
        except Exception as e:
            print(f"❌ 錯誤: {e}")
            self.send_error(500)
    
    def proxy_api_request(self):
        """代理 API 請求到 Flask 服務器"""
        try:
            # 構建完整的 API URL
            api_path = self.path
            if '?' in api_path:
                api_path, query_string = api_path.split('?', 1)
                api_url = f'{API_BASE_URL}{api_path}?{query_string}'
            else:
                api_url = f'{API_BASE_URL}{api_path}'
            
            print(f"🔗 代理 API: {api_url}")
            
            # 發送請求到 Flask
            req = urllib.request.Request(api_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.status
                headers = response.headers
                data = response.read()
                
                # 返回響應
                self.send_response(status_code)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Content-Type', headers.get('Content-Type', 'application/json'))
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.send_header('Content-Length', len(data))
                self.end_headers()
                self.wfile.write(data)
                print(f"✅ API 響應成功: {status_code}")
        except urllib.error.URLError as e:
            print(f"❌ API 連接失敗: {e}")
            self.send_error(502, f"Bad Gateway: {e}")
        except Exception as e:
            print(f"❌ 代理錯誤: {e}")
            self.send_error(500)

def run_server():
    """啟動前端服務器"""
    try:
        with socketserver.TCPServer((HOST, PORT), FrontendHandler) as httpd:
            print("╔════════════════════════════════════════════════╗")
            print("║   🌐 前端服務器已啟動 (雲端就緒配置)         ║")
            print("╚════════════════════════════════════════════════╝")
            print()
            print(f"📍 前端地址: http://127.0.0.1:{PORT}/ (本地)")
            print(f"📍 LAN 地址: http://192.168.0.17:{PORT}/ (局域網)")
            print()
            print("⚙️  配置信息:")
            print(f"  • 前端服務器監聽: {HOST}:{PORT}")
            print(f"  • 靜態文件目錄: {TEMPLATES_DIR}")
            print(f"  • 已啟用 CORS (跨域請求)")
            print(f"  • 已啟用快取禁用 (自動刷新)")
            print(f"  • 環境變數: FRONTEND_PORT={PORT}, FRONTEND_HOST={HOST}")
            print()
            print("💡 快捷提示:")
            print("  • 按 Ctrl+C 可停止服務器")
            print("  • 修改 HTML/CSS/JS 後無需重啟，直接刷新瀏覽器")
            print("  • 雲端部署時自動讀取環境變數 PORT 和 HOST")
            print()
            print("🔄 啟動 Flask API 服務器 (新視窗)...")
            
            # 啟動 Flask API（可選）
            import subprocess
            import sys
            subprocess.Popen(
                [sys.executable, "simple_app.py"],
                cwd=os.path.dirname(__file__),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            
            print("✅ Flask API 啟動中...")
            print()
            print("═" * 48)
            print()
            
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 48 or e.errno == 98:  # Port in use
            print(f"❌ 端口 {PORT} 被佔用！")
            print(f"請運行以下命令釋放端口:")
            print(f"  Windows: netstat -ano | findstr :{PORT}")
            print(f"  然後: taskkill /PID <PID> /F")
        else:
            print(f"❌ 錯誤: {e}")
    except KeyboardInterrupt:
        print("\n✅ 服務器已停止")

if __name__ == '__main__':
    run_server()
