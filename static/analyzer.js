// 智能買賣分析功能

// 選中的股票
let selectedAnalyzerStock = '';

// 加載分析器數據
function loadAnalyzerData() {
    const select = document.getElementById('analyzerStockSelect');
    if (!select) {
        console.error('找不到選擇器');
        return;
    }
    
    const stockCode = select.value;
    console.log('✅ 選擇股票:', stockCode);
    
    // 清空下面的結果區域
    const resultContainers = [
        document.getElementById('tradingAnalysisResult'),
        document.getElementById('budgetAdviceResult'),
        document.getElementById('signalsResult')
    ];
    resultContainers.forEach(container => {
        if (container) {
            container.innerHTML = '';
        }
    });
    
    if (!stockCode) {
        const financialDiv = document.getElementById('analyzerFinancialData');
        if (financialDiv) financialDiv.style.display = 'none';
        return;
    }
    
    // 先使用已緩存的股票數據快速顯示（秒級響應）
    const cachedStock = stocks[stockCode];
    if (cachedStock) {
        console.log('⚡ 使用緩存數據快速顯示');
        displayQuarterlyData({ trend: {} }, stockCode, cachedStock);
    }
    
    // 後台更新最新財務數據和股票信息（非阻塞）
    Promise.all([
        fetch(`/api/quarterly-financials/${stockCode}`).then(r => r.json()),
        fetch(`/api/stock/${stockCode}`).then(r => r.json())
    ]).then(([financialData, stockData]) => {
        console.log('📊 已獲取最新財務數據:', financialData);
        console.log('📈 已獲取最新股票數據:', stockData);
        
        // 更新全局緩存
        if (stockData && stockData.analysis) {
            stocks[stockCode].analysis = stockData.analysis;
        }
        
        // 刷新顯示
        displayQuarterlyData(financialData, stockCode, stockData);
    }).catch(e => {
        console.error('❌ 加載最新數據錯誤:', e);
        // 保持快速顯示的緩存數據
    });
}

// 顯示季度數據
function displayQuarterlyData(data, stockCode, stockDataFromAPI) {
    const stock = stocks[stockCode];
    if (!stock) {
        console.warn('找不到股票:', stockCode);
        return;
    }
    
    const currentPrice = stock.analysis?.current_price || 0;
    
    // 更新現價顯示
    const priceDisplay = document.getElementById('currentPriceDisplay');
    if (priceDisplay) {
        priceDisplay.innerHTML = `<div style="display: flex; align-items: center; gap: 20px;">
            <div>
                <div style="font-size: 14px; color: #666;">當前價格</div>
                <div style="font-size: 32px; font-weight: bold; color: #667eea;">$${currentPrice.toFixed(2)}</div>
            </div>
            <div style="flex: 1;">
                <div style="font-size: 12px; color: #666;">股票信息</div>
                <div style="font-size: 16px; color: #333;">
                    📍 ${stock.name} (${stockCode})
                    ${stock.analysis?.change_percent ? `<br>漲跌: <span style="color: ${stock.analysis.change_percent > 0 ? '#28a745' : '#dc3545'}">${stock.analysis.change_percent > 0 ? '+' : ''}${stock.analysis.change_percent.toFixed(2)}%</span>` : ''}
                </div>
            </div>
        </div>`;
    }
    
    // 顯示成長分析
    displayGrowthAnalysis(stock, data);
    
    // 顯示季度表格
    displayQuarterlyTable(data);
    
    // 顯示財務健康指標
    if (data.financials_health && Object.keys(data.financials_health).length > 0) {
        displayFinancialHealth(data.financials_health);
    } else {
        // 如果沒有新數據，從股票分析中提取
        const estimatedHealth = extractHealthFromStock(stock, data);
        if (estimatedHealth && Object.keys(estimatedHealth).length > 0) {
            displayFinancialHealth(estimatedHealth);
        }
    }
    
    // 顯示財務數據容器
    const financialDiv = document.getElementById('analyzerFinancialData');
    if (financialDiv) financialDiv.style.display = 'block';
}

// 顯示公司成長分析
function displayGrowthAnalysis(stock, data) {
    const growthDiv = document.getElementById('growthAnalysis');
    if (!growthDiv) return;
    
    const analysis = stock.analysis || {};
    const currentPrice = parseFloat(analysis.current_price) || 0;
    const high52w = parseFloat(analysis['52_week_high']) || 0;
    const low52w = parseFloat(analysis['52_week_low']) || 0;
    
    // 計算52周漲幅空間
    let upFromLow = 0, downFromHigh = 0;
    if (low52w > 0) upFromLow = ((currentPrice - low52w) / low52w * 100);
    if (high52w > 0) downFromHigh = ((high52w - currentPrice) / high52w * 100);
    
    let html = '<div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px;">';
    
    // 添加52周高點卡片
    if (high52w > 0) {
        const distanceFromHigh = high52w - currentPrice;
        const percentFromHigh = (distanceFromHigh / high52w * 100).toFixed(1);
        html += `<div style="background: linear-gradient(135deg, #fff3cd 0%, #ffe0b2 100%); padding: 12px; border-radius: 8px; border: 2px solid #ffc107;">
            <div style="font-size: 12px; color: #856404; margin-bottom: 3px;">📈 52周最高</div>
            <div style="font-size: 20px; font-weight: bold; color: #ff9800;">$${high52w.toFixed(2)}</div>
            <div style="font-size: 11px; color: #d48806; margin-top: 3px;">距離 ${percentFromHigh}% (${distanceFromHigh.toFixed(2)})</div>
        </div>`;
    }
    
    // 添加52周低點卡片
    if (low52w > 0) {
        const distanceFromLow = currentPrice - low52w;
        const percentFromLow = (distanceFromLow / low52w * 100).toFixed(1);
        html += `<div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 12px; border-radius: 8px; border: 2px solid #28a745;">
            <div style="font-size: 12px; color: #155724; margin-bottom: 3px;">📉 52周最低</div>
            <div style="font-size: 20px; font-weight: bold; color: #28a745;">$${low52w.toFixed(2)}</div>
            <div style="font-size: 11px; color: #0c5e2f; margin-top: 3px;">距離 +${percentFromLow}% (+${distanceFromLow.toFixed(2)})</div>
        </div>`;
    }
    
    const pe = parseFloat(analysis.pe_ratio) || 0;
    const pb = parseFloat(analysis.pb_ratio) || 0;
    
    // 本益比（股價相對於每股利潤）
    if (pe > 0) {
        const peColor = pe < 20 ? '#28a745' : (pe < 30 ? '#ffc107' : '#dc3545');
        const peStatus = pe < 20 ? '✅ 便宜' : (pe < 30 ? '⚠️ 中等' : '❌ 昂貴');
        html += `<div style="background: rgba(${peColor === '#28a745' ? '40,167,69' : (peColor === '#ffc107' ? '255,193,7' : '220,53,69')}, 0.1); padding: 12px; border-radius: 8px; border: 2px solid ${peColor};">
            <div style="font-size: 12px; color: #666; margin-bottom: 3px;">本益比</div>
            <div style="font-size: 20px; font-weight: bold; color: ${peColor};">${pe.toFixed(2)}</div>
            <div style="font-size: 11px; color: #999; margin-top: 3px;">${peStatus}</div>
        </div>`;
    }
    
    // 淨值比（股價相對於每股資產）
    if (pb > 0) {
        const pbColor = pb < 1.5 ? '#28a745' : (pb < 2.5 ? '#ffc107' : '#dc3545');
        const pbStatus = pb < 1.5 ? '✅ 低估' : (pb < 2.5 ? '⚠️ 合理' : '❌ 高估');
        html += `<div style="background: rgba(${pbColor === '#28a745' ? '40,167,69' : (pbColor === '#ffc107' ? '255,193,7' : '220,53,69')}, 0.1); padding: 12px; border-radius: 8px; border: 2px solid ${pbColor};">
            <div style="font-size: 12px; color: #666; margin-bottom: 3px;">淨值比</div>
            <div style="font-size: 20px; font-weight: bold; color: ${pbColor};">${pb.toFixed(2)}</div>
            <div style="font-size: 11px; color: #999; margin-top: 3px;">${pbStatus}</div>
        </div>`;
    }
    
    // 營收成長
    if (data.trend?.revenue_growth !== undefined) {
        const revGrowth = data.trend.revenue_growth;
        const revColor = revGrowth > 0 ? '#28a745' : (revGrowth < 0 ? '#dc3545' : '#999');
        html += `<div style="background: rgba(${revColor === '#28a745' ? '40,167,69' : (revColor === '#dc3545' ? '220,53,69' : '153,153,153')}, 0.1); padding: 12px; border-radius: 8px; border: 2px solid ${revColor};">
            <div style="font-size: 12px; color: #666; margin-bottom: 3px;">營收成長率</div>
            <div style="font-size: 20px; font-weight: bold; color: ${revColor};">${revGrowth > 0 ? '+' : ''}${revGrowth.toFixed(1)}%</div>
            <div style="font-size: 11px; color: #999; margin-top: 3px;">${revGrowth > 5 ? '📈 強勁' : (revGrowth > 0 ? '📊 溫和' : '📉 衰退')}</div>
        </div>`;
    }
    
    // 淨利成長
    if (data.trend?.ni_growth !== undefined) {
        const niGrowth = data.trend.ni_growth;
        const niColor = niGrowth > 0 ? '#28a745' : (niGrowth < 0 ? '#dc3545' : '#999');
        html += `<div style="background: rgba(${niColor === '#28a745' ? '40,167,69' : (niColor === '#dc3545' ? '220,53,69' : '153,153,153')}, 0.1); padding: 12px; border-radius: 8px; border: 2px solid ${niColor};">
            <div style="font-size: 12px; color: #666; margin-bottom: 3px;">淨利成長率</div>
            <div style="font-size: 20px; font-weight: bold; color: ${niColor};">${niGrowth > 0 ? '+' : ''}${niGrowth.toFixed(1)}%</div>
            <div style="font-size: 11px; color: #999; margin-top: 3px;">${niGrowth > 10 ? '💪 高增長' : (niGrowth > 0 ? '📊 正增長' : '⚠️ 衰退')}</div>
        </div>`;
    }
    
    html += '</div>';
    growthDiv.innerHTML = html;
    console.log('成長分析已更新');
}

// 從股票分析中提取財務健康指標
function extractHealthFromStock(stock, data) {
    const analysis = stock.analysis || {};
    const health = {};
    
    // 提取已有的指標
    if (analysis.pe_ratio) health.pe_ratio = parseFloat(analysis.pe_ratio);
    if (analysis.pb_ratio) health.pb_ratio = parseFloat(analysis.pb_ratio);
    
    // 計算利潤率（如果有季度數據）
    if (data.latest_quarter) {
        const latest = data.latest_quarter;
        const previous = data.previous_quarter || {};
        
        // 毛利率
        if (latest.gross_profit && latest.total_revenue) {
            health.gross_margin = (latest.gross_profit / latest.total_revenue) * 100;
        }
        
        // 營業利益率
        if (latest.operating_income && latest.total_revenue) {
            health.operating_margin_calc = (latest.operating_income / latest.total_revenue) * 100;
        }
        
        // 淨利率
        if (latest.net_income && latest.total_revenue) {
            health.net_margin = (latest.net_income / latest.total_revenue) * 100;
        }
        
        // 負債比
        if (latest.total_assets && latest.total_liabilities) {
            health.debt_ratio = (latest.total_liabilities / latest.total_assets) * 100;
        }
    }
    
    return health;
}

// 顯示季度表格
function displayQuarterlyTable(data) {
    const tbody = document.getElementById('quarterlyTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (data.latest_quarter && data.previous_quarter) {
        const latest = data.latest_quarter;
        const previous = data.previous_quarter;
        
        // 營收
        const revenue = `$${(latest.total_revenue / 1e9).toFixed(2)}B`;
        const prevRevenue = `$${(previous.total_revenue / 1e9).toFixed(2)}B`;
        const revGrowth = latest.total_revenue > 0 && previous.total_revenue > 0 
            ? (((latest.total_revenue - previous.total_revenue) / previous.total_revenue) * 100).toFixed(1)
            : '0.0';
        
        let row = `<tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;">營收</td>
            <td style="padding: 10px;">${revenue}</td>
            <td style="padding: 10px;">${prevRevenue}</td>
            <td style="padding: 10px; color: ${revGrowth > 0 ? '#28a745' : (revGrowth < 0 ? '#dc3545' : '#999')};">
                ${revGrowth > 0 ? '+' : ''}${revGrowth}%
            </td>
        </tr>`;
        tbody.innerHTML += row;
        
        // 毛利
        const grossProfit = `$${(latest.gross_profit / 1e9).toFixed(2)}B`;
        const prevGrossProfit = `$${(previous.gross_profit / 1e9).toFixed(2)}B`;
        const gpGrowth = latest.gross_profit > 0 && previous.gross_profit > 0
            ? (((latest.gross_profit - previous.gross_profit) / previous.gross_profit) * 100).toFixed(1)
            : '0.0';
        
        row = `<tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;">毛利</td>
            <td style="padding: 10px;">${grossProfit}</td>
            <td style="padding: 10px;">${prevGrossProfit}</td>
            <td style="padding: 10px; color: ${gpGrowth > 0 ? '#28a745' : (gpGrowth < 0 ? '#dc3545' : '#999')};">
                ${gpGrowth > 0 ? '+' : ''}${gpGrowth}%
            </td>
        </tr>`;
        tbody.innerHTML += row;
        
        // 營業利益
        const opIncome = `$${(latest.operating_income / 1e9).toFixed(2)}B`;
        const prevOpIncome = `$${(previous.operating_income / 1e9).toFixed(2)}B`;
        const oiGrowth = latest.operating_income > 0 && previous.operating_income > 0
            ? (((latest.operating_income - previous.operating_income) / previous.operating_income) * 100).toFixed(1)
            : '0.0';
        
        row = `<tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;">營業利益</td>
            <td style="padding: 10px;">${opIncome}</td>
            <td style="padding: 10px;">${prevOpIncome}</td>
            <td style="padding: 10px; color: ${oiGrowth > 0 ? '#28a745' : (oiGrowth < 0 ? '#dc3545' : '#999')};">
                ${oiGrowth > 0 ? '+' : ''}${oiGrowth}%
            </td>
        </tr>`;
        tbody.innerHTML += row;
        
        // 淨利
        const netIncome = `$${(latest.net_income / 1e9).toFixed(2)}B`;
        const prevNetIncome = `$${(previous.net_income / 1e9).toFixed(2)}B`;
        const niGrowth = latest.net_income > 0 && previous.net_income > 0
            ? (((latest.net_income - previous.net_income) / previous.net_income) * 100).toFixed(1)
            : '0.0';
        
        row = `<tr>
            <td style="padding: 10px;">淨利</td>
            <td style="padding: 10px;">${netIncome}</td>
            <td style="padding: 10px;">${prevNetIncome}</td>
            <td style="padding: 10px; color: ${niGrowth > 0 ? '#28a745' : (niGrowth < 0 ? '#dc3545' : '#999')};">
                ${niGrowth > 0 ? '+' : ''}${niGrowth}%
            </td>
        </tr>`;
        tbody.innerHTML += row;
    }
    
    console.log('季度表格已更新');
}

// 顯示財務健康指標
function displayFinancialHealth(health) {
    const analyzer = document.getElementById('analyzer');
    if (!analyzer) return;
    
    // 查找或創建財務健康容器
    let healthDiv = document.getElementById('financialHealthDiv');
    if (!healthDiv) {
        healthDiv = document.createElement('div');
        healthDiv.id = 'financialHealthDiv';
        const table = document.getElementById('quarterlyTable');
        if (table && table.parentNode) {
            table.parentNode.insertBefore(healthDiv, table.nextSibling);
        }
    }
    
    let html = '<h3 style="margin-top: 30px; margin-bottom: 15px;">💰 財務健康指標</h3>';
    html += '<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 20px;">';
    
    // 本益比
    if (health.pe_ratio && health.pe_ratio > 0) {
        const peColor = health.pe_ratio < 20 ? '#28a745' : (health.pe_ratio < 30 ? '#ffc107' : '#dc3545');
        html += `<div style="background: rgba(${peColor === '#28a745' ? '40,167,69' : (peColor === '#ffc107' ? '255,193,7' : '220,53,69')}, 0.1); padding: 12px; border-radius: 8px; border: 2px solid ${peColor};">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">本益比<br/><span style="font-size: 10px; color: #999;">(股價相對於每股利潤)</span></div>
            <div style="font-size: 20px; font-weight: bold; color: ${peColor};">${health.pe_ratio.toFixed(2)}</div>
            <div style="font-size: 11px; color: #999; margin-top: 3px;">${health.pe_ratio < 20 ? '✅ 便宜' : (health.pe_ratio < 30 ? '⚠️ 中等' : '❌ 昂貴')}</div>
        </div>`;
    }
    
    // 淨值比
    if (health.pb_ratio && health.pb_ratio > 0) {
        const pbColor = health.pb_ratio < 1.5 ? '#28a745' : (health.pb_ratio < 2.5 ? '#ffc107' : '#dc3545');
        html += `<div style="background: rgba(${pbColor === '#28a745' ? '40,167,69' : (pbColor === '#ffc107' ? '255,193,7' : '220,53,69')}, 0.1); padding: 12px; border-radius: 8px; border: 2px solid ${pbColor};">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">淨值比<br/><span style="font-size: 10px; color: #999;">(股價相對於每股資產)</span></div>
            <div style="font-size: 20px; font-weight: bold; color: ${pbColor};">${health.pb_ratio.toFixed(2)}</div>
            <div style="font-size: 11px; color: #999; margin-top: 3px;">${health.pb_ratio < 1.5 ? '✅ 低估' : (health.pb_ratio < 2.5 ? '⚠️ 合理' : '❌ 高估')}</div>
        </div>`;
    }
    
    // 股東權益報酬率
    if (health.return_on_equity && health.return_on_equity > 0) {
        const roeColor = health.return_on_equity > 0.15 ? '#28a745' : (health.return_on_equity > 0.1 ? '#ffc107' : '#dc3545');
        html += `<div style="background: rgba(${roeColor === '#28a745' ? '40,167,69' : (roeColor === '#ffc107' ? '255,193,7' : '220,53,69')}, 0.1); padding: 12px; border-radius: 8px; border: 2px solid ${roeColor};">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">淨利潤率<br/><span style="font-size: 10px; color: #999;">(每元資產的利潤)</span></div>
            <div style="font-size: 20px; font-weight: bold; color: ${roeColor};">${(health.return_on_equity * 100).toFixed(1)}%</div>
            <div style="font-size: 11px; color: #999; margin-top: 3px;">${health.return_on_equity > 0.15 ? '✅ 優秀' : (health.return_on_equity > 0.1 ? '⚠️ 良好' : '❌ 需改善')}</div>
        </div>`;
    }
    
    html += '</div>';
    
    // 利潤率和其他指標
    html += '<div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; margin-bottom: 20px;">';
    
    // 毛利率（售出商品的淨利潤）
    if (health.gross_margin !== undefined) {
        html += `<div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #667eea;">
            <div style="font-size: 12px; color: #666;">毛利率 %</div>
            <div style="font-size: 18px; font-weight: bold; color: #667eea;">${health.gross_margin.toFixed(1)}%</div>
        </div>`;
    }
    
    // 營業利益率（營運效率）
    if (health.operating_margin_calc !== undefined) {
        html += `<div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #667eea;">
            <div style="font-size: 12px; color: #666;">營運利益率 %</div>
            <div style="font-size: 18px; font-weight: bold; color: #667eea;">${health.operating_margin_calc.toFixed(1)}%</div>
        </div>`;
    }
    
    // 淨利率（最終賺取的比例）
    if (health.net_margin !== undefined) {
        html += `<div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #667eea;">
            <div style="font-size: 12px; color: #666;">淨利率 %</div>
            <div style="font-size: 18px; font-weight: bold; color: #667eea;">${health.net_margin.toFixed(1)}%</div>
        </div>`;
    }
    
    // 負債比（借錢比例 越低越好）
    if (health.debt_ratio !== undefined) {
        const debtColor = health.debt_ratio < 50 ? '#28a745' : (health.debt_ratio < 70 ? '#ffc107' : '#dc3545');
        html += `<div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid ${debtColor};">
            <div style="font-size: 12px; color: #666;">負債比 %</div>
            <div style="font-size: 18px; font-weight: bold; color: ${debtColor};">${health.debt_ratio.toFixed(1)}%</div>
        </div>`;
    }
    
    html += '</div>';
    
    healthDiv.innerHTML = html;
}

// 分析買賣
function analyzeTrading() {
    const select = document.getElementById('analyzerStockSelect');
    const costInput = document.getElementById('costPrice');
    
    if (!select || !select.value) {
        alert('請先選擇股票');
        return;
    }
    
    if (!costInput || !costInput.value) {
        alert('請輸入成本價');
        return;
    }
    
    const stockCode = select.value;
    const costPrice = parseFloat(costInput.value);
    
    fetch(`/api/trading-analysis/${stockCode}?cost_price=${costPrice}`)
        .then(r => r.json())
        .then(data => {
            displayTradingAnalysis(data, stockCode);
        })
        .catch(e => {
            console.error('錯誤:', e);
            alert('分析失敗');
        });
}

// 顯示買賣分析結果 - 新增詳細分析和可重複使用
function displayTradingAnalysis(data, stockCode) {
    const resultDiv = document.getElementById('tradingAnalysisResult');
    if (!resultDiv) return;
    
    const colorMap = {
        'darkred': '#8B0000',
        'red': '#dc3545',
        'orangered': '#FF4500',
        'orange': '#fd7e14',
        'darkgreen': '#1B5E20',
        'green': '#28a745',
        'blue': '#007bff',
        'darkblue': '#00008B'
    };
    
    const bgColor = colorMap[data.color] || '#667eea';
    const reasonsList = data.analysis_reasons || [];
    const reasonsHtml = reasonsList.map(r => `<div style="margin: 8px 0; font-size: 13px; line-height: 1.5;">• ${r}</div>`).join('');
    
    let html = `
    <div style="background: ${bgColor}; color: white; padding: 20px; border-radius: 10px; margin-top: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <!-- 推薦標題 -->
        <div style="font-size: 28px; font-weight: bold; margin-bottom: 5px;">
            ${data.emoji} ${data.recommendation}
        </div>
        <div style="font-size: 15px; margin-bottom: 20px; opacity: 0.95; font-weight: 500;">
            ${data.summary || ''}
        </div>
        
        <!-- 關鍵指標 -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px; border-left: 3px solid rgba(255,255,255,0.5);">
                <div style="font-size: 11px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">買入成本</div>
                <div style="font-size: 22px; font-weight: bold; margin-top: 3px;">$${(data.cost_price || 0).toFixed(0)}</div>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px; border-left: 3px solid rgba(255,255,255,0.5);">
                <div style="font-size: 11px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">現價</div>
                <div style="font-size: 22px; font-weight: bold; margin-top: 3px;">$${(data.current_price || 0).toFixed(0)}</div>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px; border-left: 3px solid rgba(255,255,255,0.5);">
                <div style="font-size: 11px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">損益金額</div>
                <div style="font-size: 22px; font-weight: bold; margin-top: 3px; ${data.profit_loss_amount >= 0 ? 'color: #90EE90' : 'color: #FFB6C6'};">
                    ${data.profit_loss_amount >= 0 ? '+' : ''}NT$${(data.profit_loss_amount || 0).toFixed(0)}
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px; border-left: 3px solid rgba(255,255,255,0.5);">
                <div style="font-size: 11px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">漲跌幅</div>
                <div style="font-size: 22px; font-weight: bold; margin-top: 3px; ${data.profit_loss_pct >= 0 ? 'color: #90EE90' : 'color: #FFB6C6'};">
                    ${data.profit_loss_pct >= 0 ? '+' : ''}${(data.profit_loss_pct || 0).toFixed(1)}%
                </div>
            </div>
        </div>
        
        <!-- 詳細分析理由 -->
        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 6px; margin-bottom: 15px;">
            <div style="font-size: 13px; font-weight: 600; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">
                📊 分析依據 (${data.analysis_reasons ? data.analysis_reasons.length : 0}項)
            </div>
            <div style="font-size: 13px; line-height: 1.8; opacity: 0.95;">
                ${reasonsHtml || '<div>無法取得分析數據</div>'}
            </div>
        </div>
        
        <!-- 技術指標摘要 -->
        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 6px; margin-bottom: 15px;">
            <div style="font-size: 13px; font-weight: 600; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">
                🔧 技術指標
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 12px; margin-bottom: 12px;">
                <div>• 相對強度指數 RSI(14): <strong>${(data.rsi || 50).toFixed(1)}</strong></div>
                <div>• 5日均線 MA5: <strong>$${(data.ma5 || 0).toFixed(0)}</strong></div>
                <div>• 20日均線 MA20: <strong>$${(data.ma20 || 0).toFixed(0)}</strong></div>
                <div>• 200日均線 MA200: <strong>$${(data.ma200 || 0).toFixed(0)}</strong></div>
                <div>• 布林帶上界: <strong>$${(data.bb_upper || 0).toFixed(0)}</strong></div>
                <div>• MACD指標: <strong>${(data.macd || 0).toFixed(4)}</strong></div>
            </div>
            
            <!-- 52週範圍可視化 -->
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.2);">
                <div style="font-size: 12px; font-weight: 600; margin-bottom: 8px;">📊 52週價格範圍</div>
                <div style="display: flex; align-items: center; gap: 10px; font-size: 11px;">
                    <div style="text-align: right; min-width: 50px;">
                        <div>最低</div>
                        <div style="font-weight: bold; font-size: 13px;">$${(data['52_week_low'] || 0).toFixed(0)}</div>
                    </div>
                    <div style="flex: 1; background: rgba(0,0,0,0.3); height: 30px; border-radius: 15px; position: relative; display: flex; align-items: center;">
                        <div style="position: absolute; left: 2px; width: 8px; height: 8px; background: #FF6B6B; border-radius: 50%;"></div>
                        <div style="position: absolute; right: 2px; width: 8px; height: 8px; background: #4ECDC4; border-radius: 50%;"></div>
                        <div style="position: absolute; left: 0; right: 0; height: 2px; background: linear-gradient(to right, #FF6B6B, #FFD93D, #4ECDC4); border-radius: 1px;"></div>
                        <div style="position: absolute; width: 4px; height: 4px; background: #FFD93D; border-radius: 50%; left: calc(${Math.min(100, Math.max(0, ((data.current_price || 0) - (data['52_week_low'] || 0)) / ((data['52_week_high'] || 0) - (data['52_week_low'] || 1)) * 100))}% - 2px);"></div>
                    </div>
                    <div style="text-align: left; min-width: 50px;">
                        <div>最高</div>
                        <div style="font-weight: bold; font-size: 13px;">$${(data['52_week_high'] || 0).toFixed(0)}</div>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 6px; font-size: 11px; opacity: 0.8;">
                    當前價格 <strong>$${(data.current_price || 0).toFixed(0)}</strong> 
                    <span style="${(data.current_price || 0) > (data['52_week_high'] || 0) * 0.9 ? 'color: #FFD93D;' : 'color: rgba(255,255,255,0.7);'}">高於52週高點90%</span>
                </div>
            </div>
        </div>
        
        <!-- 重新分析按鈕 -->
        <div style="text-align: center; margin-top: 15px;">
            <button onclick="clearAnalysis()" style="
                background: rgba(255,255,255,0.3);
                color: white;
                border: 2px solid rgba(255,255,255,0.6);
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            " onmouseover="this.style.background='rgba(255,255,255,0.5)'" onmouseout="this.style.background='rgba(255,255,255,0.3)'">
                🔄 重新分析
            </button>
        </div>
    </div>`;
    
    resultDiv.innerHTML = html;
    resultDiv.style.display = 'block';
    console.log('買賣分析已更新');
}

// 清空分析結果並重置輸入
function clearAnalysis() {
    const costInput = document.getElementById('costPrice');
    const resultDiv = document.getElementById('tradingAnalysisResult');
    
    if (costInput) {
        costInput.value = '';
        costInput.focus();
    }
    if (resultDiv) {
        resultDiv.innerHTML = '';
        resultDiv.style.display = 'none';
    }
}

// 新增函數: 獲取預算分配建議
function getBudgetAdvice() {
    const select = document.getElementById('analyzerStockSelect');
    const budgetInput = document.getElementById('budgetInput');
    
    if (!select || !select.value) {
        alert('請先選擇股票');
        return;
    }
    
    if (!budgetInput || !budgetInput.value) {
        alert('請輸入預算金額');
        return;
    }
    
    const stockCode = select.value;
    const budget = parseFloat(budgetInput.value);
    
    const resultDiv = document.getElementById('budgetAdviceResult');
    if (!resultDiv) return;
    
    // 顯示加載狀態
    resultDiv.innerHTML = '<div style="text-align: center; padding: 20px;"><p>⏳ 正在計算分配方案...</p></div>';
    
    fetch(`/api/investment-advisor/${stockCode}?budget=${budget}`)
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                resultDiv.innerHTML = `<div style="color: red; padding: 15px; background: #ffebee; border-radius: 8px;">❌ 錯誤: ${data.error}</div>`;
                return;
            }
            
            const html = `
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-top: 20px;">
                <h4 style="margin-bottom: 15px; font-size: 1.1em;">💰 ${data.stock_name} (${data.stock_code})</h4>
                
                <!-- 基本分配信息 -->
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                    <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px;">
                        <div style="font-size: 12px; opacity: 0.9;">預算</div>
                        <div style="font-size: 20px; font-weight: bold;">NT$${data.budget?.toLocaleString()}</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px;">
                        <div style="font-size: 12px; opacity: 0.9;">分配比例</div>
                        <div style="font-size: 20px; font-weight: bold;">${(data.allocation_ratio)?.toFixed(1)}%</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px;">
                        <div style="font-size: 12px; opacity: 0.9;">分配金額</div>
                        <div style="font-size: 20px; font-weight: bold;">NT$${(data.allocation_amount)?.toLocaleString()}</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px;">
                        <div style="font-size: 12px; opacity: 0.9;">購買股數</div>
                        <div style="font-size: 20px; font-weight: bold;">${data.shares?.toLocaleString()} 股</div>
                    </div>
                </div>
                
                <!-- 建議摘要 -->
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 6px; margin-bottom: 15px; border-left: 3px solid #4dd0e1;">
                    <div style="font-size: 12px; opacity: 0.9; margin-bottom: 5px;">📊 風險評分: ${(data.risk_score)?.toFixed(0)}/100</div>
                    <div style="font-size: 12px; opacity: 0.9; margin-bottom: 8px;">📍 部位規模: <strong>${data.position_size}</strong></div>
                    <div style="font-size: 13px; line-height: 1.5;">${data.recommendation}</div>
                </div>
                
                <!-- 入場信號 -->
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 6px; margin-bottom: 15px; border-left: 3px solid #81c784;">
                    <div style="font-size: 12px; font-weight: 600; margin-bottom: 8px; text-transform: uppercase;">🚀 入場信號</div>
                    <div style="font-size: 14px; margin-bottom: 5px;"><strong>目標價:</strong> NT$${(data.entry_signal?.target_price)?.toFixed(2)}</div>
                    <div style="font-size: 13px; opacity: 0.95;">${data.entry_signal?.description}</div>
                </div>
                
                <!-- 出場信號 -->
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 6px; border-left: 3px solid #e57373;">
                    <div style="font-size: 12px; font-weight: 600; margin-bottom: 10px; text-transform: uppercase;">🛑 出場信號</div>
                    <div style="font-size: 12px; line-height: 1.8;">
                        <div style="margin-bottom: 8px;">
                            <strong>止損:</strong> NT$${(data.exit_signals?.stop_loss)?.toFixed(2)}<br/>
                            <span style="opacity: 0.9; font-size: 11px;">${data.exit_signals?.stop_loss_desc}</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <strong>獲利目標1:</strong> NT$${(data.exit_signals?.profit_target_1)?.toFixed(2)}<br/>
                            <span style="opacity: 0.9; font-size: 11px;">${data.exit_signals?.profit_target_1_desc}</span>
                        </div>
                        <div>
                            <strong>獲利目標2:</strong> NT$${(data.exit_signals?.profit_target_2)?.toFixed(2)}<br/>
                            <span style="opacity: 0.9; font-size: 11px;">${data.exit_signals?.profit_target_2_desc}</span>
                        </div>
                    </div>
                </div>
            </div>`;
            
            resultDiv.innerHTML = html;
        })
        .catch(e => {
            console.error('錯誤:', e);
            resultDiv.innerHTML = '<div style="color: red; padding: 15px; background: #ffebee; border-radius: 8px;">❌ 分析失敗，請重試</div>';
        });
}

// 新增函數: 顯示預算分配建議
function displayBudgetAdvice(data, stockCode) {
    const resultDiv = document.getElementById('budgetAdviceResult');
    if (!resultDiv) return;
    
    if (data.error) {
        resultDiv.innerHTML = `<div style="color: red; padding: 15px; background: #ffebee; border-radius: 8px;">❌ 錯誤: ${data.error}</div>`;
        return;
    }
    
    const html = `
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-top: 20px;">
        <h4 style="margin-bottom: 15px; font-size: 1.1em;">💰 ${data.stock_name} (${data.stock_code})</h4>
        
        <!-- 基本分配信息 -->
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; margin-bottom: 20px;">
            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px;">
                <div style="font-size: 12px; opacity: 0.9;">預算</div>
                <div style="font-size: 20px; font-weight: bold;">NT$${data.budget?.toLocaleString()}</div>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px;">
                <div style="font-size: 12px; opacity: 0.9;">分配比例</div>
                <div style="font-size: 20px; font-weight: bold;">${(data.allocation_ratio)?.toFixed(1)}%</div>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px;">
                <div style="font-size: 12px; opacity: 0.9;">分配金額</div>
                <div style="font-size: 20px; font-weight: bold;">NT$${(data.allocation_amount)?.toLocaleString()}</div>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px;">
                <div style="font-size: 12px; opacity: 0.9;">購買股數</div>
                <div style="font-size: 20px; font-weight: bold;">${data.shares?.toLocaleString()} 股</div>
            </div>
        </div>
        
        <!-- 建議摘要 -->
        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 6px; margin-bottom: 15px; border-left: 3px solid #4dd0e1;">
            <div style="font-size: 12px; opacity: 0.9; margin-bottom: 5px;">📊 風險評分: ${(data.risk_score)?.toFixed(0)}/100</div>
            <div style="font-size: 12px; opacity: 0.9; margin-bottom: 8px;">📍 部位規模: <strong>${data.position_size}</strong></div>
            <div style="font-size: 13px; line-height: 1.5;">${data.recommendation}</div>
        </div>
        
        <!-- 入場信號 -->
        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 6px; margin-bottom: 15px; border-left: 3px solid #81c784;">
            <div style="font-size: 12px; font-weight: 600; margin-bottom: 8px; text-transform: uppercase;">🚀 入場信號</div>
            <div style="font-size: 14px; margin-bottom: 5px;"><strong>目標價:</strong> NT$${(data.entry_signal?.target_price)?.toFixed(2)}</div>
            <div style="font-size: 13px; opacity: 0.95;">${data.entry_signal?.description}</div>
        </div>
        
        <!-- 出場信號 -->
        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 6px; border-left: 3px solid #e57373;">
            <div style="font-size: 12px; font-weight: 600; margin-bottom: 10px; text-transform: uppercase;">🛑 出場信號</div>
            <div style="font-size: 12px; line-height: 1.8;">
                <div style="margin-bottom: 8px;">
                    <strong>止損:</strong> NT$${(data.exit_signals?.stop_loss)?.toFixed(2)}<br/>
                    <span style="opacity: 0.9; font-size: 11px;">${data.exit_signals?.stop_loss_desc}</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>獲利目標1:</strong> NT$${(data.exit_signals?.profit_target_1)?.toFixed(2)}<br/>
                    <span style="opacity: 0.9; font-size: 11px;">${data.exit_signals?.profit_target_1_desc}</span>
                </div>
                <div>
                    <strong>獲利目標2:</strong> NT$${(data.exit_signals?.profit_target_2)?.toFixed(2)}<br/>
                    <span style="opacity: 0.9; font-size: 11px;">${data.exit_signals?.profit_target_2_desc}</span>
                </div>
            </div>
        </div>
    </div>`;
    
    resultDiv.innerHTML = html;
}

// 新增函數: 獲取買入/賣出信號
function getStockSignals() {
    const select = document.getElementById('analyzerStockSelect');
    
    if (!select || !select.value) {
        alert('請先選擇股票');
        return;
    }
    
    const stockCode = select.value;
    const resultDiv = document.getElementById('signalsResult');
    if (!resultDiv) return;
    
    resultDiv.innerHTML = '<div style="text-align: center; padding: 20px;"><p>⏳ 正在分析信號...</p></div>';
    
    fetch(`/api/stock-signals/${stockCode}`)
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                resultDiv.innerHTML = `<div style="color: red; padding: 15px; background: #ffebee; border-radius: 8px;">❌ 錯誤: ${data.error}</div>`;
                return;
            }
            
            const signalBgColor = {
                'strong_buy': '#1b5e20',
                'buy': '#2e7d32',
                'hold': '#0277bd',
                'sell': '#d32f2f',
                'strong_sell': '#8b0000'
            }[data.signal_type] || '#667eea';
            
            const html = `
            <div style="background: ${signalBgColor}; color: white; padding: 20px; border-radius: 10px; margin-top: 20px;">
                <div style="font-size: 28px; font-weight: bold; margin-bottom: 10px;">
                    ${data.recommendation}
                </div>
                <div style="font-size: 14px; margin-bottom: 20px; opacity: 0.95;">
                    ${data.technical_summary}
                </div>
                
                <!-- 買入信號 -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                    <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 6px;">
                        <div style="font-size: 14px; font-weight: 600; margin-bottom: 10px;">🟢 買入信號 (${data.buy_score} 分)</div>
                        <div style="font-size: 13px; line-height: 1.8;">
                            ${data.buy_signals?.map(s => `<div>✅ ${s}</div>`).join('') || '<div>暫無買入信號</div>'}
                        </div>
                    </div>
                    
                    <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 6px;">
                        <div style="font-size: 14px; font-weight: 600; margin-bottom: 10px;">🔴 賣出信號 (${data.sell_score} 分)</div>
                        <div style="font-size: 13px; line-height: 1.8;">
                            ${data.sell_signals?.map(s => `<div>❌ ${s}</div>`).join('') || '<div>暫無賣出信號</div>'}
                        </div>
                    </div>
                </div>
                
                <!-- 綜合評分 -->
                <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; text-align: center; font-size: 14px;">
                    <div style="opacity: 0.9;">綜合評分: <strong>${data.net_score > 0 ? '+' : ''}${data.net_score}</strong> (買入傾向: ${Math.abs(data.net_score)} 級)</div>
                </div>
            </div>`;
            
            resultDiv.innerHTML = html;
        })
        .catch(e => {
            console.error('錯誤:', e);
            resultDiv.innerHTML = '<div style="color: red; padding: 15px; background: #ffebee; border-radius: 8px;">❌ 信號分析失敗，請重試</div>';
        });
}

// 新增函數: 加載熱門排行榜
function loadTopStocks() {
    const container = document.getElementById('topStocksContainer');
    if (!container) {
        console.log('❌ topStocksContainer not found');
        return;
    }
    
    console.log('✅ Starting loadTopStocks at', new Date().toLocaleTimeString());
    
    // 使用簡單的 setTimeout 替代 requestAnimationFrame
    setTimeout(() => {
        console.log('✅ setTimeout executing');
        
        // 顯示加載中
        container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 20px; color: rgba(255,255,255,0.7);">⏳ 加載中...</div>';
        
        fetch('/api/top-stocks')
            .then(response => {
                console.log('✅ Fetch response received, status:', response.status);
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                console.log('✅ JSON data parsed, type:', Array.isArray(data) ? 'array' : typeof data, 'length:', data?.length ?? data?.value?.length);
                console.log('✅ First item:', data?.[0]?.name ?? 'N/A');
                
                // 確保數據是數組格式
                let stocks = [];
                if (Array.isArray(data)) {
                    stocks = data;
                    console.log('✅ Data is array');
                } else if (data && Array.isArray(data.value)) {
                    stocks = data.value;
                    console.log('✅ Data.value is array');
                } else if (data && typeof data === 'object' && data.length) {
                    stocks = Array.from(data);
                    console.log('✅ Using Array.from');
                } else {
                    console.log('❌ Data format not recognized:', typeof data, 'isArray:', Array.isArray(data));
                }
                
                console.log('✅ Stocks array created, length:', stocks.length);
                
                // 檢查是否有數據
                if (!stocks || stocks.length === 0) {
                    console.log('❌ No stocks data, stocks is:', stocks, 'length:', stocks?.length);
                    container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 20px; color: rgba(255,255,255,0.6);">暫無排行數據</div>';
                    return;
                }
                
                // 清空容器並創建卡片
                container.innerHTML = '';
                console.log('✅ Creating cards for', stocks.length, 'stocks');
                
                for (let i = 0; i < stocks.length; i++) {
                    const stock = stocks[i];
                    const emoji = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟'][i];
                    const color = stock.day_change_pct >= 0 ? '#90EE90' : '#FFB6C6';
                    
                    const div = document.createElement('div');
                    div.style.cssText = 'text-align:center;padding:15px;background:rgba(255,255,255,0.12);border-radius:8px;border:1px solid rgba(255,255,255,0.2);cursor:pointer;display:flex;flex-direction:column;justify-content:space-between;min-height:200px;transition:all 0.3s ease;';
                    
                    div.onmouseover = function() {
                        this.style.transform = 'translateY(-5px) scale(1.02)';
                        this.style.background = 'rgba(255,255,255,0.18)';
                        this.style.boxShadow = '0 8px 20px rgba(102,126,234,0.3)';
                    };
                    
                    div.onmouseout = function() {
                        this.style.transform = 'translateY(0) scale(1)';
                        this.style.background = 'rgba(255,255,255,0.12)';
                        this.style.boxShadow = '';
                    };
                    
                    div.innerHTML = '<div style="font-size:1.8em;margin-bottom:8px;">' + emoji + '</div>' +
                        '<div style="font-weight:bold;color:white;margin-bottom:5px;">' + stock.name + '</div>' +
                        '<div style="font-size:0.8em;color:rgba(255,255,255,0.7);margin-bottom:10px;">代碼: ' + stock.code + '</div>' +
                        '<div style="font-size:1.2em;font-weight:bold;color:white;margin:10px 0;">NT$' + stock.current_price.toFixed(0) + '</div>' +
                        '<div style="font-size:0.85em;color:' + color + ';margin-bottom:10px;font-weight:bold;">' + 
                        (stock.day_change_pct >= 0 ? '📈 +' : '📉 ') + Math.abs(stock.day_change_pct).toFixed(2) + '%</div>' +
                        '<div style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);padding:5px 8px;border-radius:4px;font-weight:600;font-size:0.75em;">' + stock.category + '</div>';
                    
                    container.appendChild(div);
                }
                console.log('✅ All cards created successfully');
            })
            .catch(error => {
                console.error('❌ Error loading leaderboard:', error);
                console.error('❌ Error message:', error.message);
                console.error('❌ Error stack:', error.stack);
                container.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:20px;color:#FFB6C6;">⚠️ 無法加載排行榜: ' + error.message + '</div>';
            });
    }, 0); // 使用 0 毫秒延遲，立即執行
}

// 新增函數: 點選排行榜股票
function selectTopStock(code) {
    const analyzerSelect = document.getElementById('analyzerStockSelect');
    if (analyzerSelect) {
        analyzerSelect.value = code;
        const event = new Event('change', { bubbles: true });
        analyzerSelect.dispatchEvent(event);
        // 滾動到智能買賣標籤
        document.querySelector('button[data-tab="analyzer"]')?.click();
    }
}

// 頁面初始化
document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeTrading);
    }
    
    const analyzerSelect = document.getElementById('analyzerStockSelect');
    if (analyzerSelect) {
        analyzerSelect.addEventListener('change', loadAnalyzerData);
        // 啟動自動更新
        setupAutoRefreshAnalyzer(analyzerSelect);
    }
    
    // 新增: 信號分析按鈕
    const signalsBtn = document.getElementById('getSignalsBtn');
    if (signalsBtn) {
        signalsBtn.addEventListener('click', getStockSignals);
    }
    
    // 新增: 預算分配區域初始化 (自動多股票分配)
    const budgetInput = document.getElementById('budgetInputAmount');
    const budgetTopN = document.getElementById('budgetTopN');
    const calculateBtn = document.getElementById('calculateBudgetDistribution');
    
    if (calculateBtn) {
        calculateBtn.addEventListener('click', calculateAutoBudgetDistribution);
    }
    
    // 預算輸入框按 Enter 自動計算
    if (budgetInput) {
        budgetInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                calculateAutoBudgetDistribution();
            }
        });
    }
    
    // 新增: 美股分析按鈕
    const usMarketBtn = document.getElementById('analyzeUSMarket');
    if (usMarketBtn) {
        usMarketBtn.addEventListener('click', analyzeUSMarket);
    }
    
    // 新增: 加載熱門排行榜
    loadTopStocks();
});

// 新增: 自動預算分配函數
function calculateAutoBudgetDistribution() {
    const budgetInput = document.getElementById('budgetInputAmount');
    const budgetTopN = document.getElementById('budgetTopN');
    const budgetCategory = document.getElementById('budgetCategory');
    const resultDiv = document.getElementById('budgetAdviceResult');
    
    if (!resultDiv) return;
    
    const budget = parseFloat(budgetInput?.value);
    const topN = budgetTopN?.value || 5;
    const category = budgetCategory?.value || '';
    
    if (!budget || budget <= 0) {
        resultDiv.innerHTML = '<div style="color: #ff9800; padding: 15px; background: #fff3e0; border-radius: 8px;">⚠️ 請輸入有效的預算金額</div>';
        return;
    }
    
    resultDiv.innerHTML = '<div style="text-align: center; padding: 20px;"><p>⏳ AI正在計算最優分配方案...</p></div>';
    
    const apiUrl = category 
        ? `/api/auto-budget-distribution?budget=${budget}&top_n=${topN}&category=${encodeURIComponent(category)}`
        : `/api/auto-budget-distribution?budget=${budget}&top_n=${topN}`;
    
    fetch(apiUrl)
        .then(r => r.json())
        .then(data => {
            displayAutoBudgetDistribution(data);
        })
        .catch(e => {
            console.error('❌ 自動分配失敗:', e);
            resultDiv.innerHTML = '<div style="color: red; padding: 15px; background: #ffebee; border-radius: 8px;">❌ 計算失敗，請稍後重試</div>';
        });
}

// 顯示自動預算分配結果
function displayAutoBudgetDistribution(data) {
    const resultDiv = document.getElementById('budgetAdviceResult');
    if (!resultDiv) return;
    
    if (data.error) {
        resultDiv.innerHTML = `<div style="color: red; padding: 15px; background: #ffebee; border-radius: 8px;">❌ 錯誤: ${data.error}</div>`;
        return;
    }
    
    // 構建分配卡片
    let cardsHtml = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 15px;">';
    
    if (data.allocations && data.allocations.length > 0) {
        data.allocations.forEach((alloc) => {
            const changeColor = alloc.day_change_pct >= 0 ? '#90EE90' : '#FFB6C6';
            cardsHtml += `
            <div style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; text-align: center; transition: all 0.3s ease;">
                <div style="font-size: 2em; margin-bottom: 8px;">${alloc.emoji}</div>
                <div style="font-weight: bold; color: white; margin-bottom: 8px; font-size: 14px;">${alloc.name}</div>
                <div style="font-size: 12px; color: rgba(255,255,255,0.7); margin-bottom: 10px;">代碼: ${alloc.code}</div>
                
                <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px; margin-bottom: 10px;">
                    <div style="font-size: 11px; color: rgba(255,255,255,0.7); margin-bottom: 3px;">現價</div>
                    <div style="font-weight: bold; color: white;">NT$${alloc.current_price.toLocaleString('zh-TW')}</div>
                    <div style="color: ${changeColor}; font-size: 12px; margin-top: 3px;">📈 ${alloc.day_change_pct >= 0 ? '+' : ''}${alloc.day_change_pct.toFixed(2)}%</div>
                </div>
                
                <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px; margin-bottom: 10px;">
                    <div style="font-size: 11px; color: rgba(255,255,255,0.7); margin-bottom: 3px;">分配金額</div>
                    <div style="font-weight: bold; color: #81c784;">NT$${alloc.allocation_amount.toLocaleString('zh-TW')}</div>
                </div>
                
                <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px;">
                    <div style="font-size: 11px; color: rgba(255,255,255,0.7); margin-bottom: 3px;">建議買入</div>
                    <div style="font-weight: bold; color: #4dd0e1;">${alloc.shares.toLocaleString('zh-TW')} 股</div>
                    <div style="font-size: 11px; color: rgba(255,255,255,0.7); margin-top: 3px;">需要 NT$${alloc.actual_amount.toLocaleString('zh-TW')}</div>
                </div>
            </div>
            `;
        });
    }
    
    cardsHtml += '</div>';
    
    const html = `
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px;">
        <h4 style="margin-bottom: 15px; font-size: 1.1em;">🎯 AI智能分配方案</h4>
        
        <!-- 摘要信息 -->
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 20px;">
            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px;">
                <div style="font-size: 12px; opacity: 0.9;">🎯 投資預算</div>
                <div style="font-size: 20px; font-weight: bold;">NT$${(data.input_budget || 0).toLocaleString('zh-TW')}</div>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px;">
                <div style="font-size: 12px; opacity: 0.9;">✅ 已分配</div>
                <div style="font-size: 20px; font-weight: bold;">NT$${(data.total_allocated || 0).toLocaleString('zh-TW')}</div>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px;">
                <div style="font-size: 12px; opacity: 0.9;">💰 餘額</div>
                <div style="font-size: 20px; font-weight: bold;">NT$${(data.remaining_budget || 0).toLocaleString('zh-TW')}</div>
            </div>
        </div>
        
        <!-- 分配建議 -->
        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 6px; margin-bottom: 15px; border-left: 3px solid #4dd0e1;">
            <div style="font-size: 13px; line-height: 1.6;">${data.summary}</div>
        </div>
        
        <!-- 分配卡片 -->
        ${cardsHtml}
        
        <!-- 提示 -->
        <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; margin-top: 15px; border-left: 3px solid #81c784; font-size: 12px; opacity: 0.9;">
            <div>📌 <strong>提示：</strong></div>
            <div>✅ 按漲幅排序自動選擇TOP N股票進行分配</div>
            <div>✅ 股數按1000股為單位計算（台股交易單位）</div>
            <div>✅ 建議分批進場，分散投資風險</div>
            ${(data.remaining_budget || 0) > 1000 ? `<div>✅ 餘額 NT$${(data.remaining_budget || 0).toLocaleString('zh-TW')} 可用於追加投資或應對市場變化</div>` : ''}
        </div>
    </div>`;
    
    resultDiv.innerHTML = html;
}

// 新增: 加載預算分配標籤中的股票信息
function loadBudgetStockInfo() {
    const budgetStockSelect = document.getElementById('budgetStockSelect');
    const stockCode = budgetStockSelect.value;
    const budgetStockInfo = document.getElementById('budgetStockInfo');
    const budgetResultDiv = document.getElementById('budgetAdviceResult');
    
    if (!stockCode) {
        budgetStockInfo.innerHTML = '';
        budgetResultDiv.innerHTML = '';
        return;
    }
    
    // 清空之前的結果
    budgetResultDiv.innerHTML = '⏳ 加載中...';
    
    // 獲取股票信息
    fetch(`/api/stock/${stockCode}`)
        .then(r => r.json())
        .then(data => {
            if (data && data.analysis) {
                const price = data.analysis.current_price || '無';
                const name = stocks[stockCode]?.name || stockCode;
                budgetStockInfo.innerHTML = `📍 ${name} - 目前價格: NT$${price}`;
                
                // 清空結果
                budgetResultDiv.innerHTML = '';
                
                // 如果已經有預算輸入，自動計算
                const budgetInput = document.getElementById('budgetInputAmount');
                if (budgetInput && budgetInput.value) {
                    getBudgetAdviceBudgetTab();
                }
            }
        })
        .catch(e => {
            console.error('❌ 獲取股票信息失敗:', e);
            budgetStockInfo.innerHTML = '❌ 獲取信息失敗';
        });
}

// 新增: 預算分配標籤中的獲取建議
function getBudgetAdviceBudgetTab() {
    const budgetStockSelect = document.getElementById('budgetStockSelect');
    const budgetInput = document.getElementById('budgetInputAmount');
    const stockCode = budgetStockSelect.value;
    const budget = parseFloat(budgetInput.value);
    
    if (!stockCode || !budget || budget <= 0) {
        return;
    }
    
    const resultDiv = document.getElementById('budgetAdviceResult');
    resultDiv.innerHTML = '⏳ 計算中...';
    
    fetch(`/api/investment-advisor/${stockCode}?budget=${budget}`)
        .then(r => r.json())
        .then(data => {
            displayBudgetAdvice(data, stockCode);
        })
        .catch(e => {
            console.error('❌ 獲取分配建議失敗:', e);
            resultDiv.innerHTML = '❌ 獲取分配建議失敗';
        });
}

// 新增: 美股分析函數
function analyzeUSMarket() {
    const resultDiv = document.getElementById('usMarketAnalysisResult');
    if (!resultDiv) {
        console.error('❌ usMarketAnalysisResult 元素未找到');
        return;
    }
    
    // 顯示加載狀態
    resultDiv.innerHTML = '<p style="text-align: center; padding: 20px;">⏳ 正在分析美股走勢...</p>';
    
    // 調用 API
    fetch('/api/us-market-analysis')
        .then(r => {
            if (!r.ok) throw new Error('API 返回錯誤: ' + r.status);
            return r.json();
        })
        .then(data => {
            displayUSMarketAnalysis(data);
        })
        .catch(e => {
            console.error('❌ 美股分析失敗:', e);
            resultDiv.innerHTML = `<p style="color: red; text-align: center;">❌ 美股分析失敗: ${e.message}</p>`;
        });
}

// 新增: 顯示美股分析結果
function displayUSMarketAnalysis(data) {
    const resultDiv = document.getElementById('usMarketAnalysisResult');
    if (!data || !data.us_indices) {
        resultDiv.innerHTML = '<p style="color: red;">❌ 無效的分析數據</p>';
        return;
    }
    
    const usIndices = data.us_indices || {};
    const taiwanIndex = data.taiwan_index || {};
    const correlation = data.correlation || {};
    const timestamp = data.timestamp || new Date().toLocaleTimeString('zh-TW', { timeZone: 'Asia/Taipei' });
    
    // 建立方向表情符號
    function getDirectionEmoji(direction) {
        if (direction === '📈' || direction === 'up') return '📈';
        if (direction === '📉' || direction === 'down') return '📉';
        return '➡️';
    }
    
    // 構建美股指數卡片
    let usIndicesHTML = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">';
    
    for (const [name, details] of Object.entries(usIndices)) {
        if (typeof details === 'object' && details.latest_price !== undefined) {
            const direction = getDirectionEmoji(details.direction);
            const changePct = details.change_pct !== undefined ? details.change_pct.toFixed(2) : '0.00';
            const change = details.change !== undefined ? details.change.toFixed(2) : '0.00';
            
            usIndicesHTML += `
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; color: white;">
                    <div style="font-weight: bold; margin-bottom: 10px;">${name}</div>
                    <div>💵 ${details.latest_price?.toFixed(2) || 'N/A'}</div>
                    <div>${direction} 變化: ${change} (${changePct}%)</div>
                </div>
            `;
        }
    }
    usIndicesHTML += '</div>';
    
    // 台灣指數卡片
    const twDirection = getDirectionEmoji(taiwanIndex.direction);
    const twChangePct = taiwanIndex.change_pct !== undefined ? taiwanIndex.change_pct.toFixed(2) : '0.00';
    const twChange = taiwanIndex.change !== undefined ? taiwanIndex.change.toFixed(2) : '0.00';
    
    const taiwanHTML = `
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 15px; border-radius: 8px; color: white; margin-bottom: 20px;">
            <div style="font-weight: bold; margin-bottom: 10px;">台灣加權指數 (TWII)</div>
            <div>💹 ${taiwanIndex.latest_price?.toFixed(2) || 'N/A'}</div>
            <div>${twDirection} 變化: ${twChange} (${twChangePct}%)</div>
        </div>
    `;
    
    // 關聯度分析
    let correlationHTML = '<div style="margin-bottom: 20px;">';
    correlationHTML += '<h3 style="margin-bottom: 10px;">🔗 US-台股關聯分析</h3>';
    
    if (correlation.is_correlated) {
        correlationHTML += '<div style="background-color: #e8f5e9; padding: 10px; border-left: 4px solid #388e3c; border-radius: 4px;">✅ 美股與台股走勢關聯強</div>';
    } else {
        correlationHTML += '<div style="background-color: #fff3e0; padding: 10px; border-left: 4px solid #f57c00; border-radius: 4px;">⚠️ 美股與台股走勢關聯弱</div>';
    }
    
    correlationHTML += `<div style="margin-top: 10px; font-size: 0.9em; color: #666;">關聯強度: ${(correlation.correlation_strength * 100).toFixed(1)}%</div>`;
    correlationHTML += '</div>';
    
    // 預測和建議
    const predictionColor = data.risk_level === '低風險' ? '#4caf50' : (data.risk_level === '中風險' ? '#ff9800' : '#f44336');
    let predictionHTML = '<div style="background: linear-gradient(135deg, ' + predictionColor + ' 0%, rgba(0,0,0,0.1) 100%); padding: 20px; border-radius: 8px; color: white; margin-bottom: 20px;">';
    predictionHTML += `<h3 style="margin-top: 0;">${data.prediction || '預測中'}</h3>`;
    predictionHTML += `<div style="font-size: 0.9em; opacity: 0.9;">${data.recommendation || ''}</div>`;
    predictionHTML += `<div style="margin-top: 10px; font-weight: bold;">🎯 風險等級: ${data.risk_level || 'N/A'}</div>`;
    predictionHTML += '</div>';
    
    // 時間戳
    const timeHTML = `<div style="text-align: right; font-size: 0.85em; color: #999;">更新時間: ${timestamp}</div>`;
    
    // 組合所有HTML
    resultDiv.innerHTML = usIndicesHTML + taiwanHTML + correlationHTML + predictionHTML + timeHTML;
}

// 設置分析器自動更新 - 每3分鐘檢查並更新
function setupAutoRefreshAnalyzer(select) {
    function isMarketHours() {
        const now = new Date();
        const taipei = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Taipei' }));
        const day = taipei.getDay();
        const hours = taipei.getHours();
        const minutes = taipei.getMinutes();
        
        // 周一到周五 9:00 到 13:30
        const isWeekday = day >= 1 && day <= 5;
        const isTradingTime = (hours >= 9 && hours < 13) || (hours === 13 && minutes < 30);
        
        return isWeekday && isTradingTime;
    }
    
    // 每3分鐘自動更新選中的股票數據
    setInterval(() => {
        const stockCode = select.value;
        if (stockCode && isMarketHours()) {
            console.log('🔄 分析器自動更新: ' + stockCode + ' - ' + new Date().toLocaleTimeString('zh-TW', { timeZone: 'Asia/Taipei' }));
            loadAnalyzerData();
        }
    }, 180000); // 3分鐘 = 180000毫秒
}
