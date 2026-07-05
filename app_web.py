#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""台股預測儀表板 - Flask 後端 + 靜態前端"""

from flask import Flask, render_template_string, send_file, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import random

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# ============ 數據加載 ============
try:
    with open('stock_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        STOCKS = data.get('stocks', data) if isinstance(data, dict) else data
except:
    STOCKS = []

# ============ API 端點 ============
@app.route('/api/all-stocks', methods=['GET'])
def get_all_stocks():
    """獲取所有股票數據"""
    return jsonify(STOCKS)

@app.route('/api/stock/<code>', methods=['GET'])
def get_stock(code):
    """獲取單隻股票詳細數據"""
    for stock in STOCKS:
        if stock['code'] == code:
            return jsonify(stock)
    return jsonify({'error': 'Stock not found'}), 404

@app.route('/api/prediction/<code>', methods=['GET'])
def get_prediction(code):
    """獲取股票預測數據（模擬）"""
    for stock in STOCKS:
        if stock['code'] == code:
            price = stock.get('current_price', 0)
            direction = random.choice(['📈 看漲', '📉 看跌'])
            confidence = random.randint(60, 95)
            
            return jsonify({
                'code': code,
                'direction': direction,
                'confidence': confidence,
                'target_price': round(price * (1 + random.uniform(-0.1, 0.1)), 2),
                'timestamp': datetime.now().isoformat()
            })
    return jsonify({'error': 'Stock not found'}), 404

@app.route('/api/market-status', methods=['GET'])
def market_status():
    """獲取市場狀態"""
    now = datetime.now()
    hour = now.hour
    
    if 9 <= hour < 13.5:
        status = 'open'
        status_text = '盤中'
    elif 13.5 <= hour < 15:
        status = 'open'
        status_text = '午盤'
    else:
        status = 'closed'
        status_text = '休市'
    
    up_count = sum(1 for s in STOCKS if s.get('day_change_pct', 0) > 0)
    down_count = len(STOCKS) - up_count
    
    return jsonify({
        'status': status,
        'status_text': status_text,
        'up_count': up_count,
        'down_count': down_count,
        'timestamp': now.isoformat()
    })

@app.route('/api/top-stocks', methods=['GET'])
def get_top_stocks():
    """獲取表現最好的股票"""
    if not STOCKS:
        return jsonify([])
    
    sorted_stocks = sorted(STOCKS, key=lambda x: x.get('day_change_pct', 0), reverse=True)
    return jsonify(sorted_stocks[:5])

# ============ 靜態資源 ============
@app.route('/')
def index():
    """主頁 - 返回靜態 HTML"""
    try:
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return '''
        <html>
        <head><title>台股即時預測儀表板</title></head>
        <body><h1>儀表板正在加載...</h1></body>
        </html>
        '''

@app.route('/static/<path:path>')
def serve_static(path):
    """提供靜態文件"""
    return send_file(os.path.join('static', path))

@app.route('/health', methods=['GET'])
def health():
    """健康檢查"""
    return jsonify({
        'status': 'ok',
        'stocks_loaded': len(STOCKS),
        'timestamp': datetime.now().isoformat()
    })

# ============ 啟動 ============
if __name__ == '__main__':
    print(f"✅ 加載 {len(STOCKS)} 支股票")
    print("🚀 啟動 Flask 應用...")
    app.run(host='0.0.0.0', port=8080, debug=False)
