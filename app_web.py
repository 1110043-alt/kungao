#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台股預測儀表板 - 公網版本（用於 Zeabur 部署）
集成了 API 和靜態資源提供
"""

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
        # 支援兩種格式: 直接陣列或 {"stocks": [...]}
        STOCKS = data.get("stocks", data) if isinstance(data, dict) else data
except:
    STOCKS = []

# 移除不需要的股票代碼
EXCLUDED_CODES = {'3045'}  # 奇力新
STOCKS = [stock for stock in STOCKS if stock.get('code') not in EXCLUDED_CODES]

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
            # 模擬預測
            price = stock.get('current_price', 0)
            direction = random.choice(['📈 看漲', '📉 看跌'])
            confidence = random.randint(60, 95)
            
            return jsonify({
                'code': code,
                'name': stock.get('name', ''),
                'prediction': direction,
                'confidence': confidence,
                'target_price': round(price * (1 + random.uniform(-0.05, 0.05)), 2),
                'timestamp': datetime.now().isoformat()
            })
    return jsonify({'error': 'Stock not found'}), 404

@app.route('/api/market-status', methods=['GET'])
def market_status():
    """獲取市場狀態"""
    now = datetime.now()
    hour = now.hour
    
    # 判斷市場狀態
    if 9 <= hour < 13.5:  # 09:00 - 13:30
        status = 'open'
        status_text = '盤中'
    elif 13.5 <= hour < 15:  # 13:30 - 15:00
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

# ============ 靜態資源 ============
@app.route('/')
def index():
    """主頁 - 提供完整儀表板 HTML"""
    try:
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>台股預測儀表板</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial; text-align: center; margin-top: 50px; }
                h1 { color: #7c3aed; }
            </style>
        </head>
        <body>
            <h1>台股即時預測儀表板</h1>
            <p>正在加載...</p>
            <p><a href="/api/all-stocks">查看 API</a></p>
        </body>
        </html>
        '''

@app.route('/static/<path:path>')
def serve_static(path):
    """提供靜態文件"""
    static_dir = 'static'
    file_path = os.path.join(static_dir, path)
    
    if os.path.exists(file_path):
        if path.endswith('.js'):
            return send_file(file_path, mimetype='application/javascript')
        elif path.endswith('.css'):
            return send_file(file_path, mimetype='text/css')
        elif path.endswith('.json'):
            return send_file(file_path, mimetype='application/json')
        else:
            return send_file(file_path)
    
    return {'error': 'File not found'}, 404

# ============ 健康檢查 ============
@app.route('/health')
def health():
    """健康檢查端點"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'stocks_loaded': len(STOCKS)
    })

# ============ 啟動 ============
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
