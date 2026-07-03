#!/usr/bin/env python3
"""
簡單的公網隧道代理 - 用於暴露本地服務到公網
"""

import requests
import json
import time

# 使用 Localtunnel 或類似服務
def create_tunnel():
    """建立公網隧道"""
    import subprocess
    import platform
    
    local_url = "http://127.0.0.1:8080"
    
    print("🌍 建立公網隧道...")
    print(f"📍 本地服務: {local_url}")
    
    try:
        # 嘗試使用 pyngrok
        from pyngrok import ngrok
        
        # 不需要認證的替代方案
        print("❌ ngrok 需要認證")
        print("\n💡 替代方案:")
        print("1️⃣  使用 Cloudflare Tunnel:")
        print("   下載: https://developers.cloudflare.com/cloudflare-one/connections/connect-applications/install-and-setup/tunnel-guide/local-management/as-a-service/windows/")
        print("   運行: cloudflared tunnel --url http://127.0.0.1:8080")
        print("\n2️⃣  使用 localtunnel (Node.js):")
        print("   npm install -g localtunnel")
        print("   lt --port 8080")
        print("\n3️⃣  使用本機 IP 直接訪問:")
        print("   http://192.168.0.110:8080")
        
    except ImportError:
        print("❌ pyngrok 未安裝")
        print("\n如需公網訪問，請選擇上述任一方案")

if __name__ == "__main__":
    create_tunnel()
