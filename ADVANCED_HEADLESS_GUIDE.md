# 🖥️ Headless 瀏覽器版本 - Selenium/Playwright 實現

如果目標網站需要 JavaScript 渲染（動態載入內容），可使用以下方案。

## 📦 版本 1：Selenium + Chrome Headless

### 安裝依賴

```bash
# 在伺服器上執行
pip install selenium webdriver-manager

# 安裝 Chrome（如果還未安裝）
apt-get install -y chromium-browser chromium-chromedriver
```

### Python 代碼片段

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def extract_red_text_selenium(url):
    \"\"\"使用 Selenium 進行 Headless 爬取和紅字偵測\"\"\"
    
    # 配置 Chrome 選項
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 後台運行
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = None
    try:
        # 啟動瀏覽器
        driver = webdriver.Chrome(options=chrome_options)
        
        # 載入網頁
        driver.get(url)
        
        # 等待頁面完全載入（最多 10 秒）
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'body'))
        )
        
        # 等待動態內容載入（根據需要調整）
        time.sleep(2)
        
        # 獲取頁面 HTML
        page_html = driver.page_source
        
        # 使用 BeautifulSoup 解析
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(page_html, 'html.parser')
        red_tickets = []
        
        # 尋找所有帶有紅色 CSS 的元素
        for element in soup.find_all(['span', 'div', 'td', 'p', 'a', 'li']):
            style = element.get('style', '').lower()
            class_name = ' '.join(element.get('class', [])).lower()
            
            is_red = any([
                'color:red' in style or 'color: red' in style,
                'color:#ff0000' in style,
                'color:rgb(255,0,0)' in style,
                'red' in class_name,
            ])
            
            if is_red:
                text = element.get_text(strip=True)
                if text:
                    # 精確匹配「XX區剩餘XX票」
                    pattern = r'([A-Za-z0-9\\u4e00-\\u9fa5]+區)剩餘(\\d+)票'
                    matches = re.findall(pattern, text)
                    if matches:
                        for area, quantity in matches:
                            ticket_info = f\"{area}剩餘{quantity}票\"
                            if ticket_info not in red_tickets:
                                red_tickets.append(ticket_info)
        
        return red_tickets if red_tickets else None
    
    except Exception as e:
        logger.error(f\"Selenium Error: {e}\")
        return None
    
    finally:
        if driver:
            driver.quit()
```

---

## 📦 版本 2：Playwright

### 安裝依賴

```bash
# 在伺服器上執行
pip install playwright
python -m playwright install chromium
```

### Python 代碼片段

```python
import asyncio
from playwright.async_api import async_playwright
import re
from bs4 import BeautifulSoup

async def extract_red_text_playwright(url):
    \"\"\"使用 Playwright 進行 Headless 爬取和紅字偵測\"\"\"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = await browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        try:
            # 載入網頁
            await page.goto(url, wait_until='networkidle')
            
            # 等待動態內容（根據需要調整）
            await asyncio.sleep(2)
            
            # 獲取頁面 HTML
            page_html = await page.content()
            
            # 使用 BeautifulSoup 解析
            soup = BeautifulSoup(page_html, 'html.parser')
            red_tickets = []
            
            # 尋找所有帶有紅色的元素
            for element in soup.find_all(['span', 'div', 'td', 'p', 'a', 'li']):
                style = element.get('style', '').lower()
                class_name = ' '.join(element.get('class', [])).lower()
                
                is_red = any([
                    'color:red' in style or 'color: red' in style,
                    'color:#ff0000' in style,
                    'color:rgb(255,0,0)' in style,
                    'red' in class_name,
                ])
                
                if is_red:
                    text = element.get_text(strip=True)
                    if text:
                        # 精確匹配「XX區剩餘XX票」
                        pattern = r'([A-Za-z0-9\\u4e00-\\u9fa5]+區)剩餘(\\d+)票'
                        matches = re.findall(pattern, text)
                        if matches:
                            for area, quantity in matches:
                                ticket_info = f\"{area}剩餘{quantity}票\"
                                if ticket_info not in red_tickets:
                                    red_tickets.append(ticket_info)
            
            return red_tickets if red_tickets else None
        
        except Exception as e:
            logger.error(f\"Playwright Error: {e}\")
            return None
        
        finally:
            await page.close()
            await browser.close()

# 在監控循環中使用
@tasks.loop(seconds=CHECK_INTERVAL)
async def monitoring_loop():
    if not monitor_list:
        return
    
    for name, info in monitor_list.items():
        try:
            # 使用 Playwright 爬取
            red_info = await extract_red_text_playwright(info.get(\"url\", \"\"))
            
            # 其餘邏輯與原版相同...
            if red_info:
                # ... 發送通知
                pass
        except Exception as e:
            logger.error(f\"Error monitoring {name}: {e}\")
```

---

## 🎯 Selenium vs Playwright 對比

| 特性 | Selenium | Playwright |
|------|----------|-----------|
| 性能 | 中等 | 優 ⭐ |
| 穩定性 | 良好 | 優秀 ⭐ |
| 配置難度 | 中等 | 簡單 ⭐ |
| 社群支援 | 龐大 | 成長中 |
| 異步支援 | 不支持 | 支持 ⭐ |
| 記憶體占用 | 較高 | 較低 ⭐ |

**推薦**：Playwright（更快、更穩定、更省資源）

---

## 🚀 Linux 伺服器 Headless 部署

### 1. 安裝 Playwright 版本

```bash
# SSH 進伺服器
ssh root@172.105.216.222

# 進入工作目錄
cd /root/discord-bot

# 安裝依賴
pip install playwright
python -m playwright install chromium

# 驗證安裝
playwright install --with-deps chromium
```

### 2. 更新 bot.py 代碼

將上面的 `extract_red_text_playwright()` 函數替換原有的 `extract_red_text_info()`

### 3. 啟動服務

```bash
# 使用 systemd（推薦）
sudo systemctl restart discord-bot

# 或使用 nohup
nohup python3 bot.py > bot.log 2>&1 &
```

### 4. 監控運行

```bash
# 檢查日誌
tail -f /root/discord-bot/bot.log

# 查看進程資源占用
ps aux | grep bot.py

# 監控記憶體
top -p $(pgrep -f bot.py)
```

---

## ⚠️ 注意事項

### Headless 瀏覽器的限制
1. **速度較慢**：比純 HTML 爬取慢 5-10 倍
2. **資源占用高**：每次檢查需要啟動瀏覽器
3. **被封禁風險**：過於頻繁可能被網站防火牆封禁

### 優化建議

```python
# 方案 1：使用進程池（多個瀏覽器實例）
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=3)

# 方案 2：增加檢查間隔
CHECK_INTERVAL = 5  # 改為 5 秒檢查一次，而非 1 秒

# 方案 3：使用代理池
proxies = [
    'http://proxy1:8080',
    'http://proxy2:8080',
]

# 方案 4：設置 User-Agent 隨機化
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...',
]
```

---

## 🔧 故障排除

### 問題：Chromium 無法啟動

```bash
# 解決方案 1：安裝依賴
apt-get install -y libnss3 libgconf-2-4 libfontconfig1

# 解決方案 2：使用 --disable-setuid-sandbox
chrome_options.add_argument('--disable-setuid-sandbox')
```

### 問題：記憶體溢出

```bash
# 解決方案：使用更輕量的 chromium
# 或增加檢查間隔
CHECK_INTERVAL = 10

# 或在循環中手動清理
import gc
gc.collect()
```

### 問題：連接超時

```python
# 增加超時時間
page = await browser.new_page()
page.set_default_navigation_timeout(30000)  # 30 秒
```

---

**選擇合適的方案，根據目標網站的特性決定！**
