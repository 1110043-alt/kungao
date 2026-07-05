/**
 * 通知設置控制面板 - 可集成到主應用
 * 提供 UI 讓用戶管理推送通知偏好設置
 */

function createNotificationSettingsPanel() {
  const panel = `
    <div id="notificationSettingsPanel" class="notification-panel" style="
      background: #f8f9fa;
      border-radius: 12px;
      padding: 20px;
      margin: 20px 0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    ">
      <h3 style="margin-top: 0; color: #7c3aed;">🔔 推送通知設置</h3>
      
      <!-- 啟用/禁用通知 -->
      <div style="margin-bottom: 20px;">
        <label style="display: flex; align-items: center; cursor: pointer;">
          <input type="checkbox" id="enableNotifications" checked style="margin-right: 12px; width: 18px; height: 18px;">
          <span style="font-weight: 500;">啟用推送通知</span>
        </label>
        <p style="color: #666; font-size: 14px; margin: 8px 0 0 30px;">
          實時股票異動會在您的設備上發送通知
        </p>
      </div>

      <!-- 價格變化閾值 -->
      <div style="margin-bottom: 20px;">
        <label for="priceChangeThreshold" style="display: block; font-weight: 500; margin-bottom: 8px;">
          價格變化告警閾值: <span id="priceChangeValue">2.0</span>%
        </label>
        <input 
          type="range" 
          id="priceChangeThreshold" 
          min="0.5" 
          max="10" 
          step="0.5" 
          value="2.0"
          style="width: 100%; cursor: pointer;"
        >
        <p style="color: #666; font-size: 14px; margin: 8px 0 0 0;">
          當股價變化達到此百分比時會發送通知
        </p>
      </div>

      <!-- 監控股票列表 -->
      <div style="margin-bottom: 20px;">
        <label style="display: block; font-weight: 500; margin-bottom: 12px;">
          📊 監控的股票
        </label>
        <div id="watchedStocksList" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px;">
          <!-- 動態生成 -->
        </div>
        <div style="margin-top: 12px;">
          <input 
            type="text" 
            id="addStockInput" 
            placeholder="輸入股票代碼 (如: 2330)"
            style="padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; width: calc(100% - 100px); margin-right: 8px;"
          >
          <button id="addStockBtn" style="
            padding: 8px 16px;
            background: #7c3aed;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
          ">新增</button>
        </div>
      </div>

      <!-- 通知類型 -->
      <div style="margin-bottom: 20px;">
        <label style="display: block; font-weight: 500; margin-bottom: 12px;">通知類型</label>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px;">
          <label style="display: flex; align-items: center; cursor: pointer;">
            <input type="checkbox" class="notificationType" value="priceAlert" checked style="margin-right: 8px;">
            <span>📈 價格異動</span>
          </label>
          <label style="display: flex; align-items: center; cursor: pointer;">
            <input type="checkbox" class="notificationType" value="signalAlert" checked style="margin-right: 8px;">
            <span>🎯 買賣信號</span>
          </label>
          <label style="display: flex; align-items: center; cursor: pointer;">
            <input type="checkbox" class="notificationType" value="volumeAlert" style="margin-right: 8px;">
            <span>📊 成交量異常</span>
          </label>
          <label style="display: flex; align-items: center; cursor: pointer;">
            <input type="checkbox" class="notificationType" value="anomalyAlert" style="margin-right: 8px;">
            <span>⚠️ 市場異常</span>
          </label>
        </div>
      </div>

      <!-- 安靜時段 -->
      <div style="margin-bottom: 20px;">
        <label style="display: block; font-weight: 500; margin-bottom: 8px;">
          🌙 安靜時段 (不發送通知)
        </label>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
          <div>
            <label style="display: block; font-size: 14px; color: #666; margin-bottom: 4px;">開始時間</label>
            <input type="time" id="quietStart" value="22:00" style="padding: 8px; border: 1px solid #ddd; border-radius: 6px; width: 100%; box-sizing: border-box;">
          </div>
          <div>
            <label style="display: block; font-size: 14px; color: #666; margin-bottom: 4px;">結束時間</label>
            <input type="time" id="quietEnd" value="09:00" style="padding: 8px; border: 1px solid #ddd; border-radius: 6px; width: 100%; box-sizing: border-box;">
          </div>
        </div>
      </div>

      <!-- 其他選項 -->
      <div style="margin-bottom: 20px;">
        <label style="display: flex; align-items: center; cursor: pointer; margin-bottom: 10px;">
          <input type="checkbox" id="enableSound" checked style="margin-right: 8px;">
          <span>🔊 啟用聲音提示</span>
        </label>
        <label style="display: flex; align-items: center; cursor: pointer; margin-bottom: 10px;">
          <input type="checkbox" id="enableVibrate" checked style="margin-right: 8px;">
          <span>📳 啟用振動</span>
        </label>
        <label style="display: flex; align-items: center; cursor: pointer; margin-bottom: 10px;">
          <input type="checkbox" id="excludeWeekends" checked style="margin-right: 8px;">
          <span>📅 排除週末</span>
        </label>
        <label style="display: flex; align-items: center; cursor: pointer;">
          <input type="checkbox" id="excludeAfterHours" checked style="margin-right: 8px;">
          <span>🕐 排除盤後時段</span>
        </label>
      </div>

      <!-- 操作按鈕 -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
        <button id="saveSettingsBtn" style="
          padding: 12px;
          background: #7c3aed;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
          font-size: 14px;
        ">💾 保存設置</button>
        <button id="testNotificationBtn" style="
          padding: 12px;
          background: #a855f7;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
          font-size: 14px;
        ">🧪 測試通知</button>
      </div>

      <div id="statusMessage" style="
        margin-top: 12px;
        padding: 12px;
        border-radius: 6px;
        display: none;
        font-size: 14px;
      "></div>
    </div>
  `;

  return panel;
}

// ========== 初始化控制面板 ==========
function initNotificationPanel() {
  const manager = window.stockNotificationManager;
  
  if (!manager) {
    console.warn('⚠️ stockNotificationManager 尚未初始化');
    return;
  }

  // 更新 UI 以反映當前設置
  const settings = manager.notificationSettings;
  
  const enableCheckbox = document.getElementById('enableNotifications');
  const priceChangeSlider = document.getElementById('priceChangeThreshold');
  const soundCheckbox = document.getElementById('enableSound');
  const vibrateCheckbox = document.getElementById('enableVibrate');
  const weekendCheckbox = document.getElementById('excludeWeekends');
  const afterHoursCheckbox = document.getElementById('excludeAfterHours');
  const quietStartInput = document.getElementById('quietStart');
  const quietEndInput = document.getElementById('quietEnd');

  if (enableCheckbox) enableCheckbox.checked = settings.enabled;
  if (priceChangeSlider) priceChangeSlider.value = settings.priceChange;
  if (soundCheckbox) soundCheckbox.checked = settings.sound;
  if (vibrateCheckbox) vibrateCheckbox.checked = settings.vibrate;
  if (weekendCheckbox) weekendCheckbox.checked = settings.excludeWeekends;
  if (afterHoursCheckbox) afterHoursCheckbox.checked = settings.excludeAfterHours;
  if (quietStartInput) quietStartInput.value = settings.quiet_hours?.start || '22:00';
  if (quietEndInput) quietEndInput.value = settings.quiet_hours?.end || '09:00';

  // 更新監控列表
  updateWatchedStocksList();

  // 綁定事件
  bindPanelEvents();
}

function updateWatchedStocksList() {
  const manager = window.stockNotificationManager;
  const container = document.getElementById('watchedStocksList');
  
  if (!container) return;

  const watched = manager.getWatchedStocks();
  container.innerHTML = watched.map(code => `
    <div style="
      background: white;
      padding: 8px 12px;
      border-radius: 6px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border: 1px solid #ddd;
    ">
      <span style="font-weight: 500;">${code}</span>
      <button class="remove-stock-btn" data-code="${code}" style="
        background: #ff6b6b;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 4px 8px;
        cursor: pointer;
        font-size: 12px;
      ">移除</button>
    </div>
  `).join('');

  // 綁定移除按鈕
  document.querySelectorAll('.remove-stock-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const code = this.getAttribute('data-code');
      manager.removeWatchedStock(code);
      updateWatchedStocksList();
      showStatus('✅ 已移除 ' + code);
    });
  });
}

function bindPanelEvents() {
  const manager = window.stockNotificationManager;

  // 價格變化滑塊
  const priceChangeSlider = document.getElementById('priceChangeThreshold');
  const priceChangeValue = document.getElementById('priceChangeValue');
  
  if (priceChangeSlider) {
    priceChangeSlider.addEventListener('input', (e) => {
      priceChangeValue.textContent = e.target.value;
    });
  }

  // 新增股票
  const addStockBtn = document.getElementById('addStockBtn');
  const addStockInput = document.getElementById('addStockInput');
  
  if (addStockBtn && addStockInput) {
    addStockBtn.addEventListener('click', () => {
      const code = addStockInput.value.trim().toUpperCase();
      if (code && code.length <= 4) {
        manager.addWatchedStock(code);
        addStockInput.value = '';
        updateWatchedStocksList();
        showStatus('✅ 已添加 ' + code);
      } else {
        showStatus('❌ 請輸入有效的股票代碼');
      }
    });

    addStockInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') addStockBtn.click();
    });
  }

  // 保存設置
  const saveBtn = document.getElementById('saveSettingsBtn');
  if (saveBtn) {
    saveBtn.addEventListener('click', () => {
      const enableCheckbox = document.getElementById('enableNotifications');
      const priceChangeSlider = document.getElementById('priceChangeThreshold');
      const soundCheckbox = document.getElementById('enableSound');
      const vibrateCheckbox = document.getElementById('enableVibrate');
      const weekendCheckbox = document.getElementById('excludeWeekends');
      const afterHoursCheckbox = document.getElementById('excludeAfterHours');
      const quietStartInput = document.getElementById('quietStart');
      const quietEndInput = document.getElementById('quietEnd');

      manager.updateSetting('enabled', enableCheckbox.checked);
      manager.updateSetting('priceChange', parseFloat(priceChangeSlider.value));
      manager.updateSetting('sound', soundCheckbox.checked);
      manager.updateSetting('vibrate', vibrateCheckbox.checked);
      manager.updateSetting('excludeWeekends', weekendCheckbox.checked);
      manager.updateSetting('excludeAfterHours', afterHoursCheckbox.checked);
      manager.updateSetting('quiet_hours', {
        start: quietStartInput.value,
        end: quietEndInput.value
      });

      showStatus('✅ 設置已保存');

      // 根據設置決定是否啟動監控
      if (enableCheckbox.checked && !manager.isWatching) {
        manager.startWatching(30000);
      } else if (!enableCheckbox.checked && manager.isWatching) {
        manager.stopWatching();
      }
    });
  }

  // 測試通知
  const testBtn = document.getElementById('testNotificationBtn');
  if (testBtn) {
    testBtn.addEventListener('click', () => {
      testNotification();
      showStatus('✅ 測試通知已發送');
    });
  }
}

function testNotification() {
  const manager = window.stockNotificationManager;
  manager.sendPriceNotification({
    code: '2330',
    name: '台積電',
    current_price: 2410
  }, 2.5);
}

function showStatus(message) {
  const statusDiv = document.getElementById('statusMessage');
  if (!statusDiv) return;
  
  statusDiv.textContent = message;
  statusDiv.style.display = 'block';
  statusDiv.style.background = message.includes('✅') ? '#d4edda' : '#f8d7da';
  statusDiv.style.color = message.includes('✅') ? '#155724' : '#721c24';
  
  setTimeout(() => {
    statusDiv.style.display = 'none';
  }, 3000);
}

// 在 DOM 加載時初始化
document.addEventListener('DOMContentLoaded', () => {
  // 如果需要自動創建面板，可以取消註釋以下代碼
  // const panelHTML = createNotificationSettingsPanel();
  // document.body.insertAdjacentHTML('beforeend', panelHTML);
  // initNotificationPanel();
});

console.log('✅ 通知設置面板腳本已加載');
