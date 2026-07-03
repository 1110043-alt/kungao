/**
 * 背景腳本 - Service Worker
 * 處理消息、存儲和全域狀態
 */

let dataManager = null;

// 初始化
chrome.runtime.onInstalled.addListener(() => {
  console.log("✅ 多帳號自動結帳填表助手已安裝");
  
  // 初始化資料管理器
  fetch(chrome.runtime.getURL('data-manager.js'))
    .then(res => res.text())
    .then(code => {
      eval(code);
    });
});

// 監聽來自 popup 和 content script 的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  handleMessage(request, sender, sendResponse);
  return true; // 保持連接以便進行異步回應
});

async function handleMessage(request, sender, sendResponse) {
  // 確保 dataManager 已初始化
  if (!dataManager) {
    dataManager = new DataManager();
    await dataManager.loadFromStorage();
  }

  const { action, data } = request;

  try {
    let result;

    switch (action) {
      // ===== 組合操作 =====
      case 'combine':
        result = dataManager.combine(data.profileId, data.cardId);
        sendResponse(result);
        break;

      case 'loadData':
        result = dataManager.loadData(data.profileId);
        sendResponse(result);
        break;

      case 'loadCard':
        result = dataManager.loadCard(data.cardId);
        sendResponse(result);
        break;

      // ===== 取得值 =====
      case 'getFieldValue':
        const value = dataManager.getFieldValue(data.fieldType);
        sendResponse({ success: true, value });
        break;

      case 'getStatus':
        const status = dataManager.getStatus();
        sendResponse({ success: true, status });
        break;

      // ===== 查詢 =====
      case 'listProfiles':
        const profiles = dataManager.listProfiles();
        sendResponse({ success: true, profiles });
        break;

      case 'listCards':
        const cards = dataManager.listCards();
        sendResponse({ success: true, cards });
        break;

      // ===== 新增 =====
      case 'addProfile':
        result = await dataManager.addProfile(
          data.profileId,
          data.name,
          data.phone,
          data.id_number,
          data.email
        );
        sendResponse(result);
        break;

      case 'addCard':
        result = await dataManager.addCard(
          data.cardId,
          data.card_number,
          data.exp_month,
          data.exp_year,
          data.cvv
        );
        sendResponse(result);
        break;

      // ===== 刪除 =====
      case 'removeProfile':
        result = await dataManager.removeProfile(data.profileId);
        sendResponse(result);
        break;

      case 'removeCard':
        result = await dataManager.removeCard(data.cardId);
        sendResponse(result);
        break;

      default:
        sendResponse({ success: false, error: '未知的操作' });
    }
  } catch (error) {
    console.error('消息處理錯誤:', error);
    sendResponse({ success: false, error: error.message });
  }
}
