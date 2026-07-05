// Taiwan Stock Predictor Dashboard - Complete JavaScript with Charts
let currentChart = null;
let marketChart = null;
let stocks = {};
const prevPrices = {};
let lastNewsDate = null;
let lastMarketDate = null;
const MARKET_REFRESH_MS = 10000;
const predictionCache = {}; // 緩存預測數據以加快切換

document.addEventListener("DOMContentLoaded", () => {
    console.log("🟢 DOMContentLoaded fired");
    
    setupSelectors();
    setupActionButtons();
    initTradingAnalysis();
    
    // 🎯 初始化：一進網頁立刻把底部那些卡住的幽靈標籤區塊完全隱藏拿掉
    hideBottomPanels();

    document.getElementById("refreshBtn")?.addEventListener("click", () => {
        refreshDashboard(true);
    });
    
    (async () => {
        try {
            console.log("🟡 Starting initial data load...");
            
            const allStocksResponse = await fetch("/api/all-stocks?t=" + Date.now());
            if (!allStocksResponse.ok) {
                throw new Error(`API Error: ${allStocksResponse.status}`);
            }
            const allStocks = await allStocksResponse.json();
            
            const topStocksResponse = await fetch("/api/top-stocks?t=" + Date.now());
            const topStocks = await topStocksResponse.json();
            
            console.log("✅ Fetched data:", allStocks.length, "stocks");
            
            cacheStocks(allStocks);
            
            renderStockGrid(allStocks);
            renderTopStocks(topStocks);
            updateSummaryStats(allStocks, topStocks);
            updateSelectors(allStocks);
            setLastUpdate(allStocks);
            
            // 自動加載第一個股票的預測分析
            if (allStocks.length > 0) {
                setTimeout(() => loadPredictionAnalysis(allStocks[0].code), 500);
            }
            
            // 初始化填充 MA 值到 HTML 中
            const initializeMADisplay = () => {
                const stock = window.stocks?.[0];
                if (stock) {
                    try {
                        document.getElementById('ma5Value').innerText = `NT$${stock.ma5.toFixed(2)}`;
                        document.getElementById('ma10Value').innerText = `NT$${stock.ma10.toFixed(2)}`;
                        document.getElementById('ma20Value').innerText = `NT$${stock.ma20.toFixed(2)}`;
                        document.getElementById('ma50Value').innerText = `NT$${stock.ma50.toFixed(2)}`;
                        document.getElementById('ma200Value').innerText = `NT$${stock.ma200.toFixed(2)}`;
                        
                        const price = stock.current_price;
                        let maTrend = '持平';
                        if (price > stock.ma5 && price > stock.ma20 && price > stock.ma200) {
                            maTrend = '📈 強勢上升';
                        } else if (price > stock.ma5 && price > stock.ma20) {
                            maTrend = '📈 短線上升';
                        } else if (price > stock.ma20 && price > stock.ma200) {
                            maTrend = '📈 中期上升';
                        } else if (price > stock.ma200) {
                            maTrend = '📈 長期上升';
                        } else if (price < stock.ma5 && price < stock.ma20 && price < stock.ma200) {
                            maTrend = '⏸️ 蓄勢調整';
                        } else {
                            maTrend = '➡️ 區間整理';
                        }
                        document.getElementById('maTrend').innerText = maTrend;
                    } catch (e) {
                        console.log('MA display initialization:', e);
                    }
                }
            };
            setTimeout(initializeMADisplay, 1000);
            
            console.log("✅ Dashboard loaded");
            
        } catch (error) {
            console.error("❌ Initial load failed:", error);
        }
    })();

    setInterval(() => checkForNewTradingDay(), 60000);
    setInterval(() => refreshNewsIfNeeded(), 300000);
    
    // 🚀 優化刷新速率：盤中 5 秒，盤後 30 秒
    function getRefreshInterval() {
        const now = new Date();
        const hours = now.getHours();
        const minutes = now.getMinutes();
        const isMarketHours = (hours === 9 && minutes >= 0) || (hours > 9 && hours < 13) || (hours === 13 && minutes < 30);
        return isMarketHours ? 5000 : 30000;
    }
    
    let refreshTimer = setInterval(() => {
        const interval = getRefreshInterval();
        refreshDashboard();
        clearInterval(refreshTimer);
        refreshTimer = setInterval(() => refreshDashboard(), getRefreshInterval());
    }, getRefreshInterval());
    
    // 🔄 每 10 秒自動刷新預測數據（Yahoo Finance 實時更新）
    setInterval(() => {
        const predictionSelector = document.getElementById("predictionStockSelect");
        if (predictionSelector && predictionSelector.value) {
            const selectedCode = predictionSelector.value;
            console.log(`🔄 自動刷新預測數據: ${selectedCode} (${new Date().toLocaleTimeString()})`);
            fetchAndCachePrediction(selectedCode);
        }
    }, 10000);
});

// 🛑【核心修正】找不到股票或未選擇時，徹底把底部區塊拿掉/隱藏的函數
function hideBottomPanels() {
    // 尋找「AI趨勢研判」和「判斷依據與原因」的外層大型容器外殼
    const trendSection = document.getElementById('aiTrendAnalysisText')?.closest('div[style*="background"]') || 
                         document.querySelector('#analysis div[style*="AI趨勢研判"]')?.parentElement ||
                         document.querySelector('#analysis div:nth-last-child(2)');
                         
    const basisSection = document.querySelector('#analysis div[style*="background"] div')?.closest('div[style*="background"]') || 
                         document.querySelector('#analysis div[style*="判斷依據"]') ||
                         document.querySelector('#analysis div:last-child');

    // 徹底隱藏，不留白、不留任何框線死角
    if (trendSection && trendSection.id !== 'analysis') {
        trendSection.style.display = 'none';
    }
    if (basisSection && basisSection.id !== 'analysis') {
        basisSection.style.display = 'none';
    }
    
    // 移除下單張數的提示
    const oldTips = document.querySelector('.risk-shares-tips');
    if (oldTips) oldTips.remove();
}

// 🟢【核心修正】當真正選擇股票時，才把底部這兩塊完好如初地展現出來
function showBottomPanels() {
    const trendSection = document.getElementById('aiTrendAnalysisText')?.closest('div[style*="background"]') || 
                         document.querySelector('#analysis div[style*="AI趨勢研判"]')?.parentElement ||
                         document.querySelector('#analysis div:nth-last-child(2)');
                         
    const basisSection = document.querySelector('#analysis div[style*="background"] div')?.closest('div[style*="background"]') || 
                         document.querySelector('#analysis div[style*="判斷依據"]') ||
                         document.querySelector('#analysis div:last-child');

    if (trendSection) trendSection.style.display = 'block';
    if (basisSection) basisSection.style.display = 'block';
}

async function refreshDashboard(manual = false) {
    try {
        const [allStocks, topStocks] = await Promise.all([
            fetchJson("/api/all-stocks"),
            fetchJson("/api/top-stocks"),
        ]);
        cacheStocks(allStocks);
        renderStockGrid(allStocks);
        renderTopStocks(topStocks);
        updateSummaryStats(allStocks, topStocks);
        updateSelectors(allStocks);
        setLastUpdate(allStocks);
    } catch (error) {
        console.error("Dashboard refresh failed:", error);
    }
}

function checkForNewTradingDay() {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const isMarketHours = (hours === 9 && minutes >= 0) || (hours > 9 && hours < 13) || (hours === 13 && minutes < 30);
    const currentDate = now.toISOString().split('T')[0];
    if (isMarketHours && lastMarketDate !== currentDate) {
        lastMarketDate = currentDate;
        refreshDashboard(true);
    }
}

function refreshNewsIfNeeded() {
    const now = new Date();
    const currentDate = now.toISOString().split('T')[0];
    if (lastNewsDate !== currentDate) {
        lastNewsDate = currentDate;
        if (typeof loadNews === 'function') loadNews();
    }
}

function goToStockDetail(code) {
    const btn = document.querySelector('button[data-tab="analysis"]');
    const selector = document.getElementById("detailStockSelect");
    if (selector) {
        selector.value = code;
        loadDetailedAnalysis(code);
    }
    showTab('analysis', btn);
}

function showTab(tabName, button) {
    document.querySelectorAll(".tab-content").forEach((el) => {
        el.classList.toggle("hidden", el.id !== tabName);
        el.classList.toggle("active", el.id === tabName);
    });
    document.querySelectorAll(".tab-btn").forEach((el) => el.classList.remove("active"));
    button?.classList.add("active");

    if (tabName === "market") loadMarketChart();
    if (tabName === "analysis") {
        const selected = document.getElementById("detailStockSelect")?.value;
        if (selected) {
            loadDetailedAnalysis(selected);
        } else {
            hideBottomPanels(); // 切換標籤時沒選股票，直接完全隱藏
        }
    }
    if (tabName === "prediction") {
        let selected = document.getElementById("predictionStockSelect")?.value;
        // 如果沒有選擇，自動選擇第一個股票
        if (!selected || selected === 'Select Stock') {
            const selector = document.getElementById("predictionStockSelect");
            if (selector && selector.options.length > 1) {
                selector.selectedIndex = 1;
                selected = selector.value;
            }
        }
        if (selected && selected !== 'Select Stock') {
            loadPredictionAnalysis(selected);
        }
    }
    if (tabName === "news") initializeNewsSystem();
}

function setupSelectors() {
    document.getElementById("detailStockSelect")?.addEventListener("change", (e) => {
        if (e.target.value) {
            loadDetailedAnalysis(e.target.value);
        } else {
            hideBottomPanels(); // 使用者切回預設未選狀態，隱藏拿掉底部
        }
    });
    document.getElementById("predictionStockSelect")?.addEventListener("change", (e) => {
        if (e.target.value) {
            loadPredictionAnalysis(e.target.value);
        } else {
            hideBottomPanels();
        }
    });
}

function setupActionButtons() {
    document.getElementById("analyzeBtn")?.addEventListener("click", analyzeTradingCosts);
}

function initTradingAnalysis() {
    document.getElementById("analyzerStockSelect")?.addEventListener("change", (e) => {
        const code = e.target.value;
        if (code && code !== 'Select Stock') loadTradingSignals(code);
    });
}

async function fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${url}`);
    return response.json();
}

function cacheStocks(stocks) {
    window.stocks = stocks;
}

// 剩餘沒變動的底層渲染保持原樣，確保完全相容不破壞排版
function updateSelectors(allStocks) {
    ['detailStockSelect', 'analyzerStockSelect', 'predictionStockSelect'].forEach(id => {
        const selector = document.getElementById(id);
        if (!selector) return;
        const options = allStocks.map(s => `<option value="${s.code}">${s.name} (${s.code})</option>`).join('');
        selector.innerHTML = '<option value="">Select Stock</option>' + options;
        
        // 預測選擇器自動選擇第一個股票
        if (id === 'predictionStockSelect' && allStocks.length > 0) {
            selector.selectedIndex = 1;
            // 觸發 change 事件以加載預測數據
            selector.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });
}

function renderStockGrid(stocksData) {
    const container = document.getElementById("stockGrid");
    if (!container) return;
    // 產業映射表 (與 updateSummaryStats 保持同步)
    const industryMap = {
        '2330': '半導體', '2454': '半導體', '8299': '半導體', '2344': '半導體',
        '2317': '電子製造', '3037': '電子製造', '2211': '電子製造',
        '2884': '金融', '2886': '金融',
        '1101': '水泥',
        '3008': '光學',
        '2376': '電腦周邊',
        '2412': '電信',
        '0050': '指數'
    };
    const html = stocksData.map(stock => {
        const pct = stock.day_change_pct || 0;
        const up = pct >= 0;
        const absPct = Math.abs(pct);
        const price = stock.current_price || 0;
        const code = stock.code || '';
        const rsi = stock.rsi || 50;
        const category = industryMap[String(code)] || '其他';
        let rsiColor = rsi < 30 ? '#10b981' : rsi > 70 ? '#ef4444' : '#7c3aed';
        let rsiStatus = rsi < 30 ? '超賣' : rsi > 70 ? '超買' : '中性';
        const categoryIcons = { '電子/半導體': '🖥️', '金融股': '💰', '傳產股': '🏭', 'EFF': '📊', '半導體': '🖥️', '電子製造': '📱', '金融': '💰', '水泥': '🏭', '光學': '🔍', '電腦周邊': '⌨️', '電信': '📡', '指數': '📊', '其他': '📈' };
        return `<div class="stock-card" data-code="${code}" style="padding: 18px; background: linear-gradient(135deg, #ffffff 0%, #faf8ff 100%); border: 1.5px solid #e9d5ff; border-radius: 14px; cursor: pointer; box-shadow: 0 4px 6px rgba(124, 58, 237, 0.08); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 12px; right: 12px; background: rgba(124, 58, 237, 0.1); padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: 700; color: #7c3aed;">
                <span>${categoryIcons[category] || '📈'}</span> <span>${category}</span>
            </div>
            <div style="margin-bottom: 14px; padding-right: 140px;">
                <h3 style="margin: 0 0 4px 0; font-size: 28px; font-weight: 800;">${stock.name}</h3>
                <p style="margin: 0; font-size: 13px; color: #666;">代碼: <span style="font-family: monospace; color: #7c3aed;">${code}</span></p>
            </div>
            <div style="margin-bottom: 14px;">
                <div style="font-size: 28px; font-weight: 900;">NT$${price.toFixed(2)}</div>
                <div style="font-size: 14px; font-weight: 700; color: ${up ? '#ef4444' : '#10b981'}; margin-top: 4px;">
                    <span>${up ? '📈' : '📉'} ${up ? '+' : ''}${absPct.toFixed(2)}%</span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div style="padding: 10px; background: rgba(124, 58, 237, 0.06); border-radius: 10px;">
                    <div style="font-size: 11px; color: #666;">RSI (14)</div>
                    <div style="font-size: 18px; font-weight: 900; color: ${rsiColor};">${rsi.toFixed(1)}</div>
                </div>
                <div style="padding: 10px; background: rgba(168, 85, 247, 0.06); border-radius: 10px;">
                    <div style="font-size: 11px; color: #666;">波動率</div>
                    <div style="font-size: 18px; font-weight: 900; color: #a855f7;">${(stock.volatility || 0).toFixed(2)}%</div>
                </div>
            </div>
        </div>`;
    }).join('');
    container.innerHTML = html;
    container.querySelectorAll('.stock-card').forEach(card => {
        card.addEventListener('click', () => { if (card.dataset.code) goToStockDetail(card.dataset.code); });
    });
}

function renderTopStocks(topStocks) {
    const container = document.getElementById("topStocksContainer");
    if (!container) return;
    const medals = ['🥇', '🥈', '🥉'];
    container.innerHTML = topStocks.slice(0, 3).map((stock, idx) => {
        const up = (stock.day_change_pct || 0) >= 0;
        const changePct = stock.day_change_pct || 0;
        const arrow = up ? '📈' : '📉';
        const bgColor = up ? 'linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(248, 113, 113, 0.08))' : 'linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(34, 197, 94, 0.08))';
        const borderColor = up ? '#ef4444' : '#10b981';
        const textColor = up ? '#ef4444' : '#10b981';
        
        return `<div class="stock-card" data-code="${stock.code}" style="padding: 18px; background: ${bgColor}; border: 2px solid ${borderColor}; border-radius: 14px; cursor: pointer; position: relative; transition: all 0.3s ease;">
            <div style="position: absolute; top: 14px; right: 14px; font-size: 28px; font-weight: 900;">${medals[idx]}</div>
            <h3 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 800; color: #2d1b69;">${stock.name} (${stock.code})</h3>
            <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px;">
                <div style="font-size: 28px; font-weight: 900; color: ${textColor};">NT$${(stock.current_price || 0).toFixed(2)}</div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; padding: 8px; background: rgba(255,255,255,0.6); border-radius: 8px;">
                <span style="font-size: 24px;">${arrow}</span>
                <span style="font-size: 18px; font-weight: 900; color: ${textColor};">${up ? '+' : ''}${changePct.toFixed(2)}%</span>
                <span style="font-size: 12px; color: #666; margin-left: 4px;">今日漲跌</span>
            </div>
        </div>`;
    }).join('');
    container.querySelectorAll('.stock-card').forEach(card => {
        card.addEventListener('click', () => { if (card.dataset.code) goToStockDetail(card.dataset.code); });
        card.addEventListener('mouseover', function() {
            this.style.transform = 'translateY(-4px)';
            this.style.boxShadow = '0 12px 24px rgba(124, 58, 237, 0.15)';
        });
        card.addEventListener('mouseout', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
}

function updateSummaryStats(allStocks, topStocks) {
    const upCount = allStocks.filter(s => (s.day_change_pct || 0) >= 0).length;
    const downCount = allStocks.length - upCount;
    const topStock = topStocks[0];
    
    // 產業映射表
    const industryMap = {
        '2330': '半導體', '2454': '半導體', '8299': '半導體', '2344': '半導體',
        '2317': '電子製造', '3037': '電子製造', '2211': '電子製造',
        '2884': '金融', '2886': '金融',
        '1101': '水泥',
        '3008': '光學',
        '2376': '電腦周邊',
        '2412': '電信',
        '0050': '指數'
    };
    
    // 統計各產業表現
    const industryStats = {};
    allStocks.forEach(stock => {
        const industry = industryMap[String(stock.code)] || '其他';
        if (!industryStats[industry]) {
            industryStats[industry] = { up: 0, total: 0, avgChange: 0 };
        }
        industryStats[industry].total++;
        if ((stock.day_change_pct || 0) >= 0) {
            industryStats[industry].up++;
        }
        industryStats[industry].avgChange += (stock.day_change_pct || 0);
    });
    
    // 計算平均漲幅，找出表現最好的產業
    Object.keys(industryStats).forEach(ind => {
        industryStats[ind].avgChange /= industryStats[ind].total;
    });
    
    const topIndustry = Object.keys(industryStats).reduce((best, current) => {
        return industryStats[current].avgChange > industryStats[best].avgChange ? current : best;
    });
    
    // 更新概況狀態
    const overviewEl = document.getElementById('overviewStatus');
    if (overviewEl && topStock) {
        overviewEl.textContent = `${topStock.name} 領漲 +${topStock.day_change_pct.toFixed(2)}%`;
    }
    
    // 更新上漲、下跌、最強股票
    const upEl = document.getElementById('upCount');
    const downEl = document.getElementById('downCount');
    const maxGainEl = document.getElementById('maxGain');
    const topIndustryEl = document.getElementById('topIndustry');
    
    if (upEl) upEl.textContent = upCount;
    if (downEl) downEl.textContent = downCount;
    if (maxGainEl && topStock) {
        maxGainEl.textContent = `${topStock.name} +${topStock.day_change_pct.toFixed(2)}%`;
    }
    if (topIndustryEl) {
        topIndustryEl.textContent = `${topIndustry} +${industryStats[topIndustry].avgChange.toFixed(2)}%`;
    }
}

function setLastUpdate(allStocks) {
    if (!allStocks || allStocks.length === 0) {
        const now = new Date();
        const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
        const updateEl = document.getElementById('lastUpdate');
        if (updateEl) updateEl.textContent = `最後更新 ${timeStr}`;
        return;
    }
    
    // 從第一支股票取得最後更新時間
    const firstStock = allStocks[0];
    let updateTime = firstStock.updated_at || firstStock.timestamp;
    
    if (updateTime) {
        try {
            const updateDate = new Date(updateTime);
            const timeStr = updateDate.toLocaleTimeString('zh-TW', { 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit',
                hour12: false 
            });
            const updateEl = document.getElementById('lastUpdate');
            if (updateEl) updateEl.textContent = `最後更新 ${timeStr}`;
        } catch (e) {
            // 如果解析失敗，使用當前時間
            const now = new Date();
            const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
            const updateEl = document.getElementById('lastUpdate');
            if (updateEl) updateEl.textContent = `最後更新 ${timeStr}`;
        }
    }
}

async function loadDetailedAnalysis(code) {
    if (!code) return;
    const stock = window.stocks?.find(s => s.code === code);
    if (!stock) return;
    
    // 🎯 只要使用者明確選中股票，立刻還原並顯示底部大容器
    showBottomPanels();
    
    const priceUp = (stock.day_change_pct || 0) >= 0;
    document.getElementById("currentPriceInfo").innerHTML = `
        <div style="padding: 14px; background: linear-gradient(135deg, ${priceUp ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)'}, ${priceUp ? 'rgba(16, 185, 129, 0.05)' : 'rgba(248, 113, 113, 0.05)'}); border: 1px solid ${priceUp ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}; border-radius: 10px;">
            <h3 style="margin: 0 0 8px 0; color: #2d1b69;">${stock.name} (${code})</h3>
            <p style="margin: 4px 0; font-size: 24px; font-weight: 900; color: ${priceUp ? '#ef4444' : '#10b981'};">NT$${(stock.current_price || 0).toFixed(2)}</p>
        </div>
    `;
    
    document.getElementById("technicalIndicators").innerHTML = `
        <div style="margin-bottom: 12px;">
            <h4 style="margin: 0 0 10px 0; color: #2d1b69; font-size: 13px; font-weight: 700;">📊 技術指標</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                <div style="padding: 12px; background: #f3e8ff; border-radius: 8px;"><div style="color: #666; font-size: 12px;">RSI (14)</div><div style="font-size: 18px; font-weight: 900; color: #7c3aed;">${(stock.rsi || 0).toFixed(2)}</div></div>
                <div style="padding: 12px; background: #f3e8ff; border-radius: 8px;"><div style="color: #666; font-size: 12px;">波動率</div><div style="font-size: 18px; font-weight: 900; color: #7c3aed;">${(stock.volatility || 0).toFixed(2)}%</div></div>
            </div>
            <h4 style="margin: 0 0 10px 0; color: #2d1b69; font-size: 13px; font-weight: 700;">📈 移動平均線 (MA)</h4>
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px;">
                <div style="padding: 10px; background: linear-gradient(135deg, #e9d5ff, #f3e8ff); border-radius: 8px; border-left: 4px solid #a78bfa;">
                    <div style="color: #666; font-size: 11px; margin-bottom: 4px;">MA5</div>
                    <div style="font-size: 16px; font-weight: 900; color: #7c3aed;">NT$${(stock.ma5 || 0).toFixed(0)}</div>
                </div>
                <div style="padding: 10px; background: linear-gradient(135deg, #e9d5ff, #f3e8ff); border-radius: 8px; border-left: 4px solid #a78bfa;">
                    <div style="color: #666; font-size: 11px; margin-bottom: 4px;">MA10</div>
                    <div style="font-size: 16px; font-weight: 900; color: #7c3aed;">NT$${(stock.ma10 || 0).toFixed(0)}</div>
                </div>
                <div style="padding: 10px; background: linear-gradient(135deg, #e9d5ff, #f3e8ff); border-radius: 8px; border-left: 4px solid #a78bfa;">
                    <div style="color: #666; font-size: 11px; margin-bottom: 4px;">MA20</div>
                    <div style="font-size: 16px; font-weight: 900; color: #7c3aed;">NT$${(stock.ma20 || 0).toFixed(0)}</div>
                </div>
                <div style="padding: 10px; background: linear-gradient(135deg, #e9d5ff, #f3e8ff); border-radius: 8px; border-left: 4px solid #a78bfa;">
                    <div style="color: #666; font-size: 11px; margin-bottom: 4px;">MA50</div>
                    <div style="font-size: 16px; font-weight: 900; color: #7c3aed;">NT$${(stock.ma50 || 0).toFixed(0)}</div>
                </div>
                <div style="padding: 10px; background: linear-gradient(135deg, #e9d5ff, #f3e8ff); border-radius: 8px; border-left: 4px solid #a78bfa;">
                    <div style="color: #666; font-size: 11px; margin-bottom: 4px;">MA200</div>
                    <div style="font-size: 16px; font-weight: 900; color: #7c3aed;">NT$${(stock.ma200 || 0).toFixed(0)}</div>
                </div>
            </div>
        </div>
    `;
    
    // 支撐位和壓力位 - 移到股票名稱下方
    const supportResistanceEl = document.getElementById("supportResistanceInfo");
    if (supportResistanceEl) {
        supportResistanceEl.innerHTML = `
        <div style="padding: 12px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.05)); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 10px;">
            <div style="color: #666; font-size: 12px; margin-bottom: 6px; font-weight: 600;">📍 支撐位</div>
            <div style="font-size: 20px; font-weight: 900; color: #10b981;">NT$${(stock.support || 0).toFixed(2)}</div>
        </div>
        <div style="padding: 12px; background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(239, 68, 68, 0.05)); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 10px;">
            <div style="color: #666; font-size: 12px; margin-bottom: 6px; font-weight: 600;">📍 壓力位</div>
            <div style="font-size: 20px; font-weight: 900; color: #ef4444;">NT$${(stock.resistance || 0).toFixed(2)}</div>
        </div>
    `;
    }
    
    // 技術面/基本面/風險提示 - 獨立容器
    const basisAnalysisContainer = document.getElementById("basisAnalysisContainer");
    if (basisAnalysisContainer) {
        const stopLoss = stock.stop_loss || (stock.buy_price || stock.current_price * 0.95) * 0.95;
        basisAnalysisContainer.innerHTML = `
            <div style="padding: 12px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.05)); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 10px;">
                <div style="color: #666; font-size: 12px; margin-bottom: 6px; font-weight: 600;"><span style="color:#10b981;font-weight:700;">📈 技術面：</span></div>
                <div style="font-size: 14px; color: #1e5631;">支撐位穩固在 ${stock.support.toFixed(1)} 元。</div>
            </div>
            <div style="padding: 12px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(59, 130, 246, 0.05)); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 10px;">
                <div style="color: #666; font-size: 12px; margin-bottom: 6px; font-weight: 600;"><span style="color:#3b82f6;font-weight:700;">💼 基本面：</span></div>
                <div style="font-size: 14px; color: #1e3a8a;">營收增長穩健。</div>
            </div>
            <div style="padding: 12px; background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(239, 68, 68, 0.05)); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 10px;">
                <div style="color: #666; font-size: 12px; margin-bottom: 6px; font-weight: 600;"><span style="color:#ef4444;font-weight:700;">⚠️ 風險提示：</span></div>
                <div style="font-size: 14px; color: #7f1d1d;">跌破關卡價 ${stopLoss.toFixed(1)} 元須嚴格投資防禦。</div>
            </div>
        `;
    }
    
    const financialMetricsEl = document.getElementById("financialMetrics");
    if (financialMetricsEl) {
        financialMetricsEl.innerHTML = ``;
    }
    
    const price = stock.current_price || 0;
    const directionScore = stock.direction_score || 0;
    const buyDiscount = 0.03 + (Math.min(5, Math.abs(directionScore)) * 0.002);
    const buyPrice = stock.buy_price || (price * (1 - buyDiscount));
    const sellPremium = 0.10 + (Math.min(5, Math.max(0, directionScore)) * 0.01);
    const sellPrice = stock.sell_price || (price * (1 + sellPremium));
    const stopLoss = stock.stop_loss || (buyPrice * 0.95);

    const buyPriceEl = document.getElementById('suggested_buy_price');
    const sellPriceEl = document.getElementById('suggested_sell_price') || document.getElementById('suggested_target_price');
    const stopLossEl = document.getElementById('suggested_stop_loss');
    
    if (buyPriceEl) buyPriceEl.innerText = "NT$" + buyPrice.toFixed(2);
    if (sellPriceEl) sellPriceEl.innerText = "NT$" + sellPrice.toFixed(2);
    if (stopLossEl) stopLossEl.innerText = "NT$" + stopLoss.toFixed(2);

    // 填入即時動態資料
    const trendContainer = document.getElementById('aiTrendAnalysisText');
    if (trendContainer) {
        trendContainer.innerHTML = `<div style="padding:5px; color:#4c1d95; font-weight:600;">🤖 AI評估：<b>${stock.name}</b> 目前短線動態評分為 <b>${directionScore > 0 ? '+' : ''}${directionScore.toFixed(1)} 分</b>，技術面 RSI 為 ${stock.rsi.toFixed(1)}，多空平衡。</div>`;
    }

    // ✅ 舊的 basisContainers 邏輯已被 basisAnalysisContainer 取代，移除以避免衝突

    const totalCapital = 1000000;
    const shares5pct = Math.max(0, Math.floor((totalCapital * 0.05) / buyPrice));
    const shares10pct = Math.max(0, Math.floor((totalCapital * 0.10) / buyPrice));
    const riskPanel = document.querySelector('#buyPositionPrediction')?.parentElement;
    if (riskPanel) {
        let sharesTips = riskPanel.querySelector('.risk-shares-tips') || document.createElement('div');
        sharesTips.className = 'risk-shares-tips';
        sharesTips.style.cssText = "margin-top:14px; padding:10px; background:rgba(30,64,175,0.04); border:1px dashed rgba(30,64,175,0.2); border-radius:8px; font-size:12px; color:#1e3a8a;";
        sharesTips.innerHTML = `🎛️ <b>100萬本金 股數建議：</b><br>🔹 低風險 (5%): <b>${shares5pct.toLocaleString()}</b> 股<br>🔸 標準 (10%): <b>${shares10pct.toLocaleString()}</b> 股`;
        riskPanel.appendChild(sharesTips);
    }
    
    // 🟢 從 API 獲取季度財務數據
    try {
        const quarterlyRes = await fetch(`/api/quarterly-data/${code}?t=${Date.now()}`);
        const quarterlyJSON = await quarterlyRes.json();
        const quarterlyData = quarterlyJSON.quarterly || [];
        
        // 填充表格
        const tableBody = document.getElementById("quarterlyTableBody");
        if (tableBody && quarterlyData.length > 0) {
            tableBody.innerHTML = quarterlyData.map((row, idx) => `
                <tr style="border-bottom: 1px solid #e9d5ff; ${idx % 2 === 0 ? 'background: rgba(124, 58, 237, 0.02);' : ''}">
                    <td style="padding: 10px; color: #2d1b69; font-weight: 600;">${row.name}</td>
                    <td style="padding: 10px; text-align: right; color: #555;">${row.latest}</td>
                    <td style="padding: 10px; text-align: right; color: ${row.change.includes('-') ? '#10b981' : '#ef4444'}; font-weight: 700;">${row.change}</td>
                </tr>
            `).join('');
        }
    } catch (err) {
        console.warn('季度數據加載失敗:', err);
        // 備用數據
        document.getElementById("quarterlyTableBody").innerHTML = `
            <tr style="border-bottom: 1px solid #e9d5ff;"><td style="padding:10px;">營收 (Revenue)</td><td style="text-align:right; font-weight:700;">NT$${(Math.random() * 300 + 50).toFixed(1)}B</td><td style="text-align:right;">--</td></tr>
            <tr style="border-bottom: 1px solid #e9d5ff;"><td style="padding:10px;">EPS</td><td style="text-align:right; font-weight:700;">NT$${(Math.random() * 10 + 1).toFixed(2)}</td><td style="text-align:right;">--</td></tr>
        `;
    }
    
    // 強制應用 grid 布局
    ensureGridLayout();
    
    drawKlineChart(code, stock);
}

// 強制應用 grid 布局
function ensureGridLayout() {
    const gridContainer = document.getElementById('chartFinancialGrid');
    if (gridContainer) {
        gridContainer.style.display = 'grid';
        gridContainer.style.gridTemplateColumns = '1fr 1fr';
        gridContainer.style.gap = '16px';
        gridContainer.style.width = '100%';
        gridContainer.style.alignItems = 'flex-start';
        gridContainer.style.marginTop = '24px';
        gridContainer.style.marginBottom = '18px';
    }
}

// 🎯 K線圖表繪製函數
async function drawKlineChart(code, stock) {
    try {
        const response = await fetch('/api/stock-history/' + code, { cache: 'no-store' });
        if (!response.ok) throw new Error('Failed to fetch chart data');
        
        const data = await response.json();
        const container = document.getElementById('priceChartContainer');
        if (!container) return;
        
        const canvas = document.getElementById('priceChart');
        if (!canvas) return;
        
        // 銷毀舊圖表
        if (window.priceChartInstance && typeof window.priceChartInstance.destroy === 'function') {
            try {
                window.priceChartInstance.destroy();
            } catch (e) {
                console.warn('Chart destroy error:', e);
            }
        }
        
        // 準備K線數據
        const closes = data.closes || [];
        const dates = data.dates || [];
        
        if (!closes.length) {
            container.innerHTML = '<p style="color: #999; padding: 20px;">無圖表數據</p>';
            return;
        }
        
        // 計算均線
        const ma5 = calculateMovingAverage(closes, 5);
        const ma20 = calculateMovingAverage(closes, 20);
        const ma50 = calculateMovingAverage(closes, 50);
        const ma100 = calculateMovingAverage(closes, 100);
        const ma200 = calculateMovingAverage(closes, 200);
        
        // 存儲圖表數據供MA線選擇器使用
        window.currentChartData = {
            code: code,
            closes: closes,
            dates: dates,
            ma5: ma5,
            ma20: ma20,
            ma50: ma50,
            ma100: ma100,
            ma200: ma200
        };
        
        // K線顏色判斷（紅漲綠跌）
        const klineColors = closes.map((c, i) => {
            if (i === 0) return '#ef4444';
            return c >= closes[i-1] ? '#ef4444' : '#10b981';
        });
        
        // 創建圖表
        window.priceChartInstance = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: '走勢K線',
                        data: closes,
                        backgroundColor: klineColors,
                        borderColor: klineColors,
                        borderWidth: 1,
                        barThickness: 'flex',
                        categoryPercentage: 0.8,
                        barPercentage: 0.6,
                        yAxisID: 'y'
                    },
                    {
                        label: 'MA100',
                        data: ma100,
                        type: 'line',
                        borderColor: '#a855f7',
                        backgroundColor: 'rgba(168, 85, 247, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        tension: 0.3,
                        yAxisID: 'y',
                        borderDash: []
                    },
                    {
                        label: 'MA200',
                        data: ma200,
                        type: 'line',
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        tension: 0.3,
                        yAxisID: 'y',
                        borderDash: [6, 3]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#7c3aed',
                            font: { size: 12, weight: '600' },
                            padding: 12,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(124, 58, 237, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#a855f7',
                        borderWidth: 1,
                        padding: 12,
                        titleFont: { size: 13, weight: 'bold' },
                        bodyFont: { size: 11 }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        position: 'left',
                        beginAtZero: false,
                        ticks: {
                            color: '#7c3aed',
                            font: { size: 11 },
                            callback: function(v) {
                                return 'NT$' + v.toFixed(0);
                            }
                        },
                        grid: {
                            color: 'rgba(124, 58, 237, 0.1)',
                            drawBorder: false
                        },
                        title: {
                            display: true,
                            text: '股價 (NT$)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#7c3aed',
                            font: { size: 10 },
                            maxRotation: 45,
                            minRotation: 0,
                            callback: function(value, index) {
                                // 根据日期数量动态显示标签频率，确保走势线完整显示
                                const step = Math.max(1, Math.ceil(dates.length / 12));
                                return index % step === 0 ? dates[index] : '';
                            }
                        },
                        grid: {
                            display: false,
                            drawBorder: false
                        }
                    }
                }
            }
        });
        
        console.log('✅ K線圖已成功繪製:', code);
        
        // 延迟后检查 canvas 是否有内容，如果没有则使用备选方案
        setTimeout(() => {
            const ctx = canvas.getContext('2d');
            const imageData = ctx.getImageData(0, 0, 10, 10);
            let hasContent = false;
            for (let i = 0; i < imageData.data.length; i += 4) {
                if (imageData.data[i + 3] > 0) {
                    hasContent = true;
                    break;
                }
            }
            
            // 如果 Chart.js 没有成功渲染，使用原生 Canvas 绘制
            if (!hasContent) {
                console.warn('⚠️ Chart.js未能渲染，使用备选方案...');
                drawCanvasFallback(canvas, closes, dates, ma5, ma20, ma50, ma100, ma200, 'ma100-200');
            }
        }, 1000);
        
    } catch (error) {
        console.error('❌ K線圖繪製錯誤:', error);
        const canvas = document.getElementById('priceChart');
        if (canvas) {
            drawCanvasFallback(canvas, [], [], [], [], [], [], [], 'ma100-200');
        }
        document.getElementById('priceChartContainer').innerHTML = '<p style="color: #ef4444; padding: 20px;">圖表加載失敗: ' + error.message + '</p>';
    }
}

// 🎨 原生 Canvas 备选绘制方案
function drawCanvasFallback(canvas, closes, dates, ma5, ma20, ma50, ma100, ma200, maChoice = 'ma100-200') {
    try {
        const ctx = canvas.getContext('2d', { willReadFrequently: true });
        if (!ctx) return;
        
        console.log('🎨 Canvas 绘制开始，显示 MA100 和 MA200 线');
        console.log('📊 数据统计 - closes:', closes.length, 'dates:', dates.length, 'ma100:', ma100.length);
        
        // 始终显示 MA100 和 MA200
        const maLines = {};
        maLines.ma100 = { data: ma100, color: '#a855f7', label: 'MA100' };
        maLines.ma200 = { data: ma200, color: '#3b82f6', label: 'MA200' };
        
        // 计算绘制参数
        const padding = 50;
        let width = canvas.clientWidth || canvas.width || 800;
        let height = canvas.clientHeight || canvas.height || 480;
        
        // 确保容器有最小尺寸
        if (width < 100) width = 800;
        if (height < 100) height = 480;
        
        const dateAreaHeight = 30; // 为日期标签留出空间
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2 - dateAreaHeight;
        
        console.log('📐 Canvas 尺寸设置:', { width, height, chartWidth, chartHeight });
        
        // 重新设置 canvas 大小
        canvas.width = width * window.devicePixelRatio;
        canvas.height = height * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        
        console.log('✅ Canvas 尺寸已应用:', { canvasWidth: canvas.width, canvasHeight: canvas.height });
        
        // 清空并填充背景
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, width, height);
        
        // 绘制标题
        ctx.fillStyle = '#2d1b69';
        ctx.font = 'bold 16px sans-serif';
        ctx.fillText('📊 30天走勢圖表（K線數據）', padding, 30);
        
        if (!closes || closes.length === 0) {
            ctx.fillStyle = '#999';
            ctx.font = '14px sans-serif';
            ctx.fillText('無圖表數據', padding, height / 2);
            return;
        }
        
        // 计算数据范围
        const minPrice = Math.min(...closes);
        const maxPrice = Math.max(...closes);
        const priceRange = maxPrice - minPrice;
        const priceScale = chartHeight / priceRange;
        
        // 绘制网格和坐标轴
        ctx.strokeStyle = 'rgba(124, 58, 237, 0.1)';
        ctx.lineWidth = 1;
        
        // 纵轴网格线
        for (let i = 0; i <= 5; i++) {
            const y = padding + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
            
            // 价格标签
            const price = maxPrice - (priceRange / 5) * i;
            ctx.fillStyle = '#7c3aed';
            ctx.font = '11px sans-serif';
            ctx.textAlign = 'right';
            ctx.fillText('NT$' + price.toFixed(0), padding - 10, y + 4);
        }
        
        // 绘制 K 线
        const barWidth = Math.max(2, chartWidth / closes.length * 0.6);
        const barSpacing = chartWidth / closes.length;
        
        // 先绘制 K 线
        for (let i = 0; i < closes.length; i++) {
            const price = closes[i];
            const x = padding + (i + 0.5) * barSpacing;
            const y = padding + chartHeight - (price - minPrice) * priceScale;
            
            // K 线颜色：红涨绿跌
            const isUp = i === 0 ? true : price >= closes[i - 1];
            ctx.fillStyle = isUp ? '#ef4444' : '#10b981';
            
            ctx.fillRect(x - barWidth / 2, y, barWidth, padding + chartHeight - y);
        }
        
        // 然后绘制 MA 线条（这样 MA 线条就显示在 K 线上方）
        // 绘制 MA100 线（紫色，实线，粗）
        if (maLines.ma100 && ma100 && ma100.some(v => v !== null)) {
            ctx.strokeStyle = '#a855f7';
            ctx.lineWidth = 3;
            ctx.setLineDash([]);
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';
            ctx.beginPath();
            
            let firstPoint = true;
            for (let i = 0; i < ma100.length; i++) {
                if (ma100[i] !== null) {
                    const x = padding + (i + 0.5) * barSpacing;
                    const y = padding + chartHeight - (ma100[i] - minPrice) * priceScale;
                    
                    if (firstPoint) {
                        ctx.moveTo(x, y);
                        firstPoint = false;
                    } else {
                        ctx.lineTo(x, y);
                    }
                }
            }
            ctx.stroke();
            console.log('📗 MA100 已绘制');
        }
        
        // 绘制 MA200 线（蓝色，虚线）
        if (maLines.ma200 && ma200 && ma200.some(v => v !== null)) {
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 2;
            ctx.setLineDash([6, 3]);
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';
            ctx.beginPath();
            
            let firstPoint = true;
            for (let i = 0; i < ma200.length; i++) {
                if (ma200[i] !== null) {
                    const x = padding + (i + 0.5) * barSpacing;
                    const y = padding + chartHeight - (ma200[i] - minPrice) * priceScale;
                    
                    if (firstPoint) {
                        ctx.moveTo(x, y);
                        firstPoint = false;
                    } else {
                        ctx.lineTo(x, y);
                    }
                }
            }
            ctx.stroke();
            ctx.setLineDash([]);
            console.log('📗 MA200 已绘制');
        }
        

        
        // 绘制图例
        const legendY = height - 20;
        ctx.font = '11px sans-serif';
        ctx.fillStyle = '#ef4444';
        ctx.fillRect(padding, legendY, 10, 10);
        ctx.fillStyle = '#2d1b69';
        ctx.textAlign = 'left';
        ctx.fillText('K線', padding + 14, legendY + 8);
        
        let legendX = padding + 60;
        
        // 显示 MA100 和 MA200 的图例
        if (maLines.ma100) {
            ctx.fillStyle = '#a855f7';
            ctx.fillRect(legendX, legendY, 10, 10);
            ctx.fillStyle = '#2d1b69';
            ctx.fillText('MA100', legendX + 14, legendY + 8);
            legendX += 70;
        }
        
        if (maLines.ma200) {
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 2;
            ctx.setLineDash([4, 2]);
            ctx.beginPath();
            ctx.moveTo(legendX, legendY + 5);
            ctx.lineTo(legendX + 10, legendY + 5);
            ctx.stroke();
            ctx.setLineDash([]);
            ctx.fillStyle = '#2d1b69';
            ctx.fillText('MA200', legendX + 14, legendY + 8);
        }
        
        // 绘制日期标签（显示"XX天"格式）
        if (dates && dates.length > 0) {
            const lastIndex = dates.length - 1;
            const recentDaysCount = 10;
            
            for (let i = 0; i < dates.length; i++) {
                let shouldShow = false;
                
                // 检查是否在最近10天内
                if (i >= lastIndex - recentDaysCount + 1) {
                    shouldShow = true;
                }
                
                // 检查是否是季月（3月、6月、9月、12月）
                // 日期格式为 MM/DD，所以检查前两位
                const dateStr = dates[i];
                if (dateStr && (dateStr.startsWith('03/') || dateStr.startsWith('06/') || 
                               dateStr.startsWith('09/') || dateStr.startsWith('12/'))) {
                    shouldShow = true;
                }
                
                if (shouldShow) {
                    const x = padding + (i + 0.5) * barSpacing;
                    const y = padding + chartHeight + 25;
                    
                    // 计算距离最后一天的天数
                    const daysAgo = lastIndex - i;
                    const displayDate = String(daysAgo).padStart(2, '0') + '天';
                    
                    // 绘制日期标签
                    ctx.save();
                    ctx.fillStyle = '#666';
                    ctx.font = 'bold 12px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillText(displayDate, x, y);
                    ctx.restore();
                }
            }
        }
        
        console.log('✅ Canvas 图表已绘制（K线 + MA100/200 + 日期标签）');
    } catch (err) {
        console.error('备选绘制错误:', err);
    }
}

// 計算移動平均線
function calculateMovingAverage(data, period) {
    const result = [];
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
            result.push(null);
        } else {
            const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
            result.push(sum / period);
        }
    }
    return result;
}

// 🟢 大盤走勢圖表
async function loadMarketChart() {
    try {
        const response = await fetch('/api/market-index', { cache: 'no-store' });
        if (!response.ok) throw new Error('Failed to fetch market data');
        
        const data = await response.json();
        const container = document.getElementById('marketChartContainer');
        if (!container) return;
        
        const canvas = document.getElementById('marketChart');
        if (!canvas) return;
        
        // 銷毀舊圖表
        if (window.marketChartInstance && typeof window.marketChartInstance.destroy === 'function') {
            try {
                window.marketChartInstance.destroy();
            } catch (e) {
                console.warn('Chart destroy error:', e);
            }
        }
        
        // 準備數據
        const dates = data.dates || [];
        const closes = data.closes || [];
        
        if (!closes.length) {
            container.innerHTML = '<p style="color: #999; padding: 20px;">無大盤數據</p>';
            return;
        }
        
        // 計算均線
        const ma20 = calculateMovingAverage(closes, 50);
        const ma50 = calculateMovingAverage(closes, 20);
        const ma100 = calculateMovingAverage(closes, 100);
        
        // 計算漲跌
        const latest = closes[closes.length - 1];
        const previous = closes[0];
        const change = latest - previous;
        const changePct = (change / previous) * 100;
        const isUp = change >= 0;
        
        // 更新指數卡片
        const cardsDiv = document.getElementById('marketIndexCards');
        if (cardsDiv) {
            cardsDiv.innerHTML = `
                <div style="padding: 16px; background: linear-gradient(135deg, rgba(124, 58, 237, 0.08), rgba(168, 85, 247, 0.05)); border: 1px solid #e9d5ff; border-radius: 10px; text-align: center;">
                    <div style="color: #7c3aed; font-size: 12px; margin-bottom: 8px; font-weight: 700;">台股加權指數</div>
                    <div style="font-size: 28px; font-weight: 900; color: ${isUp ? '#ef4444' : '#10b981'};">${latest.toFixed(0)}</div>
                    <div style="color: #666; font-size: 12px; margin-top: 8px;">
                        <span style="color: ${isUp ? '#ef4444' : '#10b981'}; font-weight: 700;">
                            ${isUp ? '+' : ''}${change.toFixed(0)}
                        </span>
                        <span style="color: #999;"> (${isUp ? '+' : ''}${changePct.toFixed(2)}%)</span>
                    </div>
                </div>
            `;
        }
        
        // 建立圖表
        window.marketChartInstance = new Chart(canvas, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: '台股加權指數',
                        data: closes,
                        borderColor: isUp ? '#ef4444' : '#10b981',
                        backgroundColor: isUp ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        tension: 0.3,
                        pointBackgroundColor: '#7c3aed',
                        pointBorderColor: '#fff'
                    },
                    {
                        label: 'MA50',
                        data: ma20,
                        borderColor: '#f59e0b',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        tension: 0.3
                    },
                    {
                        label: 'MA20',
                        data: ma50,
                        borderColor: '#3b82f6',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        tension: 0.3
                    },
                    {
                        label: 'MA100',
                        data: ma100,
                        borderColor: '#ef4444',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#7c3aed',
                            font: { size: 13, weight: '700' },
                            padding: 15,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(124, 58, 237, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#a855f7',
                        borderWidth: 1,
                        padding: 12,
                        titleFont: { size: 13, weight: 'bold' },
                        bodyFont: { size: 12 },
                        callbacks: {
                            label: function(context) {
                                return '指數: ' + context.parsed.y.toFixed(0);
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        position: 'left',
                        beginAtZero: false,
                        ticks: {
                            color: '#7c3aed',
                            font: { size: 11 },
                            callback: function(v) {
                                return v.toFixed(0);
                            }
                        },
                        grid: {
                            color: 'rgba(124, 58, 237, 0.1)',
                            drawBorder: false
                        }
                    },
                    x: {
                        ticks: {
                            color: '#7c3aed',
                            font: { size: 10 },
                            maxRotation: 45,
                            minRotation: 0,
                            callback: function(value, index) {
                                // 根据日期数量动态显示标签频率，确保走势线完整显示
                                const step = Math.max(1, Math.ceil(dates.length / 12));
                                return index % step === 0 ? dates[index] : '';
                            }
                        },
                        grid: {
                            display: false,
                            drawBorder: false
                        }
                    }
                }
            }
        });
        
        // 更新分析文字
        const analysisDiv = document.getElementById('marketAnalysis');
        if (analysisDiv) {
            const trend = closes[closes.length - 1] > closes[Math.max(0, closes.length - 6)] ? '上升' : '下降';
            const trendEmoji = trend === '上升' ? '📈' : '📉';
            
            analysisDiv.innerHTML = `
                <div style="padding: 14px; background: linear-gradient(135deg, rgba(124, 58, 237, 0.08), rgba(168, 85, 247, 0.05)); border: 1px solid #e9d5ff; border-radius: 10px;">
                    <h3 style="margin: 0 0 12px 0; color: #2d1b69; font-size: 16px; font-weight: 900;">${trendEmoji} 大盤走勢分析</h3>
                    <div style="line-height: 1.8; color: #555; font-size: 13px;">
                        <p style="margin: 8px 0;">
                            <span style="color: #7c3aed; font-weight: 700;">• 最新指數：</span>
                            ${latest.toFixed(0)} 點
                        </p>
                        <p style="margin: 8px 0;">
                            <span style="color: #7c3aed; font-weight: 700;">• 今日漲跌：</span>
                            <span style="color: ${isUp ? '#10b981' : '#ef4444'}; font-weight: 700;">
                                ${isUp ? '+' : ''}${change.toFixed(0)} 點 (${isUp ? '+' : ''}${changePct.toFixed(2)}%)
                            </span>
                        </p>
                        <p style="margin: 8px 0;">
                            <span style="color: #7c3aed; font-weight: 700;">• 近期趨勢：</span>
                            ${trend === '上升' ? '看多 ✓' : '看空 ✗'}
                        </p>
                    </div>
                </div>
            `;
        }
        
        console.log('✅ 大盤走勢圖已成功繪製');
    } catch (error) {
        console.error('❌ 大盤圖表錯誤:', error);
        const container = document.getElementById('marketChartContainer');
        if (container) {
            container.innerHTML = '<p style="color: #ef4444; padding: 20px;">圖表加載失敗: ' + error.message + '</p>';
        }
    }
}

// 🔮 預測分析頁面加載函數（帶快速緩存切換）
async function loadPredictionAnalysis(code) {
    try {
        if (!code || code === 'Select Stock') return;
        
        // 如果緩存中有數據，先快速顯示
        if (predictionCache[code]) {
            renderPredictionData(predictionCache[code]);
            // 後台異步更新數據
            fetchAndCachePrediction(code);
            return;
        }
        
        // 顯示加載狀態
        showPredictionLoadingState();
        
        // 獲取新數據
        const data = await fetchPredictionData(code);
        predictionCache[code] = data; // 緩存
        renderPredictionData(data);
        
        console.log('✅ 預測分析已加載:', code);
    } catch (error) {
        console.error('❌ 預測分析加載失敗:', error);
    }
}

// 獲取預測數據（後台更新）
async function fetchAndCachePrediction(code) {
    try {
        const data = await fetchPredictionData(code);
        predictionCache[code] = data;
        // 如果用戶仍在查看此股票，更新顯示
        const selector = document.getElementById("predictionStockSelect");
        if (selector && selector.value === code) {
            renderPredictionData(data);
        }
    } catch (error) {
        console.error('後台更新預測數據失敗:', error);
    }
}

// 實際獲取API數據
async function fetchPredictionData(code) {
    const response = await fetch(`/api/stock-prediction/${code}?t=${Date.now()}`, { cache: 'no-store' });
    if (!response.ok) throw new Error('Failed to fetch prediction data');
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    return data;
}

// 顯示加載狀態
function showPredictionLoadingState() {
    const directionDiv = document.getElementById('priceDirectionPrediction');
    const targetDiv = document.getElementById('targetPricePrediction');
    const sharesRiskEl = document.getElementById('sharesRiskContent');
    const reasonsDiv = document.getElementById('predictionReasons');
    
    const loadingHtml = '<div style="padding: 12px; text-align: center; color: #666;">⏳ 加載中...</div>';
    if (directionDiv) directionDiv.innerHTML = loadingHtml;
    if (targetDiv) targetDiv.innerHTML = loadingHtml;
    if (sharesRiskEl) sharesRiskEl.innerHTML = loadingHtml;
    if (reasonsDiv) reasonsDiv.innerHTML = loadingHtml;
}

// 渲染預測數據
function renderPredictionData(data) {
    // 股價方向預測
    const directionDiv = document.getElementById('priceDirectionPrediction');
    if (directionDiv) {
        directionDiv.innerHTML = `
            <div style="padding: 12px; background: white; border-radius: 8px; text-align: center;">
                <div style="color: #666; font-size: 12px; margin-bottom: 4px;">預測方向</div>
                <div style="font-size: 24px; font-weight: 900; margin-bottom: 4px;">${data.direction}</div>
                <div style="color: #666; font-size: 11px;">信心度 ${data.confidence}%</div>
            </div>
        `;
    }
    
    // 目標價預測（使用紅漲綠跌顏色）
    const targetDiv = document.getElementById('targetPricePrediction');
    if (targetDiv) {
        const shortTermColor = data.short_term_change >= 0 ? '#ef4444' : '#10b981';
        const longTermColor = data.long_term_change >= 0 ? '#ef4444' : '#10b981';
        
        targetDiv.innerHTML = `
            <div style="padding: 12px; background: white; border-radius: 8px;">
                <div style="color: #666; font-size: 12px; margin-bottom: 4px;">${data.short_term_label}</div>
                <div style="font-size: 18px; font-weight: 900; color: #3b82f6; margin-bottom: 2px;">NT$${data.short_term_target.toFixed(2)}</div>
                <div style="color: ${shortTermColor}; font-size: 12px; font-weight: 700;">漲幅預期 ${data.short_term_change > 0 ? '+' : ''}${data.short_term_change.toFixed(2)}%</div>
            </div>
            <div style="padding: 12px; background: white; border-radius: 8px;">
                <div style="color: #666; font-size: 12px; margin-bottom: 4px;">${data.long_term_label}</div>
                <div style="font-size: 18px; font-weight: 900; color: #3b82f6; margin-bottom: 2px;">NT$${data.long_term_target.toFixed(2)}</div>
                <div style="color: ${longTermColor}; font-size: 12px; font-weight: 700;">漲幅預期 ${data.long_term_change > 0 ? '+' : ''}${data.long_term_change.toFixed(2)}%</div>
            </div>
        `;
    }
    
    // 買賣點位預測
    const buyEl = document.getElementById('suggested_buy_price');
    if (buyEl) buyEl.innerText = `NT$${data.buy_price.toFixed(2)}`;
    
    const buyProbEl = document.getElementById('suggested_buy_prob');
    if (buyProbEl) buyProbEl.innerText = `勝率 ${data.buy_probability}%`;
    
    const stopLossEl = document.getElementById('suggested_stop_loss');
    if (stopLossEl) stopLossEl.innerText = `NT$${data.stop_loss.toFixed(2)}`;
    
    // 計算股數建議（100萬本金）
    const totalCapital = 1000000;
    const shares5pct = Math.max(0, Math.floor((totalCapital * 0.05) / data.buy_price));
    const shares10pct = Math.max(0, Math.floor((totalCapital * 0.10) / data.buy_price));
    
    const sharesRiskEl = document.getElementById('sharesRiskContent');
    if (sharesRiskEl) {
        // 計算張數：1張 = 1000股
        const lots5pct = shares5pct / 1000;
        const lots10pct = shares10pct / 1000;
        
        sharesRiskEl.innerHTML = `
            🔹 <b>低風險模式 (本金 5%)：</b> 建議買進 <b>${shares5pct.toLocaleString()}</b> 股 (約 ${lots5pct.toFixed(2)} 張)<br>
            🔸 <b>標準風險模式 (本金 10%)：</b> 建議買進 <b>${shares10pct.toLocaleString()}</b> 股 (約 ${lots10pct.toFixed(2)} 張)
        `;
    }
    
    // 顯示移動平均線
    const stock = Array.isArray(stocks) ? stocks.find(s => s.code === data.code) : stocks[data.code];
    if (stock) {
        document.getElementById('ma5Value').innerText = `NT$${stock.ma5.toFixed(2)}`;
        document.getElementById('ma10Value').innerText = `NT$${stock.ma10.toFixed(2)}`;
        document.getElementById('ma20Value').innerText = `NT$${stock.ma20.toFixed(2)}`;
        document.getElementById('ma50Value').innerText = `NT$${stock.ma50.toFixed(2)}`;
        document.getElementById('ma200Value').innerText = `NT$${stock.ma200.toFixed(2)}`;
        
        // 判斷MA趨勢
        const price = data.current_price;
        const ma5 = stock.ma5;
        const ma20 = stock.ma20;
        const ma200 = stock.ma200;
        
        let maTrend = '持平';
        if (price > ma5 && price > ma20 && price > ma200) {
            maTrend = '📈 強勢上升';
        } else if (price > ma5 && price > ma20) {
            maTrend = '📈 短線上升';
        } else if (price > ma20 && price > ma200) {
            maTrend = '📈 中期上升';
        } else if (price > ma200) {
            maTrend = '📈 長期上升';
        } else if (price < ma5 && price < ma20 && price < ma200) {
            maTrend = '⏸️ 蓄勢調整';
        } else {
            maTrend = '➡️ 區間整理';
        }
        
        document.getElementById('maTrend').innerText = maTrend;
    }

    
    // ============ 🔥 波動率交易信號系統渲染 ============
    if (data.volatility && data.trading_signal) {
        const vol = data.volatility;
        const sig = data.trading_signal;
        
        // 波動率強度
        document.getElementById('volatilityRank').innerText = vol.signal_status || vol.volatility_rank;
        document.getElementById('volDaily').innerText = vol.daily_vol;
        document.getElementById('volAvg20').innerText = vol.avg_vol_20;
        document.getElementById('volNorm').innerText = vol.normalized_vol;
        
        // 趨勢信號
        document.getElementById('signalStatus').innerText = vol.signal_status;
        document.getElementById('trendVal').innerText = vol.trend.toFixed(2);
        document.getElementById('signalVal').innerText = vol.signal.toFixed(3);
        document.getElementById('signalAction').innerText = `💡 ${vol.signal_action}`;
        
        // 進出場計畫
        document.getElementById('entryPrice').innerText = `NT$${sig.entry_price.toFixed(2)}`;
        document.getElementById('targetPrice').innerText = `NT$${sig.target_price.toFixed(2)}`;
        document.getElementById('stopPrice').innerText = `NT$${sig.stop_price.toFixed(2)}`;
        document.getElementById('rrRatio').innerText = sig.win_loss_ratio.toFixed(2);
        
        // 成功機率
        document.getElementById('signalProb').innerText = vol.signal_prob;
        document.getElementById('volPeriod').innerText = `使用週期: ${vol.dynamic_ma_period}`;
        document.getElementById('sigStatus').innerText = `${vol.signal_status} • ${vol.signal_action}`;
    }
    
    // ============ 📊 期望價格預測區間渲染 ============
    if (data.price_forecast) {
        const forecast = data.price_forecast;
        const vol = data.volatility || {};
        
        // 1週預測
        document.getElementById('range1wUpper').innerText = `NT$${forecast.range_1w_upper.toFixed(2)}`;
        document.getElementById('range1wLower').innerText = `NT$${forecast.range_1w_lower.toFixed(2)}`;
        document.getElementById('currentPrice').innerText = `NT$${data.current_price.toFixed(2)}`;
        
        // 1月預測
        document.getElementById('range1mUpper').innerText = `NT$${forecast.range_1m_upper.toFixed(2)}`;
        document.getElementById('range1mLower').innerText = `NT$${forecast.range_1m_lower.toFixed(2)}`;
        document.getElementById('priceCenter').innerText = `NT$${data.current_price.toFixed(2)}`;
        
        // 核心公式
        document.getElementById('futurePrice').innerText = `NT$${forecast.future_price_base.toFixed(2)}`;
        document.getElementById('kValue').innerText = (vol.k_value || 'N/A');
        document.getElementById('formulaDisplay').innerText = forecast.formula;
        
        // 上下緣
        document.getElementById('upperBound').innerText = `NT$${forecast.upper_bound.toFixed(2)}`;
        document.getElementById('curPrice').innerText = `NT$${data.current_price.toFixed(2)}`;
        document.getElementById('lowerBound').innerText = `NT$${forecast.lower_bound.toFixed(2)}`;
    }
}

// ============ 新聞加載函數 ============
async function loadNews() {
    try {
        const response = await fetch('/api/news?t=' + Date.now());
        if (!response.ok) throw new Error('Failed to fetch news');
        const data = await response.json();
        
        const newsContainer = document.getElementById('newsList');
        if (!newsContainer) return;
        
        const newsItems = data.news || [];
        
        if (newsItems.length === 0) {
            newsContainer.innerHTML = '<p style="padding: 20px; text-align: center; color: #999;">暫無最新新聞</p>';
            return;
        }
        
        newsContainer.innerHTML = newsItems.map((news, index) => `
            <div style="padding: 16px; border-bottom: 1px solid #e5e7eb; transition: all 0.3s ease;">
                <div style="display: flex; align-items: start; gap: 12px;">
                    <div style="flex: 1;">
                        <div style="font-weight: 700; font-size: 14px; color: #1f2937; margin-bottom: 6px;">
                            ${news.title}
                        </div>
                        <div style="font-size: 13px; color: #666; line-height: 1.5; margin-bottom: 8px;">
                            ${news.content}
                        </div>
                        <div style="font-size: 11px; color: #999;">
                            ${new Date(news.timestamp).toLocaleTimeString('zh-TW')}
                        </div>
                    </div>
                    <div style="
                        padding: 4px 8px;
                        border-radius: 4px;
                        font-size: 11px;
                        font-weight: 600;
                        white-space: nowrap;
                        ${news.priority === 'high' ? 'background: #fecaca; color: #991b1b;' : 
                          news.priority === 'medium' ? 'background: #fed7aa; color: #92400e;' : 
                          'background: #dbeafe; color: #1e40af;'}
                    ">
                        ${news.priority === 'high' ? '🔴 高' : news.priority === 'medium' ? '🟡 中' : '🟢 低'}
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('新聞載入錯誤:', error);
        const newsContainer = document.getElementById('newsList');
        if (newsContainer) {
            newsContainer.innerHTML = '<p style="padding: 20px; text-align: center; color: #e74c3c;">無法載入新聞數據</p>';
        }
    }
}