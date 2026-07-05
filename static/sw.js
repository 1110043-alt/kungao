// Service Worker for Taiwan Stock Predictor PWA
// 版本: 1.0.0
// 功能: 離線支持, 緩存策略, 後台同步, 推送通知

const CACHE_NAME = 'taiwan-stock-v1';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/script.js',
  'https://cdn.jsdelivr.net/npm/chart.js',
  '/api/all-stocks'
];

// === 安裝事件 ===
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .catch(err => console.error('[Service Worker] Cache failed:', err))
  );
  self.skipWaiting(); // 立即激活
});

// === 激活事件 ===
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim(); // 立即接管所有客戶端
});

// === 獲取事件（請求攔截）===
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // API 請求 - 網絡優先, 失敗時使用緩存
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // 緩存成功的 API 響應
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // 網絡失敗時返回緩存
          return caches.match(request);
        })
    );
    return;
  }

  // 靜態資源 - 緩存優先
  event.respondWith(
    caches.match(request)
      .then(response => {
        if (response) return response;
        
        return fetch(request).then(response => {
          // 不緩存非200響應
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }
          
          // 緩存新資源
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(request, responseClone);
          });
          
          return response;
        });
      })
      .catch(() => {
        // 返回簡單的離線頁面
        return new Response('離線模式 - 無網絡連接', {
          status: 503,
          statusText: 'Service Unavailable',
          headers: new Headers({
            'Content-Type': 'text/plain; charset=utf-8'
          })
        });
      })
  );
});

// === 推送通知事件 ===
self.addEventListener('push', event => {
  console.log('[Service Worker] Push received:', event);
  
  const options = {
    body: '',
    icon: '/static/icon-192x192.png',
    badge: '/static/badge-72x72.png',
    tag: 'stock-notification',
    requireInteraction: false,
    vibrate: [100, 50, 100],
    actions: [
      {
        action: 'open',
        title: '查看詳情'
      },
      {
        action: 'close',
        title: '關閉'
      }
    ]
  };

  // 解析推送數據
  if (event.data) {
    try {
      const data = event.data.json();
      options.body = data.message || '有新的股票異動';
      options.data = {
        url: data.url || '/',
        stockCode: data.stockCode || '',
        ...data
      };
      options.tag = `stock-${data.stockCode || 'general'}`;
    } catch (e) {
      options.body = event.data.text();
    }
  }

  event.waitUntil(
    self.registration.showNotification('台股即時預測', options)
  );
});

// === 通知點擊事件 ===
self.addEventListener('notificationclick', event => {
  console.log('[Service Worker] Notification clicked:', event.action);
  event.notification.close();

  if (event.action === 'close') {
    return;
  }

  const urlToOpen = event.notification.data?.url || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(clientList => {
        // 查找已打開的窗口
        for (let i = 0; i < clientList.length; i++) {
          const client = clientList[i];
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus();
          }
        }
        // 打開新窗口
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

// === 後台同步事件（定期檢查更新）===
self.addEventListener('sync', event => {
  console.log('[Service Worker] Background sync triggered');
  
  if (event.tag === 'sync-stocks') {
    event.waitUntil(
      fetch('/api/all-stocks')
        .then(response => response.json())
        .then(data => {
          console.log('[Service Worker] Synced stock data');
          // 可以在這裡處理數據更新
        })
        .catch(err => console.error('[Service Worker] Sync failed:', err))
    );
  }
});

// === 消息處理 ===
self.addEventListener('message', event => {
  console.log('[Service Worker] Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'SYNC_STOCKS') {
    event.waitUntil(
      fetch('/api/all-stocks')
        .then(response => response.json())
        .then(data => {
          event.ports[0].postMessage({ success: true, data });
        })
        .catch(err => {
          event.ports[0].postMessage({ success: false, error: err.message });
        })
    );
  }
});

console.log('[Service Worker] Loaded successfully');
