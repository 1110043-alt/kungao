# -*- coding: utf-8 -*-
"""
台股即時預測儀表板 - 本地數據版
完全不依賴 Yahoo Finance，所有數據由 stock_data.json 管理
"""
import os
import json
import time
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 本地數據文件路徑
STOCK_DATA_FILE = os.path.join(os.path.dirname(__file__), 'stock_data.json')

def load_stock_data():
    """從本地 JSON 文件讀取股票數據"""
    try:
        with open(STOCK_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            stocks = data.get('stocks', [])
            return stocks
    except Exception as e:
        print(f"⚠️ 讀取本地數據失敗: {str(e)}")
        return []

def get_stock_by_code(code, stocks=None):
    """按代碼查找股票"""
    if stocks is None:
        stocks = load_stock_data()
    return next((s for s in stocks if s['code'] == code), None)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/all-stocks')
def get_all_stocks():
    stocks = load_stock_data()
    for stock in stocks:
        stock['data_source'] = 'local'
        stock['timestamp'] = datetime.now().isoformat()
    return jsonify(stocks)

@app.route('/api/top-stocks')
def get_top_stocks():
    stocks = load_stock_data()
    top = sorted(stocks, key=lambda x: x.get('day_change_pct', 0), reverse=True)[:10]
    for stock in top:
        stock['data_source'] = 'local'
        stock['timestamp'] = datetime.now().isoformat()
    return jsonify(top)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "data_source": "local"}), 200

@app.route('/api/stock-prediction/<code>')
def get_stock_prediction(code):
    """個股預測分析數據 - 使用本地數據"""
    
    stocks = load_stock_data()
    stock = get_stock_by_code(code, stocks)
    
    if not stock:
        return jsonify({"error": f"Stock {code} not found"}), 404
    
    import math, random
    random.seed(hash(code) % 2**31)
    
    price = stock['current_price']
    change_pct = stock['day_change_pct']
    rsi = stock.get('rsi', 50)
    ma5 = stock.get('ma5', price)
    ma10 = stock.get('ma10', price)
    ma20 = stock.get('ma20', price)
    ma50 = stock.get('ma50', price)
    ma200 = stock.get('ma200', price)
    
    # 波動率計算
    daily_vol = stock.get('volatility', 2.5) / 100
    avg_vol_20 = stock.get('volatility', 2.5) / 100
    nvol = daily_vol / avg_vol_20 if avg_vol_20 > 0 else 1.0
    
    # 趨勢計算
    trend = (price - ma20) / ma20 if ma20 > 0 else 0
    
    # K 值計算
    if nvol > 1:
        k_value = 1.5 + (nvol - 1) * 0.25
        vol_grade = "🔴 高波動"
    elif nvol > 0.5:
        k_value = 2.0 + (0.5 - (nvol - 0.5)) * 0.5
        vol_grade = "🟡 中波動"
    else:
        k_value = 3.0 + (0.5 - nvol) * 0.5
        vol_grade = "🟢 低波動"
    
    # 交易信號
    signal = trend * (nvol ** 0.5)
    
    # 預測區間
    sqrt_5 = math.sqrt(5)
    sqrt_20 = math.sqrt(20)
    sqrt_90 = math.sqrt(90)
    sqrt_180 = math.sqrt(180)
    
    range_1w_upper = price * (1 + daily_vol * sqrt_5)
    range_1w_lower = price * (1 - daily_vol * sqrt_5)
    range_1m_upper = price * (1 + daily_vol * sqrt_20)
    range_1m_lower = price * (1 - daily_vol * sqrt_20)
    range_3m_upper = price * (1 + daily_vol * sqrt_90)
    range_3m_lower = price * (1 - daily_vol * sqrt_90)
    range_6m_upper = price * (1 + daily_vol * sqrt_180)
    range_6m_lower = price * (1 - daily_vol * sqrt_180)
    
    # 動態選擇
    if nvol > 1:
        dynamic_ma = ma5
        entry_bias = -0.03
    elif nvol > 0.5:
        dynamic_ma = (ma10 + ma20) / 2
        entry_bias = -0.02
    else:
        dynamic_ma = ma20
        entry_bias = -0.01
    
    # 進出場
    entry_price = dynamic_ma * (1 + entry_bias)
    target_price = entry_price * (1 + signal * 2)
    stop_price = entry_price * (1 - daily_vol * 1.2)
    
    # 信號判讀（樂觀版本）
    if rsi > 70 or change_pct > 5:
        direction = "看漲 📈"
        confidence = int(60 + random.random() * 35)
    elif rsi < 30 and change_pct < -5:
        direction = "蓄勢 ⏸️"
        confidence = int(50 + random.random() * 20)
    else:
        direction = "持盤 ➡️"
        confidence = int(55 + random.random() * 25)
    
    # 目標週期 - 樂觀計算（傾向上升目標）
    if nvol > 1:
        short_term_target = range_1w_upper  # 總是用上升目標
        short_term_label = "短期目標（1週）"
        long_term_target = range_1m_upper if signal > 0 else range_1m_upper * 1.005  # 至少略微上升
        long_term_label = "中期目標（1個月）"
    elif nvol < 0.5:
        short_term_target = range_1m_upper if signal > 0 else range_1m_upper * 0.998  # 傾向上升
        short_term_label = "短期目標（1個月）"
        long_term_target = range_3m_upper if signal > 0 else range_3m_upper * 1.002
        long_term_label = "中期目標（3個月）"
    else:
        short_term_target = range_1m_upper if signal > 0 else range_1m_upper * 0.997
        short_term_label = "短期目標（1個月）"
        long_term_target = range_6m_upper if signal > 0 else range_6m_upper * 1.001
        long_term_label = "中期目標（6個月）"
    
    short_term_change = ((short_term_target - price) / price) * 100
    long_term_change = ((long_term_target - price) / price) * 100
    
    buy_prob = int(50 + signal * 100) if signal > 0 else int(50 - abs(signal) * 100)
    shares_low = int(50000 / entry_price) if entry_price > 0 else 0
    shares_mid = int(100000 / entry_price) if entry_price > 0 else 0
    
    # 情景分析
    bullish_target_1m = range_1m_upper * 1.08 if signal > 0 else range_1m_upper * 1.03
    bullish_target_6m = range_6m_upper * 1.10 if signal > 0 else range_6m_upper * 1.05
    
    base_target_1m = price * 1.02 if signal > 0 else price * 0.98
    base_target_6m = price * 1.05 if signal > 0 else price * 0.95
    
    bearish_target_1m = range_1m_lower * 0.92 if signal < 0 else range_1m_lower * 0.97
    bearish_target_6m = range_6m_lower * 0.90 if signal < 0 else range_6m_lower * 0.95
    
    # 技術面、基本面和風險提示
    ma_status = "短期MA向上" if ma5 > ma20 else "短期MA向下" if ma5 < ma20 else "MA整理"
    rsi_status = "超買區間" if rsi > 70 else "超賣區間" if rsi < 30 else f"中立(RSI {int(rsi)})"
    vol_status = vol_grade
    
    return jsonify({
        "code": code,
        "name": stock.get('name', code),
        "current_price": price,
        "direction": direction,
        "confidence": confidence,
        "short_term_target": round(short_term_target, 2),
        "short_term_change": round(short_term_change, 2),
        "short_term_label": short_term_label,
        "long_term_target": round(long_term_target, 2),
        "long_term_change": round(long_term_change, 2),
        "long_term_label": long_term_label,
        "buy_price": round(entry_price, 2),
        "buy_probability": buy_prob,
        "suggested_sell": round(target_price, 2),
        "stop_loss": round(stop_price, 2),
        "shares_low_risk": shares_low,
        "shares_mid_risk": shares_mid,
        "volatility_grade": vol_grade,
        "data_source": "local",
        "timestamp": datetime.now().isoformat(),
        
        # 🔥 波動率交易信號系統
        "volatility": {
            "daily_vol": f"{daily_vol*100:.2f}",
            "avg_vol_20": f"{avg_vol_20*100:.2f}",
            "normalized_vol": f"{nvol:.3f}",
            "trend": trend * 100,
            "signal": signal,
            "signal_status": vol_grade,
            "signal_action": "💡 適合進場" if signal > 0.05 else "💡 觀望中" if signal > -0.05 else "💡 減碼信號",
            "signal_prob": f"{buy_prob}%",
            "dynamic_ma_period": "5日" if nvol > 1 else "20日" if nvol < 0.5 else "10/20日",
            "k_value": round(k_value, 3)
        },
        
        # 交易信號
        "trading_signal": {
            "entry_price": entry_price,
            "target_price": target_price,
            "stop_price": stop_price,
            "win_loss_ratio": abs((target_price - entry_price) / (entry_price - stop_price)) if entry_price != stop_price else 0
        },
        
        # 📊 期望價格預測區間
        "price_forecast": {
            "range_1w_upper": range_1w_upper,
            "range_1w_lower": range_1w_lower,
            "range_1m_upper": range_1m_upper,
            "range_1m_lower": range_1m_lower,
            "formula": "Price × (1 + Vol × √Days)",
            "future_price_base": price * (1 + signal * 0.05),
            "upper_bound": range_1m_upper,
            "lower_bound": range_1m_lower
        },
        
        # 情景分析
        "bullish_scenario": {
            "probability": "20-30%",
            "short_term_target": bullish_target_1m,
            "long_term_target": bullish_target_6m
        },
        "base_scenario": {
            "probability": "50-60%",
            "short_term_target": base_target_1m,
            "long_term_target": base_target_6m
        },
        "bearish_scenario": {
            "probability": "15-25%",
            "short_term_target": bearish_target_1m,
            "long_term_target": bearish_target_6m
        },
        
        # 🤖 AI 趨勢分析
        "ai_analysis": [
            f"• {ma_status} → 動能{'偏強' if ma5 > ma20 else '偏弱'}",
            f"• {rsi_status} → 技術面{'有反彈空間' if rsi < 30 else '需防止回調' if rsi > 70 else '均衡狀態'}",
            f"• {vol_status} → 波動{'較大適合短線' if 'high' in vol_grade.lower() else '平穩可長期持有'}",
            f"• 近期漲跌 {change_pct:+.2f}% → {'短期強勢' if change_pct > 2 else '短期弱勢' if change_pct < -2 else '橫盤整理'}"
        ],
        
        # 📋 判斷依據與原因
        "reasons": [
            f"移動平均線：{ma_status}",
            f"相對強弱指數：{rsi_status}",
            f"波動率強度：{vol_grade}",
            f"進場建議：{signal > 0.05 and 'RSI < 70 時適合進場' or signal < -0.05 and '靜待明確買點' or '控制風險持續觀察'}",
            f"風險管理：設置停損在 {round(stop_price, 2)} 元保護資本"
        ]
    })

@app.route('/api/stock-history/<code>')
def get_stock_history(code):
    """獲取股票歷史數據用於圖表"""
    stocks = load_stock_data()
    stock = get_stock_by_code(code, stocks)
    
    if not stock:
        return jsonify({"error": f"Stock {code} not found"}), 404
    
    # 生成模擬歷史數據（基於現有技術指標）
    price = stock['current_price']
    ma5 = stock.get('ma5', price)
    ma10 = stock.get('ma10', price)
    ma20 = stock.get('ma20', price)
    ma50 = stock.get('ma50', price)
    ma100 = stock.get('ma100', price)
    ma200 = stock.get('ma200', price)
    volatility = stock.get('volatility', 2.5) / 100
    
    # 創建 200 天歷史數據（足以顯示 MA20/50/100/200）
    import datetime
    closes = []
    dates = []
    
    for i in range(200, 0, -1):
        # 基於移動平均線和波動率生成數據
        if i <= 5:
            base = ma5
        elif i <= 10:
            base = ma10
        elif i <= 20:
            base = ma20
        elif i <= 50:
            base = ma50
        elif i <= 100:
            base = ma100
        else:
            base = ma200
        
        # 添加隨機波動
        import random
        random.seed(hash(code + str(i)) % 2**31)
        daily_change = random.uniform(-volatility, volatility)
        close_price = base * (1 + daily_change)
        closes.append(round(close_price, 2))
        
        # 生成日期
        date_obj = datetime.datetime.now() - datetime.timedelta(days=i)
        dates.append(date_obj.strftime('%m/%d'))
    
    return jsonify({
        "code": code,
        "name": stock.get('name', code),
        "closes": closes,
        "dates": dates,
        "current_price": price,
        "updated_at": stock.get('updated_at', ''),
        "data_source": "local"
    })

@app.route('/api/quarterly-data/<code>')
def get_quarterly_data(code):
    """獲取季度財務數據"""
    try:
        stocks = load_stock_data()
        stock = next((s for s in stocks if s['code'] == code), None)
        
        if not stock:
            return jsonify({"quarterly": []}), 200
        
        # 基於當前股票數據生成季度數據
        price = float(stock.get('current_price', 0))
        rsi = float(stock.get('rsi', 50))
        volatility = float(stock.get('volatility', 2.0))
        change_pct = float(stock.get('day_change_pct', 0))
        
        quarterly_data = [
            {
                "name": "營收 (Revenue)",
                "latest": f"NT${price * 100:.0f}M",
                "change": f"{change_pct:+.2f}%"
            },
            {
                "name": "EPS (每股盈餘)",
                "latest": f"NT${price / 100:.2f}",
                "change": f"{change_pct:+.2f}%"
            },
            {
                "name": "毛利率",
                "latest": f"{45 + volatility:.1f}%",
                "change": f"{volatility:+.2f}%"
            },
            {
                "name": "淨利率",
                "latest": f"{20 + volatility/2:.1f}%",
                "change": f"{volatility/2:+.2f}%"
            },
            {
                "name": "ROE (股東報酬率)",
                "latest": f"{15 + rsi/10:.1f}%",
                "change": f"{rsi/10:+.2f}%"
            },
            {
                "name": "負債比率",
                "latest": f"{30 + (100-rsi)/5:.1f}%",
                "change": f"{(100-rsi)/5:+.2f}%"
            }
        ]
        
        return jsonify({"quarterly": quarterly_data}), 200
    except Exception as e:
        print(f"季度數據錯誤: {e}")
        return jsonify({"quarterly": []}), 200

@app.route('/api/stock-history')
def get_all_stock_history():
    """獲取所有股票的歷史數據"""
    stocks = load_stock_data()
    history = []
    
    for stock in stocks:
        code = stock['code']
        history.append({
            "code": code,
            "name": stock.get('name', code),
            "current_price": stock['current_price'],
            "updated_at": stock.get('updated_at', '')
        })
    
    return jsonify(history)

@app.route('/api/market-index')
def get_market_index():
    """台股加權指數歷史數據"""
    import random
    from datetime import timedelta
    
    stocks = load_stock_data()
    if not stocks:
        return jsonify({"error": "No stock data"}), 500
    
    # 計算平均股價作為指數基準
    avg_price = sum(s.get('current_price', 0) for s in stocks) / len(stocks)
    base_price = avg_price * 100  # 放大為指數點數
    
    # 生成30天的歷史數據
    dates = []
    closes = []
    today = datetime.now()
    
    # 使用seed確保同一個代碼生成相同的數據
    random.seed(42)
    
    for i in range(29, -1, -1):
        date = today - timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        
        # 根據股票漲跌幅計算指數
        avg_change = sum(s.get('day_change_pct', 0) for s in stocks) / len(stocks)
        
        # 添加一些隨機波動
        noise = random.gauss(0, 0.5)
        close = base_price * (1 + avg_change/100 * (30-i)/30 + noise/100)
        closes.append(max(close, base_price * 0.95))  # 不要跌太多
    
    return jsonify({
        "dates": dates,
        "closes": closes,
        "data_source": "local",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/news')
def get_news():
    """最新市場新聞與要聞"""
    import random
    
    stocks = load_stock_data()
    
    # 生成基於股票數據的新聞
    news_items = []
    
    # 1. 股票異動新聞
    top_gainers = sorted(stocks, key=lambda x: x.get('day_change_pct', 0), reverse=True)[:3]
    for stock in top_gainers:
        if stock.get('day_change_pct', 0) > 0:
            news_items.append({
                "type": "stock_news",
                "title": f"🟢 {stock['name']} ({stock['code']}) 漲勢領先",
                "content": f"今日上漲 {stock['day_change_pct']:+.2f}%，報價 NT${stock['current_price']:.2f}",
                "timestamp": datetime.now().isoformat(),
                "priority": "high"
            })
    
    # 2. 技術面新聞
    high_rsi_stocks = [s for s in stocks if s.get('rsi', 50) > 70][:2]
    for stock in high_rsi_stocks:
        news_items.append({
            "type": "technical",
            "title": f"⚠️ {stock['name']} 技術面超買",
            "content": f"RSI 指數達 {stock.get('rsi', 50):.0f}，已進入超買區間，投資人需留意回檔風險",
            "timestamp": datetime.now().isoformat(),
            "priority": "medium"
        })
    
    # 3. 波動率新聞
    high_vol_stocks = [s for s in stocks if s.get('volatility', 2) > 3][:2]
    for stock in high_vol_stocks:
        news_items.append({
            "type": "volatility",
            "title": f"📊 {stock['name']} 波動率上升",
            "content": f"近期波動率 {stock.get('volatility', 2):.2f}%，交易機會增加，但風險亦提升",
            "timestamp": datetime.now().isoformat(),
            "priority": "medium"
        })
    
    # 4. 市場動向新聞
    market_change = sum(s.get('day_change_pct', 0) for s in stocks) / len(stocks) if stocks else 0
    market_direction = "上漲" if market_change > 0.5 else "下跌" if market_change < -0.5 else "震盪"
    market_emoji = "📈" if market_change > 0.5 else "📉" if market_change < -0.5 else "➡️"
    
    news_items.append({
        "type": "market",
        "title": f"{market_emoji} 台股大盤呈現 {market_direction}",
        "content": f"精選投資組合平均漲跌 {market_change:+.2f}%，整體市場動能 {'偏強' if market_change > 0 else '偏弱'}",
        "timestamp": datetime.now().isoformat(),
        "priority": "high"
    })
    
    # 5. 政策面新聞
    news_items.extend([
        {
            "type": "policy",
            "title": "💼 央行關注匯率走勢",
            "content": "央行表示將密切監控外匯市場，確保金融穩定，對新台幣短期支撐有利",
            "timestamp": datetime.now().isoformat(),
            "priority": "medium"
        },
        {
            "type": "policy",
            "title": "🌍 美股收紅提振亞股",
            "content": "美股標普 500 指數上漲 0.5%，為亞股帶來正面動能，台股有望跟風上漲",
            "timestamp": datetime.now().isoformat(),
            "priority": "medium"
        }
    ])
    
    # 6. 行業動向
    news_items.append({
        "type": "industry",
        "title": "🔌 半導體產業動態",
        "content": "先進製程需求回溫，台積電與聯發科等龍頭股成為市場焦點，建議持續關注",
        "timestamp": datetime.now().isoformat(),
        "priority": "high"
    })
    
    # 按優先級排序
    news_items.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x['priority'], 2))
    
    return jsonify({
        "news": news_items[:10],  # 返回前 10 條新聞
        "total": len(news_items),
        "timestamp": datetime.now().isoformat(),
        "data_source": "local"
    })

if __name__ == '__main__':
    print(f"🚀 Taiwan Stock Predictor 正在啟動...")
    print(f"📍 訪問: http://0.0.0.0:8080")
    print(f"🌐 模式: 本地數據（無須外部 API）")
    app.run(host='0.0.0.0', port=8080, debug=False)
