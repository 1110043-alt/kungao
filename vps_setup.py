#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🖥️ VPS部署交互式配置器
幫助用戶快速配置并部署Bot到VPS
"""

import json
import os
import sys
import subprocess
from pathlib import Path

class VPSConfigurator:
    def __init__(self):
        self.config_file = "monitor_config.json"
        self.config = self.load_config()
    
    def load_config(self):
        """加載現有配置或建立新配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self.create_default_config()
    
    def create_default_config(self):
        """建立預設配置"""
        return {
            "bot_token": "",
            "channel_id": "",
            "check_interval": 30,
            "targets": [],
            "snapshot_dir": "snapshots"
        }
    
    def print_header(self):
        """打印標題"""
        print("\n")
        print("╔════════════════════════════════════════════╗")
        print("║      🖥️  VPS部署交互式配置器              ║")
        print("║      Discord Bot 24/7 監控設定            ║")
        print("╚════════════════════════════════════════════╝")
        print()
    
    def get_bot_token(self):
        """獲取Bot Token"""
        print("📌 第1步: Bot Token")
        print()
        print("獲取方法:")
        print("  1. 訪問 https://discord.com/developers/applications")
        print("  2. 選擇你的應用")
        print("  3. 左側 Bot → Copy TOKEN")
        print()
        
        while True:
            token = input("輸入你的Discord Bot Token: ").strip()
            if token and len(token) > 20:
                self.config["bot_token"] = token
                print(f"✅ Token已保存 (前15位: {token[:15]}...)")
                return
            else:
                print("❌ Token無效，請重試")
    
    def get_channel_id(self):
        """獲取頻道ID"""
        print()
        print("📌 第2步: 頻道ID")
        print()
        print("獲取方法:")
        print("  1. 在Discord開啟開發者模式 (用戶設定 → 進階 → 開發者模式)")
        print("  2. 右鍵點擊頻道 → 複製頻道ID")
        print()
        
        while True:
            channel_id = input("輸入頻道ID: ").strip()
            if channel_id.isdigit() and len(channel_id) > 10:
                self.config["channel_id"] = channel_id
                print(f"✅ 頻道ID已保存: {channel_id}")
                return
            else:
                print("❌ 頻道ID無效，請重試")
    
    def get_check_interval(self):
        """獲取檢查間隔"""
        print()
        print("📌 第3步: 監控間隔")
        print()
        print("檢查頻率 (秒數):")
        print("  • 10 - 非常頻繁 (消耗資源多)")
        print("  • 30 - 平衡 (推薦)")
        print("  • 60 - 低頻率 (節省資源)")
        print("  • 300 - 很低頻率 (5分鐘)")
        print()
        
        while True:
            interval = input("輸入間隔秒數 (預設30): ").strip()
            if not interval:
                interval = 30
            
            try:
                interval = int(interval)
                if 5 <= interval <= 3600:
                    self.config["check_interval"] = interval
                    print(f"✅ 間隔已設定: 每 {interval} 秒檢查一次")
                    return
                else:
                    print("❌ 請輸入 5-3600 之間的數字")
            except ValueError:
                print("❌ 請輸入有效的數字")
    
    def add_target(self):
        """添加監控目標"""
        print()
        print("📌 第4步: 監控目標")
        print()
        
        if self.config["targets"]:
            print("現有目標:")
            for i, target in enumerate(self.config["targets"], 1):
                print(f"  {i}. {target.get('name', '未命名')} - {target.get('url', '')}")
            print()
            
            modify = input("修改現有目標? (y/n): ").strip().lower()
            if modify != 'y':
                print("✅ 保持現有目標")
                return
        
        print("輸入監控目標信息:")
        print()
        
        while True:
            name = input("目標名稱 (如 Tixcraft): ").strip()
            if not name:
                print("❌ 名稱不能為空")
                continue
            
            url = input("網址 (如 https://...): ").strip()
            if not url.startswith("http"):
                print("❌ 網址必須以 http 或 https 開頭")
                continue
            
            selector = input("CSS選擇器 (如 .ticket-status, #countdown): ").strip()
            if not selector:
                print("❌ 選擇器不能為空")
                continue
            
            target = {
                "name": name,
                "url": url,
                "selector": selector
            }
            
            self.config["targets"].append(target)
            print(f"✅ 已添加目標: {name}")
            
            another = input("添加另一個目標? (y/n): ").strip().lower()
            if another != 'y':
                break
        
        print(f"✅ 共 {len(self.config['targets'])} 個監控目標")
    
    def save_config(self):
        """保存配置到JSON"""
        print()
        print("💾 保存配置...")
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"✅ 配置已保存到 {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ 保存失敗: {e}")
            return False
    
    def display_summary(self):
        """顯示配置摘要"""
        print()
        print("════════════════════════════════════════════")
        print("📋 配置摘要")
        print("════════════════════════════════════════════")
        print()
        
        print(f"Bot Token:        {self.config.get('bot_token', '')[:15]}...")
        print(f"頻道ID:           {self.config.get('channel_id', '')}")
        print(f"檢查間隔:          {self.config.get('check_interval', 30)} 秒")
        print()
        
        print(f"監控目標 ({len(self.config.get('targets', []))}):")
        for target in self.config.get("targets", []):
            print(f"  • {target.get('name', '未命名')}")
            print(f"    {target.get('url', '')}")
            print(f"    選擇器: {target.get('selector', '')}")
            print()
    
    def show_next_steps(self):
        """顯示下一步操作"""
        print()
        print("════════════════════════════════════════════")
        print("🚀 後續步驟")
        print("════════════════════════════════════════════")
        print()
        
        print("1️⃣  在VPS上執行部署腳本:")
        print("   chmod +x vps_deploy.sh")
        print("   sudo ./vps_deploy.sh")
        print()
        
        print("2️⃣  啟動Bot:")
        print("   systemctl start discord-bot")
        print()
        
        print("3️⃣  檢查狀態:")
        print("   systemctl status discord-bot")
        print("   journalctl -u discord-bot -f")
        print()
        
        print("4️⃣  在Discord驗證:")
        print("   在頻道輸入: !status")
        print()
        
        print("5️⃣  其他命令:")
        print("   !list-targets          # 列表目標")
        print("   !check-now             # 立即檢查")
        print("   !set-interval 60       # 改間隔")
        print()
    
    def run(self):
        """運行配置器"""
        self.print_header()
        
        try:
            self.get_bot_token()
            self.get_channel_id()
            self.get_check_interval()
            self.add_target()
            
            self.display_summary()
            
            confirm = input("\n保存配置? (y/n): ").strip().lower()
            if confirm == 'y':
                if self.save_config():
                    self.show_next_steps()
                    print("✅ 配置完成！")
                    print()
                    return 0
            else:
                print("❌ 配置已取消")
                return 1
        
        except KeyboardInterrupt:
            print("\n\n❌ 配置已中止")
            return 1
        except Exception as e:
            print(f"\n❌ 發生錯誤: {e}")
            return 1

if __name__ == "__main__":
    configurator = VPSConfigurator()
    sys.exit(configurator.run())
