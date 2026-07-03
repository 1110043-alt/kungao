#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成逼真的模擬股票數據"""

import json
import random
from datetime import datetime

STOCK_DATA_FILE = 'stock_data.json'

def simulate_price_change(current_price, volatility):
    """模擬現實的價格波動"""
    # 基於波動率的隨機變化
    change_pct = random.gauss(0, volatility / 2)
    new_price = current_price * (1 + change_pct / 100)
    return round(new_price, 2)

def simulate_moving_averages(current_price, ma_type):
    """模擬移動平均線"""
    # 基於當前價格的合理偏差
    deviation = random.gauss(0, 1)
    if ma_type == 'ma5':
        adjusted = current_price * (1 - deviation * 0.5 / 100)
    elif ma_type == 'ma10':
        adjusted = current_price * (1 - deviation * 1 / 100)
    elif ma_type == 'ma20':
        adjusted = current_price * (1 - deviation * 1.5 / 100)
    elif ma_type == 'ma50':
        adjusted = current_price * (1 - deviation * 2 / 100)
    else:  # ma200
        adjusted = current_price * (1 - deviation * 3 / 100)
    
    return round(adjusted, 2)

def update_with_simulated_data():
    """使用模擬數據更新股票"""
    print("[UPDATING] 生成逼真的模擬股票數據...")
    
    with open(STOCK_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for stock in data['stocks']:
        # 獲取當前價格和波動率
        current = stock['current_price']
        volatility = stock.get('volatility', 2.0)
        
        # 模擬新的價格
        new_price = simulate_price_change(current, volatility)
        
        # 計算漲跌幅（基於前一日數據）
        prev_price = current * (1 - stock.get('day_change_pct', 0) / 100)
        day_change_pct = round((new_price - prev_price) / prev_price * 100, 2)
        
        # 更新移動平均線
        stock['current_price'] = new_price
        stock['day_change_pct'] = day_change_pct
        stock['ma5'] = simulate_moving_averages(new_price, 'ma5')
        stock['ma10'] = simulate_moving_averages(new_price, 'ma10')
        stock['ma20'] = simulate_moving_averages(new_price, 'ma20')
        stock['ma50'] = simulate_moving_averages(new_price, 'ma50')
        stock['ma200'] = simulate_moving_averages(new_price, 'ma200')
        
        # 模擬支撐/阻力
        stock['support'] = round(new_price * 0.95, 2)
        stock['resistance'] = round(new_price * 1.05, 2)
        
        # 模擬 RSI
        stock['rsi'] = round(random.gauss(50, 15), 2)
        
        # 模擬波動率
        stock['volatility'] = round(random.gauss(stock.get('volatility', 2), 0.5), 2)
        
        # 更新時間戳
        stock['updated_at'] = datetime.now().isoformat()
        
        print(f"[OK] {stock['code']} {stock['name']}: NT${new_price:.2f} ({day_change_pct:+.2f}%)")
    
    # 保存更新
    with open(STOCK_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[SUCCESS] 數據已更新至 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    random.seed()  # 隨機種子以獲得不同的結果
    update_with_simulated_data()
