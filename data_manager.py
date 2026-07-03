# -*- coding: utf-8 -*-
"""
股票數據管理工具 - 簡單 Web 界面編輯 stock_data.json
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'stock_data.json')

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('data_manager_new.html')

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    data = load_data()
    return jsonify(data['stocks'])

@app.route('/api/stocks/<code>', methods=['PUT'])
def update_stock(code):
    data = load_data()
    stocks = data['stocks']
    stock = next((s for s in stocks if s['code'] == code), None)
    
    if not stock:
        return jsonify({"error": "Stock not found"}), 404
    
    update_data = request.json
    stock.update(update_data)
    save_data(data)
    
    return jsonify(stock)

@app.route('/api/stocks', methods=['POST'])
def add_stock():
    data = load_data()
    new_stock = request.json
    data['stocks'].append(new_stock)
    save_data(data)
    
    return jsonify(new_stock), 201

@app.route('/api/stocks/<code>', methods=['DELETE'])
def delete_stock(code):
    data = load_data()
    stocks = data['stocks']
    data['stocks'] = [s for s in stocks if s['code'] != code]
    save_data(data)
    
    return jsonify({"message": "Deleted"})

if __name__ == '__main__':
    print("📊 股票數據管理工具啟動")
    print("📍 訪問: http://localhost:8081")
    app.run(host='localhost', port=8081, debug=True)
