// ============ 全局變量 ============
let STOCKS_CACHE = [];
let AUTO_REFRESH_INTERVAL = null;

// ============ 初始化 ============
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 初始化儀表板');
    loadAllStocks();
    loadMarketStatus();
    startAutoRefresh();
});

// ============ 標籤頁切換 ============
function switchTab(tabName) {
    // 隱藏所有標籤頁
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 移除所有標籤按鈕的活動狀態
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 顯示選擇的標籤頁
    document.getElementById(tabName).classList.add('active');
    
    // 激活按鈕
    event.target.classList.add('active');
    
    // 首次顯示時加載數據
    if (tabName === 'market') {
        setTimeout(renderMarketChart, 100);
    } else if (tabName === 'stocks') {
        renderStockGrid();
    } else if (tabName === 'news') {
        renderNews();
    }
}

// ============ 數據加載 ============
async function loadAllStocks() {
    try {
        const response = await fetch('/api/all-stocks?t=' + Date.now());
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        STOCKS_CACHE = await response.json();
        console.log(`✅ 加載 ${STOCKS_CACHE.length} 支股票`);
        
        renderStockGrid();
        updateSummaryStats();
        updateSelectors();
        
    } catch (error) {
        console.error('❌ 加載股票失敗:', error);
        document.getElementById('stockGrid').innerHTML = '❌ 加載失敗';
    }
}

async function loadTopStocks() {
    try {
        const response = await fetch('/api/top-stocks?t=' + Date.now());
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const topStocks = await response.json();
        renderTopStocks(topStocks);
        
    } catch (error) {
        console.error('加載頂部股票失敗:', error);
    }
}

async function loadMarketStatus() {
    try {
        const response = await fetch('/api/market-status?t=' + Date.now());
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const status = await response.json();
        document.getElementById('marketStatus').innerHTML = `
            <span class="status-indicator"></span>
            ${status.status_text}
        `;
        
    } catch (error) {
        console.error('加載市場狀態失敗:', error);
    }
}

// ============ 渲染函數 ============
function renderStockGrid() {
    const container = document.getElementById('stockGrid');
    
    if (!STOCKS_CACHE || STOCKS_CACHE.length === 0) {
        container.innerHTML = '<p class="loading">暫無數據</p>';
        return;
    }
    
    const stocks = applyFiltersAndSort();
    
    container.innerHTML = stocks.map(stock => {
        const change = parseFloat(stock.day_change_pct || 0);
        const changeClass = change >= 0 ? 'up' : 'down';
        const changeSymbol = change >= 0 ? '📈' : '📉';
        
        return `
            <div class="stock-card" onclick="showStockDetail('${stock.code}')">
                <div class="stock-code">${stock.code}</div>
                <div class="stock-name">${stock.name}</div>
                <div class="stock-price">$${formatNumber(stock.current_price)}</div>
                <div class="stock-change ${changeClass}">
                    ${changeSymbol} ${change >= 0 ? '+' : ''}${change.toFixed(2)}%
                </div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 10px;">
                    <div>RSI: ${stock.rsi ? stock.rsi.toFixed(1) : '-'}</div>
                    <div>MA20: ${stock.ma20 ? formatNumber(stock.ma20) : '-'}</div>
                </div>
            </div>
        `;
    }).join('');
}

function renderTopStocks(stocks) {
    const container = document.getElementById('topStocksContainer');
    
    if (!stocks || stocks.length === 0) {
        container.innerHTML = '<p class="info-text">暫無數據</p>';
        return;
    }
    
    container.innerHTML = stocks.map(stock => {
        const change = parseFloat(stock.day_change_pct || 0);
        return `
            <div class="top-stock-item">
                <div>
                    <div class="top-stock-name">${stock.name}</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">${stock.code}</div>
                </div>
                <div class="top-stock-change">${change >= 0 ? '+' : ''}${change.toFixed(2)}%</div>
            </div>
        `;
    }).join('');
}

function updateSummaryStats() {
    if (!STOCKS_CACHE || STOCKS_CACHE.length === 0) return;
    
    const upCount = STOCKS_CACHE.filter(s => parseFloat(s.day_change_pct || 0) > 0).length;
    const downCount = STOCKS_CACHE.length - upCount;
    
    document.getElementById('upCount').textContent = upCount;
    document.getElementById('downCount').textContent = downCount;
    
    loadTopStocks();
}

function updateSelectors() {
    const selector = document.getElementById('predictionSelector');
    selector.innerHTML = '<option value="">-- 請選擇 --</option>' + 
        STOCKS_CACHE.map(s => `<option value="${s.code}">${s.name} (${s.code})</option>`).join('');
}

function renderMarketChart() {
    const canvas = document.getElementById('marketChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // 生成模擬數據
    const labels = [];
    const prices = [];
    let basePrice = 15000;
    
    for (let i = 0; i < 20; i++) {
        labels.push(`${9 + Math.floor(i/2)}:${(i % 2) * 30}`);
        basePrice += (Math.random() - 0.5) * 100;
        prices.push(Math.round(basePrice));
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '加權指數',
                data: prices,
                borderColor: '#7c3aed',
                backgroundColor: 'rgba(124, 58, 237, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#7c3aed'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: false }
            }
        }
    });
}

function renderNews() {
    const container = document.getElementById('newsList');
    
    const news = [
        {
            priority: '🔴 緊急',
            title: '美股標普500指數創新高',
            content: '美國股市在積極經濟數據推動下創下新高，投資者對科技股前景樂觀。',
            time: '2小時前'
        },
        {
            priority: '🟡 重要',
            title: '台積電產能持續擴張',
            content: '台積電宣布進一步擴大產能投資計畫，以應對全球晶片需求。',
            time: '4小時前'
        },
        {
            priority: '🟢 消息',
            title: '聯發科推出新款5G晶片',
            content: '聯發科技發布最新世代5G處理器，性能提升15%，耗電降低10%。',
            time: '6小時前'
        },
        {
            priority: '🟢 消息',
            title: '大立光評估提價計畫',
            content: '光學鏡頭龍頭大立光因原料成本上升，評估調升產品售價。',
            time: '8小時前'
        },
        {
            priority: '🟡 重要',
            title: '央行將召開貨幣政策會議',
            content: '中央銀行下週召開貨幣政策會議，市場關注是否升息。',
            time: '12小時前'
        }
    ];
    
    container.innerHTML = news.map(item => `
        <div class="news-item">
            <span class="news-badge">${item.priority}</span>
            <div class="news-title">${item.title}</div>
            <div class="news-content">${item.content}</div>
            <div class="news-time">${item.time}</div>
        </div>
    `).join('');
}

// ============ 股票詳情 ============
function showStockDetail(code) {
    const stock = STOCKS_CACHE.find(s => s.code === code);
    if (!stock) return;
    
    alert(`
${stock.name} (${stock.code})
───────────────────
現價: $${formatNumber(stock.current_price)}
漲跌: ${stock.day_change_pct >= 0 ? '+' : ''}${stock.day_change_pct.toFixed(2)}%

技術指標：
RSI: ${stock.rsi.toFixed(2)}
MA5: ${formatNumber(stock.ma5)}
MA20: ${formatNumber(stock.ma20)}
MA50: ${formatNumber(stock.ma50)}

支撐: $${formatNumber(stock.support)}
壓力: $${formatNumber(stock.resistance)}
    `);
}

// ============ 預測 ============
async function showPrediction() {
    const code = document.getElementById('predictionSelector').value;
    if (!code) return;
    
    const resultDiv = document.getElementById('predictionResult');
    resultDiv.innerHTML = '<p class="loading">分析中...</p>';
    
    try {
        const response = await fetch(`/api/prediction/${code}?t=${Date.now()}`);
        if (!response.ok) {
            resultDiv.innerHTML = '<p class="info-text">預測功能暫未開放</p>';
            return;
        }
        
        const pred = await response.json();
        const stock = STOCKS_CACHE.find(s => s.code === code);
        
        resultDiv.innerHTML = `
            <div class="prediction-item">
                <h4>${stock.name} (${code})</h4>
                <p><strong>現價:</strong> $${formatNumber(stock.current_price)}</p>
                <p><strong>目標價:</strong> $${formatNumber(pred.target_price)}</p>
                <p><strong>預測方向:</strong> ${pred.direction}</p>
                <p><strong>信心度:</strong> ${pred.confidence}%</p>
            </div>
        `;
    } catch (error) {
        resultDiv.innerHTML = '<p class="info-text">預測分析暫未開放</p>';
    }
}

// ============ 工具函數 ============
function formatNumber(num) {
    if (!num) return '0';
    return parseFloat(num).toLocaleString('zh-TW', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function applyFiltersAndSort() {
    let filtered = [...STOCKS_CACHE];
    
    // 搜尋過濾
    const search = document.getElementById('searchInput').value.toLowerCase();
    if (search) {
        filtered = filtered.filter(s => 
            s.code.includes(search) || s.name.toLowerCase().includes(search)
        );
    }
    
    // 排序
    const sortType = document.getElementById('sortSelector').value;
    switch (sortType) {
        case 'price':
            filtered.sort((a, b) => b.current_price - a.current_price);
            break;
        case 'change':
            filtered.sort((a, b) => (b.day_change_pct || 0) - (a.day_change_pct || 0));
            break;
        case 'volume':
            filtered.sort((a, b) => (b.trading_volume || 0) - (a.trading_volume || 0));
            break;
        case 'name':
        default:
            filtered.sort((a, b) => a.name.localeCompare(b.name, 'zh-TW'));
    }
    
    return filtered;
}

function filterStocks() {
    renderStockGrid();
}

function sortStocks() {
    renderStockGrid();
}

function refreshData() {
    console.log('🔄 手動刷新數據');
    loadAllStocks();
    loadMarketStatus();
}

function startAutoRefresh() {
    // 每10秒自動刷新一次
    AUTO_REFRESH_INTERVAL = setInterval(() => {
        const now = new Date();
        if (now.getHours() >= 9 && now.getHours() < 15) {
            loadAllStocks();
            loadMarketStatus();
        }
    }, 10000);
}

// 更新時間戳
function updateTimestamp() {
    const now = new Date();
    document.getElementById('updateTime').textContent = now.toLocaleString('zh-TW');
}

// 每秒更新時間
setInterval(updateTimestamp, 1000);
updateTimestamp();
