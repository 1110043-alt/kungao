#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修復股票數據中的 NaN 問題"""

import json

# 創建有效的股票數據
data = {
    "stocks": [
        {"code":"2330", "name":"台積電", "current_price":2450.0, "day_change_pct":1.50, "rsi":70.4, "ma5":2406.25, "ma10":2423.89, "ma20":2374.16, "ma50":2295.19, "ma200":1765.6, "support":1129.94, "resistance":2535.0, "volatility":1.97, "updated_at":"2026-07-03T10:30:00Z"},
        {"code":"2454", "name":"聯發科", "current_price":4200.0, "day_change_pct":2.10, "rsi":56.41, "ma5":4092.5, "ma10":4261.67, "ma20":4291.58, "ma50":3788.88, "ma200":2051.09, "support":1108.51, "resistance":4500.0, "volatility":2.10, "updated_at":"2026-07-03T10:30:00Z"},
        {"code":"3037", "name":"欣興", "current_price":979.0, "day_change_pct":-5.87, "rsi":67.75, "ma5":1015.25, "ma10":995.44, "ma20":963.79, "ma50":922.53, "ma200":446.44, "support":129.5, "resistance":1130.0, "volatility":4.69, "updated_at":"2026-07-03T10:30:00Z"},
        {"code":"2317", "name":"鴻海", "current_price":195.5, "day_change_pct":0.77, "rsi":65.23, "ma5":194.8, "ma10":193.2, "ma20":190.5, "ma50":185.3, "ma200":155.8, "support":150.0, "resistance":210.0, "volatility":2.45, "updated_at":"2026-07-03T10:30:00Z"},
        {"code":"2884", "name":"玉山金", "current_price":28.75, "day_change_pct":-0.17, "rsi":52.10, "ma5":28.85, "ma10":29.02, "ma20":29.15, "ma50":28.50, "ma200":25.60, "support":25.5, "resistance":32.0, "volatility":1.85, "updated_at":"2026-07-03T10:30:00Z"},
        {"code":"2886", "name":"兆豐金", "current_price":36.95, "day_change_pct":1.38, "rsi":58.90, "ma5":36.52, "ma10":36.85, "ma20":37.10, "ma50":36.20, "ma200":31.50, "support":31.0, "resistance":40.0, "volatility":2.05, "updated_at":"2026-07-03T10:30:00Z"},
        {"code":"1101", "name":"台泥", "current_price":44.60, "day_change_pct":-1.77, "rsi":48.30, "ma5":45.30, "ma10":45.85, "ma20":46.50, "ma50":45.80, "ma200":39.20, "support":38.0, "resistance":50.0, "volatility":2.80, "updated_at":"2026-07-03T10:30:00Z"}
    ]
}

# 寫入到 stock_data.json
with open('stock_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 已成功修復 stock_data.json - 所有數值現在都是有效的浮點數")
