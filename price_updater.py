# -*- coding: utf-8 -*-
"""
台股實時價格更新器 - 每 10 秒從 Yahoo Finance 拉取最新價格
"""
import os
import json
import time
import threading
import yfinance as yf
from datetime import datetime

STOCK_DATA_FILE = os.path.join(os.path.dirname(__file__), 'stock_data.json')

# 股票代碼對應
STOCK_CODES = {
    "2330": "2330.TW",  # 台積電
    "2454": "2454.TW",  # 聯發科
    "2317": "2317.TW",  # 鴻海
    "2884": "2884.TW",  # 玉山金
    "2412": "2412.TW",  # 中華電
    "2886": "2886.TW",  # 兆豐金
    "1101": "1101.TW",  # 台泥
    "3008": "3008.TW",  # 大立光
    "8299": "8299.TW",  # 群聯
    "2376": "2376.TW",  # 技嘉
    "3037": "3037.TW",  # 欣興
    "2211": "2211.TW",  # 華通
    "2344": "2344.TW",  # 華邦電
    "0050": "0050.TW",  # 元大台灣50
}

def get_stock_data_from_yahoo(ticker_code):
    """從 Yahoo Finance 獲取股票數據"""
    try:
        ticker = yf.Ticker(ticker_code)
        data = ticker.history(period='1d')
        
        if data.empty:
            return None
        
        # 獲取最新價格
        current_price = float(data['Close'].iloc[-1])
        
        # 獲取前一日收盤價
        try:
            prev_data = ticker.history(period='5d')
            if len(prev_data) > 1:
                prev_close = float(prev_data['Close'].iloc[-2])
            else:
                prev_close = current_price
        except:
            prev_close = current_price
        
        # 計算漲跌幅
        day_change_pct = round(((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0, 2)
        
        return {
            "current_price": round(current_price, 2),
            "day_change_pct": day_change_pct,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ 獲取 {ticker_code} 數據失敗: {str(e)}")
        return None

def load_stock_data():
    """讀取本地股票數據"""
    try:
        with open(STOCK_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 讀取數據文件失敗: {str(e)}")
        return {"stocks": []}

def save_stock_data(data):
    """保存股票數據到本地"""
    try:
        with open(STOCK_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存數據文件失敗: {str(e)}")
        return False

def update_prices():
    """更新所有股票價格"""
    print(f"[UPDATING] [{datetime.now().strftime('%H:%M:%S')}] 開始更新股票價格...")
    
    # 讀取現有數據
    data = load_stock_data()
    stocks = data.get('stocks', [])
    
    updated_count = 0
    failed_count = 0
    
    # 更新每支股票
    for stock in stocks:
        code = stock.get('code')
        if code not in STOCK_CODES:
            continue
        
        yahoo_code = STOCK_CODES[code]
        new_data = get_stock_data_from_yahoo(yahoo_code)
        
        if new_data:
            stock['current_price'] = new_data['current_price']
            stock['day_change_pct'] = new_data['day_change_pct']
            stock['updated_at'] = new_data['timestamp']
            updated_count += 1
            print(f"   [OK] {code} {stock.get('name', code)}: NT${new_data['current_price']} ({new_data['day_change_pct']:+.2f}%)")
        else:
            failed_count += 1
            print(f"   [FAIL] {code} {stock.get('name', code)}: 更新失敗，保留現有價格")
    
    # 保存更新後的數據
    if save_stock_data(data):
        print(f"[SUCCESS] 更新完成！成功: {updated_count}, 失敗: {failed_count}\n")
    else:
        print(f"[ERROR] 數據保存失敗\n")

def start_auto_updater(interval=10):
    """啟動自動更新線程"""
    def run_updater():
        print(f"🚀 價格自動更新器已啟動 (間隔: {interval} 秒)")
        print(f"📊 監控股票: {', '.join([f'{k}({v})' for k, v in list(STOCK_CODES.items())[:5]])}...")
        
        while True:
            try:
                update_prices()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n[STOPPED] 更新器已停止")
                break
            except Exception as e:
                print(f"[ERROR] 更新錯誤: {str(e)}")
                time.sleep(interval)
    
    # 啟動後台線程
    updater_thread = threading.Thread(target=run_updater, daemon=True)
    updater_thread.start()
    return updater_thread

if __name__ == '__main__':
    print("=" * 60)
    print("台股實時價格自動更新器")
    print("=" * 60)
    
    # 立即執行一次更新
    update_prices()
    
    # 啟動自動更新 (每 10 秒)
    start_auto_updater(interval=10)
    
    # 保持程序運行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n程序已停止")
