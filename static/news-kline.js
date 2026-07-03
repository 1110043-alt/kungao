// 新聞和K線圖表功能模塊

async function loadNews() {
    try {
        const response = await fetch('/api/news', { cache: 'no-store' });
        const responseData = await response.json();
        
        // 处理 API 返回结构：{ data_source, news: [...], timestamp, total }
        const newsArray = responseData.news || responseData || [];
        
        const newsContainer = document.getElementById('newsList');
        if (!newsContainer) return;
        
        let html = '<div style="display: grid; gap: 16px;">';
        
        if (!Array.isArray(newsArray) || newsArray.length === 0) {
            html += '<div style="text-align: center; color: #999; padding: 20px;">暫無新聞資訊</div>';
        } else {
            newsArray.forEach(item => {
                // 根据优先级确定颜色
                let priorityColor = '#3b82f6';  // 默认蓝色
                if (item.priority === 'high') priorityColor = '#dc2626';
                if (item.priority === 'low') priorityColor = '#6b7280';
                
                html += '<div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">';
                html += '<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">';
                html += '<div style="flex: 1;"><h3 style="margin: 0; color: #1f2937; font-size: 16px; font-weight: 600;">' + item.title + '</h3>';
                
                // 格式化时间戳
                let formattedTime = '';
                if (item.timestamp) {
                    const date = new Date(item.timestamp);
                    formattedTime = date.toLocaleString('zh-TW');
                }
                
                html += '<div style="font-size: 12px; color: #666; margin-top: 4px;">' + formattedTime + ' • <span style="color: ' + priorityColor + '; font-weight: 500;">' + (item.type || item.category || '市場') + '</span></div></div>';
                
                // 优先级徽章
                let badgeEmoji = '⚪';
                if (item.priority === 'high') badgeEmoji = '🔴';
                if (item.priority === 'medium') badgeEmoji = '🟡';
                html += '<span style="font-size: 20px; margin-left: 8px;">' + badgeEmoji + '</span></div>';
                
                html += '<p style="margin: 0 0 12px 0; color: #4b5563; line-height: 1.5;">' + (item.description || item.content || '') + '</p>';
                
                html += '</div>';
            });
        }
        
        html += '</div>';
        newsContainer.innerHTML = html;
    } catch (error) {
        console.error('新聞載入錯誤:', error);
        const newsContainer = document.getElementById('newsList');
        if (newsContainer) {
            newsContainer.innerHTML = '<div style="text-align: center; color: #dc2626; padding: 20px;">新聞載入失敗：' + error.message + '</div>';
        }
    }
}

async function loadKlineChart(code) {
    try {
        const response = await fetch('/api/stock-history/' + code, { cache: 'no-store' });
        const data = await response.json();
        const panel = document.getElementById('klineChartPanel');
        if (!panel || !data.dates || data.dates.length === 0) return;
        
        const canvas = document.getElementById('klineChart');
        if (!canvas) return;
        
        if (window.klineChart && typeof window.klineChart.destroy === 'function') {
            try {
                window.klineChart.destroy();
            } catch (e) {
                console.warn('Error destroying previous chart:', e);
            }
        }
        
        // 準備 K 線數據
        const closes = data.closes || [];
        const dates = data.dates || [];
        
        // 計算均線
        const ma20 = calculateMA(closes, 20);
        const ma50 = calculateMA(closes, 50);
        const ma200 = calculateMA(closes, 200);
        
        // 準備 K 線顏色
        const klineColors = closes.map((c, i) => {
            if (i === 0) return '#ef4444';
            return c >= closes[i-1] ? '#ef4444' : '#10b981';
        });
        
        window.klineChart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: 'K 線',
                        data: closes,
                        backgroundColor: klineColors,
                        borderColor: klineColors,
                        borderWidth: 1,
                        borderSkipped: false,
                        barThickness: 'flex',
                        categoryPercentage: 0.8,
                        barPercentage: 0.6
                    },
                    {
                        label: 'MA20',
                        data: ma20,
                        type: 'line',
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        tension: 0.3
                    },
                    {
                        label: 'MA50',
                        data: ma50,
                        type: 'line',
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        tension: 0.3
                    },
                    {
                        label: 'MA200',
                        data: ma200,
                        type: 'line',
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
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
                maintainAspectRatio: true,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#7c3a93',
                            font: { size: 12, weight: '600' },
                            padding: 12,
                            usePointStyle: true,
                            pointStyle: 'line'
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(124, 58, 237, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#a855f7',
                        borderWidth: 1,
                        padding: 12,
                        titleFont: { size: 12, weight: 'bold' },
                        bodyFont: { size: 11 }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            color: '#7c3a93',
                            font: { size: 10 },
                            callback: function(v) {
                                return 'NT$' + v.toFixed(0);
                            }
                        },
                        grid: {
                            color: 'rgba(124, 58, 237, 0.1)',
                            drawBorder: false
                        }
                    },
                    x: {
                        ticks: {
                            color: '#7c3a93',
                            font: { size: 10 },
                            maxRotation: 45,
                            minRotation: 0
                        },
                        grid: {
                            display: false,
                            drawBorder: false
                        }
                    }
                }
            }
        });
        
        console.log('K-line chart loaded for', code);
    } catch (error) {
        console.error('K線圖表錯誤:', error);
    }
}

function calculateMA(data, period) {
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

function initializeNewsSystem() {
    // 加載新聞並設置定時刷新
    loadNews();
    // 每 5 分鐘刷新一次新聞
    setInterval(loadNews, 300000);
}
