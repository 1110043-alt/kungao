"""
快速啟動 Tixcraft 自動註冊 GUI 應用
直接執行此文件即可啟動應用
"""

import subprocess
import sys
import os

def install_requirements():
    """安裝依賴"""
    print("正在安裝依賴包...")
    
    requirements = [
        "PyQt5>=5.15.0",
        "playwright>=1.40.0",
        "gspread>=5.10.0",
        "google-auth-oauthlib>=1.0.0",
        "google-auth-httplib2>=0.2.0",
        "google-api-python-client>=2.0.0",
        "requests>=2.28.0"
    ]
    
    for req in requirements:
        print(f"  安裝 {req}...")
        subprocess.run([sys.executable, "-m", "pip", "install", req, "-q"], check=False)
    
    print("✓ 依賴安裝完成！\n")

def run_app():
    """執行應用"""
    os.chdir(r"c:\Users\USER\Desktop\taiwan-stock-predictor")
    
    print("=" * 60)
    print("  Tixcraft 自動註冊工具 v1.0")
    print("=" * 60)
    
    # 嘗試導入所需模塊
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5 已安裝")
    except ImportError:
        print("⚠ PyQt5 未安裝，正在安裝...")
        install_requirements()
    
    # 啟動應用
    print("\n啟動應用...\n")
    
    try:
        from tixcraft_auto_register_gui import TixcraftGUI
        import sys
        
        app = QApplication(sys.argv)
        window = TixcraftGUI()
        window.show()
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"啟動失敗: {e}")
        print("\n嘗試安裝所有依賴...")
        install_requirements()
        print("請重新運行此腳本")

if __name__ == "__main__":
    run_app()
