import json
from datetime import datetime

# 讀取現有數據
with open('stock_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

stocks = data['stocks']

# 過濾掉不要的股票 (2204 中華, 3035 智原)
filtered = [s for s in stocks if s['code'] not in ['2204', '3035']]

# 添加華通
huatong = {
    'code': '2211',
    'name': '華通',
    'current_price': 93.9,
    'day_change_pct': 0.21,
    'rsi': 52.5,
    'ma5': 93.5,
    'ma10': 93.2,
    'ma20': 92.8,
    'ma50': 91.5,
    'ma200': 89.2,
    'support': 90.5,
    'resistance': 96.2,
    'volatility': 1.12,
    'updated_at': datetime.now().isoformat()
}

# 在中華電後面插入華通
insert_pos = next((i for i, s in enumerate(filtered) if s['code'] == '2412'), -1)
if insert_pos >= 0:
    filtered.insert(insert_pos + 1, huatong)

# 更新JSON
data['stocks'] = filtered

# 寫回檔案
with open('stock_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('✅ 已更新！現有 ' + str(len(filtered)) + ' 支股票')
for s in filtered:
    print('   ' + s['code'] + ' ' + s['name'])
