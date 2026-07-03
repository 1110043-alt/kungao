    #!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🚀 台股預測儀表板 - 雲端部署專用啟動器
支援 Zeabur、Render、Heroku 等雲端平台

環境變數配置：
  • PORT: 服務器端口（預設 5555）
  • HOST: 監聽地址（預設 0.0.0.0）
  • DEBUG: 調試模式（預設 False）

使用方式：
  本地開發：
    DEBUG=true python cloud_ready_app.py
  
  生產部署（雲端平台自動使用）：
    python cloud_ready_app.py
"""

import os
import sys

def main():
    # 檢查依賴
    try:
        import flask
        from flask_cors import CORS
        import yfinance
        import waitress
    except ImportError as e:
        print(f"❌ 缺少依賴: {e}")
        print("請執行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 確認虛擬環境已激活
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  警告：虛擬環境未激活，建議先激活虛擬環境再運行")
    
    print("╔════════════════════════════════════════════════╗")
    print("║   🚀 台股預測儀表板 - 雲端部署應用         ║")
    print("╚════════════════════════════════════════════════╝")
    print()
    
    # 讀取環境變數
    port = int(os.environ.get('PORT', 5555))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    environment = 'development' if debug else 'production'
    
    print(f"📊 運行配置:")
    print(f"   • 環境: {environment.upper()}")
    print(f"   • Host: {host}")
    print(f"   • Port: {port}")
    print(f"   • Debug: {debug}")
    print()
    
    # 載入 Flask app
    from simple_app import app
    
    if debug:
        print("🔧 使用 Flask 開發服務器")
        print("   (自動重載已啟用)")
        app.run(debug=True, host=host, port=port)
    else:
        print("⚙️  使用 Waitress 生產服務器")
        print("   (高性能、多線程)")
        from waitress import serve
        print()
        print("═" * 48)
        print()
        serve(app, host=host, port=port, _quiet=False)

if __name__ == '__main__':
    main()
