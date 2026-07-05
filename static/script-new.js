// 台灣股市即時預測儀表板 - 主要 JavaScript 檔案

let currentChart = null;
let marketChart = null;
let stocks = {};
const prevPrices = {};
const MARKET_REFRESH_MS = 10000;

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOMContentLoaded fired");
    setupTabs();
    setupSelectors();
    setupActionButtons();
    document.getElementById("refreshBtn")?.addEventListener("click", () => refreshDashboard(true));
    
    (async () => {
        try {
            console.log("Starting initial data load...");
            const [allStocks, topStocks] = await Promise.all([
                fetchJson("/api/all-stocks"),
                fetchJson("/api/top-stocks"),
            ]);
            console.log("Fetched data - allStocks:", allStocks.length, "topStocks:", topStocks.length);
            cacheStocks(allStocks);
            renderStockGrid(allStocks);
            console.log("Stock grid rendered");
            renderTopStocks(topStocks);
            console.log("Top stocks rendered");
            updateSummaryStats(allStocks, topStocks);
            updateSelectors(allStocks);
            setLastUpdate(allStocks);
            console.log("✅ Initial dashboard loaded");
        } catch (error) {
            console.error("❌ Initial load failed:", error);
        }
    })();

    setInterval(() => refreshDashboard(false), MARKET_REFRESH_MS);
});

async function refreshDashboard(manual = false) {
    if (!manual) {
        console.log("Refreshing dashboard");
    }
    try {
        const [allStocks, topStocks] = await Promise.all([
            fetchJson("/api/all-stocks"),
            fetchJson("/api/top-stocks"),
        ]);
        cacheStocks(allStocks);
        updateStockPrices(allStocks);
        updateTopStocksPrices(topStocks);
        updateSummaryStats(allStocks, topStocks);
        updateSelectors(allStocks);
        setLastUpdate(allStocks);
    } catch (error) {
        console.error("Dashboard refresh failed:", error);
    }
}

function setupTabs() {
    document.querySelectorAll(".tab-btn").forEach((btn) => {
        btn.addEventListener("click", () => showTab(btn.dataset.tab, btn));
    });
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
        if (selected) loadDetailedAnalysis(selected);
    }
    if (tabName === "news" && typeof loadNews === 'function') loadNews();
}

function setupSelectors() {
    document.getElementById("detailStockSelect")?.addEventListener("change", (e) => {
        const selected = e.target.value;
        if (selected) loadDetailedAnalysis(selected);
    });
}

function setupActionButtons() {
    // Add custom button handlers if needed
}

async function loadDetailedAnalysis(stockCode) {
    const container = document.getElementById("analysisContainer");
    if (!container) return;
    
    try {
        const stock = stocks[stockCode] || {};
        container.innerHTML = `
            <div style="padding: 20px;">
                <h3>${stock.name} (${stockCode})</h3>
                <p>現價: NT$${Number(stock.current_price || 0).toFixed(2)}</p>
                <p>漲跌: ${Number(stock.day_change_pct || 0).toFixed(2)}%</p>
            </div>
        `;
        
        // 加載 K線圖
        if (typeof loadKlineChart === 'function') {
            loadKlineChart(stockCode);
        }
    } catch (error) {
        console.error("Failed to load analysis:", error);
    }
}

async function loadMarketChart() {
    const ctx = document.getElementById("marketChartCanvas");
    if (!ctx) return;
    try {
        const data = await fetchJson("/api/market-chart?period=daily");
        if (marketChart) marketChart.destroy();
        const start = data.prices[0] || 0;
        const end = data.prices[data.prices.length - 1] || 0;
        const color = end >= start ? "#dc2626" : "#10b981";
        marketChart = new Chart(ctx, chartConfig("大盤指數", data.labels, data.prices, color));
    } catch (error) {
        console.error("Market chart error:", error);
    }
}

function chartConfig(title, labels, data, color) {
    return {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                borderColor: color,
                backgroundColor: color + "33",
                tension: 0.1,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: false },
            },
        },
    };
}

async function fetchJson(url) {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) {
        throw new Error(`${url} HTTP ${response.status}`);
    }
    return response.json();
}

function cacheStocks(data) {
    if (Array.isArray(data)) {
        data.forEach((stock) => {
            stocks[stock.code] = stock;
        });
    }
}

function setLastUpdate(data) {
    const el = document.getElementById("lastUpdate");
    if (!el) return;
    const latest = data[0]?.last_update;
    const date = latest ? new Date(latest * 1000) : new Date();
    el.dataset.fixed = "1";
    el.textContent = `最後更新 ${date.toLocaleTimeString("zh-TW")}`;
}

function renderStockGrid(data) {
    const grid = document.getElementById("stockGrid");
    if (!grid) return;
    
    grid.innerHTML = data.map(stock => `
        <div class="stock-card" style="border: 1px solid #ddd; padding: 12px; border-radius: 8px; text-align: center;">
            <h4 style="margin: 0;">${stock.name}</h4>
            <p style="margin: 5px 0; font-size: 18px; font-weight: bold; color: ${Number(stock.day_change_pct || 0) >= 0 ? '#dc2626' : '#10b981'};">
                NT$${Number(stock.current_price || 0).toFixed(2)}
            </p>
            <p style="margin: 0; font-size: 14px; color: ${Number(stock.day_change_pct || 0) >= 0 ? '#dc2626' : '#10b981'};">
                ${Number(stock.day_change_pct || 0) >= 0 ? '▲' : '▼'} ${Number(stock.day_change_pct || 0).toFixed(2)}%
            </p>
        </div>
    `).join('');
}

function renderTopStocks(data) {
    const container = document.getElementById("topStocksContainer");
    if (!container) return;
    
    const topThree = data.slice(0, 3);
    container.innerHTML = topThree.map((stock, idx) => `
        <div style="flex: 1; padding: 15px; background: linear-gradient(135deg, #7c3aed, #a855f7); color: white; border-radius: 8px; text-align: center;">
            <div style="font-size: 12px; opacity: 0.8;">Top ${idx + 1}</div>
            <h4 style="margin: 8px 0; font-size: 16px;">${stock.name}</h4>
            <p style="margin: 5px 0; font-size: 20px; font-weight: bold;">NT$${Number(stock.current_price || 0).toFixed(2)}</p>
            <p style="margin: 0; font-size: 14px;">▲ +${Number(stock.day_change_pct || 0).toFixed(2)}%</p>
        </div>
    `).join('');
}

function updateSummaryStats(allStocks, topStocks) {
    let upCount = 0;
    let downCount = 0;
    
    allStocks.forEach(stock => {
        const pct = Number(stock.day_change_pct || 0);
        if (pct > 0) upCount++;
        else if (pct < 0) downCount++;
    });
    
    let bestStockName = "--";
    if (topStocks && topStocks.length > 0) {
        const topStock = topStocks[0];
        const pct = Number(topStock.day_change_pct || 0);
        bestStockName = `${topStock.name} (${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%)`;
    }
    
    const summaryStats = document.querySelector(".summary-stats");
    if (summaryStats) {
        const statDivs = summaryStats.querySelectorAll("div");
        if (statDivs.length >= 6) {
            statDivs[1].textContent = `${upCount} 檔`;
            statDivs[3].textContent = `${downCount} 檔`;
            statDivs[5].textContent = bestStockName;
        }
    }
}

function updateSelectors(allStocks) {
    const selectors = ["chartStockSelect", "detailStockSelect"];
    selectors.forEach(id => {
        const select = document.getElementById(id);
        if (!select) return;
        
        const current = select.value;
        select.innerHTML = '<option value="">選擇股票</option>';
        allStocks.forEach((stock) => {
            const option = document.createElement("option");
            option.value = stock.code;
            option.textContent = `${stock.name} (${stock.code})`;
            select.appendChild(option);
        });
        if (current) select.value = current;
    });
}

function updateStockPrices(data) {
    data.forEach(stock => {
        const card = document.querySelector(`[data-code="${stock.code}"]`);
        if (!card) return;
        
        const price = Number(stock.current_price || 0);
        const priceSpan = card.querySelector('p:nth-of-type(2)');
        if (priceSpan) {
            priceSpan.textContent = `NT$${price.toFixed(2)}`;
        }
        
        const pct = Number(stock.day_change_pct || 0);
        const changeSpan = card.querySelector('p:nth-of-type(3)');
        if (changeSpan) {
            const up = pct >= 0;
            changeSpan.textContent = `${up ? "▲" : "▼"} ${Math.abs(pct).toFixed(2)}%`;
            changeSpan.style.color = up ? "#dc2626" : "#10b981";
        }
        
        prevPrices[stock.code] = price;
    });
}

function updateTopStocksPrices(data) {
    if (!Array.isArray(data) || data.length === 0) return;
    const topThree = data.slice(0, 3);
    const topCards = document.querySelectorAll('[style*="gradient"]');
    
    topCards.forEach((card, idx) => {
        if (idx >= topThree.length) return;
        const stock = topThree[idx];
        const spans = card.querySelectorAll('p');
        if (spans.length >= 2) {
            spans[0].textContent = `NT$${Number(stock.current_price || 0).toFixed(2)}`;
            spans[1].textContent = `▲ +${Number(stock.day_change_pct || 0).toFixed(2)}%`;
        }
    });
}
