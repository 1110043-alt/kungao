#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速更新股票價格 - 使用 yfinance"""

import json
import yfinance as yf
from datetime import datetime
import os

STOCK_DATA_FILE = 'stock_data.json'

STOCK_CODES = {
    "2330": "2330.TW",
    "2454": "2454.TW",
    "2317": "2317.TW",
    "2884": "2884.TW",
    "2412": "2412.TW",
    "2886": "2886.TW",
    "1101": "1101.TW",
    "3008": "3008.TW",
    "8299": "8299.TW",
    "2376": "2376.TW",
    "3037": "3037.TW",
    "2211": "2211.TW",
    "2344": "2344.TW",
    "0050": "0050.TW",
}

def update_stocks():
    """更新所有股票的實時價格"""
    print("[UPDATING] 正在從 Yahoo Finance 獲取最新數據...")
    
    # 讀取現有數據
    with open(STOCK_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated = 0
    failed = 0
    
    for stock in data['stocks']:
        code = stock['code']
        if code not in STOCK_CODES:
            continue
        
        try:
            yahoo_code = STOCK_CODES[code]
            ticker = yf.Ticker(yahoo_code)
            hist = ticker.history(period='5d')
            
            if len(hist) > 0:
                current_price = float(hist['Close'].iloc[-1])
                prev_close = float(hist['Close'].iloc[0])
                day_change_pct = round((current_price - prev_close) / prev_close * 100, 2)
                
                stock['current_price'] = round(current_price, 2)
                stock['day_change_pct'] = day_change_pct
                stock['updated_at'] = datetime.now().isoformat()
                
                print(f"[OK] {code} {stock['name']}: NT${current_price:.2f} ({day_change_pct:+.2f}%)")
                updated += 1
            else:
                print(f"[SKIP] {code} {stock['name']}: 無數據")
                failed += 1
        except Exception as e:
            print(f"[ERROR] {code} {stock['name']}: {str(e)[:50]}")
            failed += 1
    
    # 保存更新
    with open(STOCK_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[SUCCESS] 更新完成! 成功: {updated}, 失敗: {failed}")

if __name__ == '__main__':
    try:
        update_stocks()
    except Exception as e:
        print(f"[ERROR] {str(e)}")
