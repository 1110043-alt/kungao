"""
使用 PyInstaller 打包為 EXE
"""

import os
import sys
import subprocess

def build_exe():
    """打包為 EXE"""
    
    # 安裝必要的包
    print("安裝依賴包...")
    packages = [
        "PyQt5",
        "playwright",
        "gspread",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
        "requests",
        "pyinstaller"
    ]
    
    for pkg in packages:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=False)
    
    # 安裝 Playwright 瀏覽器
    print("\n安裝 Playwright 瀏覽器...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
    
    # 構建 EXE
    print("\n開始構建 EXE...")
    
    exe_name = "Tixcraft_Auto_Register"
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

a = Analysis(
    ['tixcraft_auto_register_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt5',
        'gspread',
        'google.auth',
        'google.oauth2',
        'playwright',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open("build.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    # 運行 PyInstaller
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "build.spec", "--distpath", "dist"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"\n✓ EXE 已成功構建！")
        print(f"位置: dist/{exe_name}.exe")
        
        # 顯示輸出
        print(result.stdout)
    else:
        print(f"\n✗ 構建失敗!")
        print(result.stderr)
        return False
    
    return True


if __name__ == "__main__":
    os.chdir(r"c:\Users\USER\Desktop\taiwan-stock-predictor")
    build_exe()
