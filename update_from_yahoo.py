#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 Yahoo Finance 取得真實台股數據
支持自動更新 stock_data.json
"""

import yfinance as yf
import json
import os
from datetime import datetime

# 台股代碼
STOCKS = {
    "2330": "台積電",
    "2454": "聯發科", 
    "2317": "鴻海",
    "2884": "玉山金",
    "2886": "兆豐金",
    "1101": "台泥",
    "3008": "大立光",
    "8299": "群聯",
    "2376": "技嘉",
    "3037": "欣興",
    "2412": "中華電",
    "2211": "華通",
    "2344": "華邦電",
    "0050": "元大台灣50"
}

def get_stock_data():
    """從 Yahoo Finance 取得股票數據"""
    stocks_list = []
    
    for code, name in STOCKS.items():
        try:
            # Yahoo Finance 台灣股票代碼格式
            ticker_str = f"{code}.TW"
            print(f"獲取 {name} ({code})...", end=" ")
            
            ticker = yf.Ticker(ticker_str)
            
            # 獲取基本信息
            try:
                # 獲取最近 200 天數據用於技術指標計算
                history = ticker.history(period="200d")
                if history.empty or len(history) < 2:
                    print("❌ 無數據")
                    continue
                    
                current_price = float(history['Close'].iloc[-1])
                prev_close = float(history['Close'].iloc[-2])  # 前一日收盤價
                
                # 計算漲跌幅 (正確的計算方式)
                day_change = current_price - prev_close
                day_change_pct = (day_change / prev_close * 100) if prev_close != 0 else 0
                
                # 計算移動平均線
                ma5 = history['Close'].tail(5).mean()
                ma10 = history['Close'].tail(10).mean()
                ma20 = history['Close'].tail(20).mean()
                ma50 = history['Close'].tail(50).mean()
                ma200 = history['Close'].tail(200).mean()
                
                # 計算 RSI (14 期)
                delta = history['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs.iloc[-1])) if loss.iloc[-1] != 0 else 50
                
                # 計算支撐與阻力 (使用52周高低)
                high_52w = history['High'].tail(252).max()
                low_52w = history['Low'].tail(252).min()
                support = low_52w
                resistance = high_52w
                
                # 計算波動率 (日漲跌幅的標準差)
                volatility = history['Close'].pct_change().std() * 100
                
                stock_data = {
                    "code": code,
                    "name": name,
                    "current_price": round(current_price, 2),
                    "day_change_pct": round(day_change_pct, 2),
                    "rsi": round(rsi, 2),
                    "ma5": round(float(ma5), 2),
                    "ma10": round(float(ma10), 2),
                    "ma20": round(float(ma20), 2),
                    "ma50": round(float(ma50), 2),
                    "ma200": round(float(ma200), 2),
                    "support": round(float(support), 2),
                    "resistance": round(float(resistance), 2),
                    "volatility": round(volatility, 2),
                    "updated_at": datetime.utcnow().isoformat() + "Z"
                }
                
                stocks_list.append(stock_data)
                print(f"✅ {current_price} ({day_change_pct:+.2f}%)")
                
            except Exception as e:
                print(f"❌ 錯誤: {str(e)[:50]}")
                continue
                
        except Exception as e:
            print(f"❌ 連線錯誤: {str(e)[:50]}")
            continue
    
    return stocks_list

def save_to_json(stocks_list):
    """儲存到 stock_data.json"""
    if not stocks_list:
        print("❌ 沒有有效數據，中止保存")
        return False
        
    data = {"stocks": stocks_list}
    
    json_file = "stock_data.json"
    
    # 先備份
    if os.path.exists(json_file):
        os.system(f"copy {json_file} {json_file}.bak > nul")
        print(f"✅ 備份舊文件: {json_file}.bak")
    
    # 保存新數據
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存: {json_file}")
        return True
    except Exception as e:
        print(f"❌ 保存失敗: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 台股實時數據更新程序")
    print("=" * 60)
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("1️⃣  正在從 Yahoo Finance 取得數據...")
    stocks_data = get_stock_data()
    
    print()
    print(f"2️⃣  取得 {len(stocks_data)} 支股票的數據")
    
    if stocks_data:
        if save_to_json(stocks_data):
            print()
            print("=" * 60)
            print("✅ 更新完成！")
            print("=" * 60)
        else:
            print("❌ 保存失敗")
    else:
        print("❌ 無法取得任何數據")
