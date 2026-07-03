/**
 * 股票推送通知管理系統
 * 版本: 1.0.0
 * 功能: 監控股票異動, 發送推送通知, 管理通知偏好設置
 */

class StockNotificationManager {
  constructor() {
    this.storageKey = 'stock_notification_settings';
    this.watchedStocks = new Map();
    this.notificationSettings = this.loadSettings();
    this.isWatching = false;
    this.updateInterval = null;
    this.previousData = new Map();
    
    console.log('📲 股票推送通知管理器已初始化');
    this.initializeWatchers();
  }

  // ========== 設置管理 ==========
  loadSettings() {
    const saved = localStorage.getItem(this.storageKey);
    return saved ? JSON.parse(saved) : {
      enabled: true,
      priceChange: 2.0,  // 價格變化 2% 時通知
      volumeChange: 20.0, // 成交量變化 20% 時通知
      watchedStocks: ['2330', '2454', '3008'],  // 預設監控
      sound: true,
      vibrate: true,
      excludeWeekends: true,
      excludeAfterHours: true,
      quiet_hours: { start: '22:00', end: '09:00' } // 安靜時段
    };
  }

  saveSettings() {
    localStorage.setItem(this.storageKey, JSON.stringify(this.notificationSettings));
    console.log('💾 通知設置已保存');
  }

  updateSetting(key, value) {
    this.notificationSettings[key] = value;
    this.saveSettings();
  }

  // ========== 監控設置 ==========
  addWatchedStock(code, priceChangeThreshold = null) {
    this.watchedStocks.set(code, {
      code,
      lastPrice: null,
      lastVolume: null,
      priceChangeThreshold: priceChangeThreshold || this.notificationSettings.priceChange,
      lastNotificationTime: 0,
      notificationCooldown: 60000 // 60秒冷卻時間
    });
    console.log(`✅ 已添加監控: ${code}`);
    this.saveWatchedStocks();
  }

  removeWatchedStock(code) {
    this.watchedStocks.delete(code);
    console.log(`❌ 已移除監控: ${code}`);
    this.saveWatchedStocks();
  }

  getWatchedStocks() {
    return Array.from(this.watchedStocks.keys());
  }

  saveWatchedStocks() {
    const watched = this.getWatchedStocks();
    localStorage.setItem('watched_stocks', JSON.stringify(watched));
  }

  loadWatchedStocks() {
    const saved = localStorage.getItem('watched_stocks');
    if (saved) {
      try {
        const stocks = JSON.parse(saved);
        stocks.forEach(code => this.addWatchedStock(code));
      } catch (e) {
        console.error('❌ 無法加載監控列表:', e);
      }
    }
  }

  // ========== 時間檢查 ==========
  isInQuietHours() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const currentTime = `${hours}:${minutes}`;
    
    const { start, end } = this.notificationSettings.quiet_hours;
    
    if (start < end) {
      return currentTime >= start && currentTime < end;
    } else {
      return currentTime >= start || currentTime < end;
    }
  }

  isMarketOpen() {
    const now = new Date();
    const day = now.getDay();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const currentTime = hours * 100 + minutes;

    // 台灣時間: 9:00-13:30 交易 (UTC+8)
    const isWeekday = day >= 1 && day <= 5;
    const isOpenHours = currentTime >= 900 && currentTime < 1330;

    return isWeekday && isOpenHours;
  }

  shouldNotify() {
    if (!this.notificationSettings.enabled) return false;
    if (this.isInQuietHours()) return false;
    if (this.notificationSettings.excludeAfterHours && !this.isMarketOpen()) return false;
    if (this.notificationSettings.excludeWeekends && new Date().getDay() > 5) return false;
    
    return true;
  }

  // ========== 價格監控 ==========
  checkPriceChanges(allStocks) {
    if (!this.shouldNotify()) return;

    this.watchedStocks.forEach((watchSettings, code) => {
      const stock = allStocks.find(s => s.code === code);
      if (!stock) return;

      const currentPrice = stock.current_price;
      const priceChange = stock.day_change_pct || 0;

      // 檢查價格變化
      if (Math.abs(priceChange) >= watchSettings.priceChangeThreshold) {
        const now = Date.now();
        if (now - watchSettings.lastNotificationTime > watchSettings.notificationCooldown) {
          this.sendPriceNotification(stock, priceChange);
          watchSettings.lastNotificationTime = now;
        }
      }

      // 保存前一次數據
      this.previousData.set(code, {
        price: currentPrice,
        volume: stock.volume || 0,
        timestamp: Date.now()
      });
    });
  }

  sendPriceNotification(stock, priceChange) {
    const direction = priceChange >= 0 ? '📈 上漲' : '📉 下跌';
    const title = `${stock.name} (${stock.code})`;
    const body = `${direction} ${Math.abs(priceChange).toFixed(2)}% | ${stock.current_price}`;

    this.showNotification(title, body, {
      tag: `price-${stock.code}`,
      stockCode: stock.code,
      url: `/?tab=analysis&stock=${stock.code}`,
      priceChange,
      price: stock.current_price
    });

    console.log(`🔔 價格通知已發送: ${title} ${direction} ${Math.abs(priceChange).toFixed(2)}%`);
  }

  // ========== 信號通知 ==========
  sendSignalNotification(stockCode, signal, signalStrength) {
    const signalEmoji = {
      'buy': '🟢 買進信號',
      'sell': '🔴 賣出信號',
      'hold': '🟡 持有信號'
    };

    const title = `${stockCode} 交易信號`;
    const body = `${signalEmoji[signal] || signal} (強度: ${signalStrength})`;

    this.showNotification(title, body, {
      tag: `signal-${stockCode}`,
      stockCode,
      url: `/?tab=analyzer&stock=${stockCode}`,
      signal,
      strength: signalStrength,
      priority: 'high'
    });

    console.log(`🟢 信號通知已發送: ${stockCode} ${signal}`);
  }

  // ========== 異常通知 ==========
  sendAnomalyNotification(stockCode, anomaly, description) {
    const anomalyEmoji = {
      'volume_spike': '📊 成交量異常',
      'gap_up': '⬆️ 跳空上升',
      'gap_down': '⬇️ 跳空下跌',
      'limit_up': '🚀 漲停',
      'limit_down': '💥 跌停'
    };

    const title = `${stockCode} 異常現象`;
    const body = `${anomalyEmoji[anomaly] || anomaly}: ${description}`;

    this.showNotification(title, body, {
      tag: `anomaly-${stockCode}`,
      stockCode,
      url: `/?tab=analysis&stock=${stockCode}`,
      anomaly,
      priority: 'high',
      requireInteraction: true
    });

    console.log(`⚠️ 異常通知已發送: ${stockCode} ${anomaly}`);
  }

  // ========== 推送通知實現 ==========
  async showNotification(title, body, options = {}) {
    if (!('Notification' in window)) {
      console.warn('此瀏覽器不支持通知功能');
      return;
    }

    if (Notification.permission !== 'granted') {
      console.warn('未授予通知權限');
      return;
    }

    try {
      const defaultOptions = {
        icon: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"%3E%3Crect fill="%237c3aed" width="192" height="192"/%3E%3Ctext x="96" y="120" font-size="80" font-family="Arial" font-weight="bold" text-anchor="middle" fill="white"%3E股%3C/text%3E%3C/svg%3E',
        badge: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 72"%3E%3Crect fill="%237c3aed" width="72" height="72"/%3E%3Ctext x="36" y="55" font-size="45" font-family="Arial" font-weight="bold" text-anchor="middle" fill="white"%3E股%3C/text%3E%3C/svg%3E',
        tag: 'stock-notification',
        requireInteraction: false,
        vibrate: this.notificationSettings.vibrate ? [100, 50, 100] : [],
        data: {},
        actions: [
          { action: 'view', title: '查看' },
          { action: 'close', title: '關閉' }
        ]
      };

      const notificationOptions = { ...defaultOptions, ...options };

      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.ready;
        registration.showNotification(title, notificationOptions);
      } else {
        new Notification(title, { body, ...notificationOptions });
      }

      // 播放聲音（可選）
      if (this.notificationSettings.sound) {
        this.playNotificationSound();
      }
    } catch (error) {
      console.error('❌ 通知發送失敗:', error);
    }
  }

  // ========== 聲音提醒 ==========
  playNotificationSound() {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.value = 800;
      oscillator.type = 'sine';

      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.5);
    } catch (error) {
      console.warn('❌ 無法播放聲音:', error);
    }
  }

  // ========== 開始監控 ==========
  startWatching(updateInterval = 30000) {
    if (this.isWatching) {
      console.warn('⚠️ 已在監控中');
      return;
    }

    this.isWatching = true;
    console.log('🔍 開始監控股票異動...');

    this.updateInterval = setInterval(async () => {
      try {
        const response = await fetch('/api/all-stocks');
        const allStocks = await response.json();
        this.checkPriceChanges(allStocks);
      } catch (error) {
        console.error('❌ 獲取股票數據失敗:', error);
      }
    }, updateInterval);
  }

  stopWatching() {
    if (!this.isWatching) return;
    
    clearInterval(this.updateInterval);
    this.isWatching = false;
    console.log('⏸️ 已停止監控');
  }

  // ========== 初始化監控列表 ==========
  initializeWatchers() {
    const watchedStocks = this.notificationSettings.watchedStocks || ['2330', '2454', '3008'];
    watchedStocks.forEach(code => this.addWatchedStock(code));
  }

  // ========== 工具方法 ==========
  getStatus() {
    return {
      enabled: this.notificationSettings.enabled,
      isWatching: this.isWatching,
      watchedStocks: this.getWatchedStocks(),
      settings: this.notificationSettings,
      notificationPermission: Notification.permission
    };
  }

  exportSettings() {
    return JSON.stringify(this.notificationSettings, null, 2);
  }

  importSettings(jsonString) {
    try {
      const settings = JSON.parse(jsonString);
      this.notificationSettings = { ...this.notificationSettings, ...settings };
      this.saveSettings();
      console.log('✅ 設置已導入');
    } catch (error) {
      console.error('❌ 導入設置失敗:', error);
    }
  }
}

// ========== 全局實例 ==========
window.stockNotificationManager = new StockNotificationManager();

// ========== 在 DOM 加載後自動啟動 ==========
document.addEventListener('DOMContentLoaded', () => {
  if (window.stockNotificationManager.notificationSettings.enabled) {
    window.stockNotificationManager.startWatching(30000); // 每30秒檢查一次
  }
});

console.log('✅ 股票推送通知模塊已加載');
