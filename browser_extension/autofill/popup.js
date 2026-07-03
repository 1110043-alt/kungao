/**
 * Popup 邏輯腳本
 * 處理 UI 交互和消息傳遞
 */

class PopupApp {
  constructor() {
    this.profiles = [];
    this.cards = [];
    this.currentProfile = null;
    this.currentCard = null;
    
    this.initializeUI();
    this.loadData();
    this.setupEventListeners();
  }

  initializeUI() {
    // 初始化標籤頁
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.switchTab(e.target.dataset.tab);
      });
    });
  }

  async loadData() {
    chrome.runtime.sendMessage({ action: 'listProfiles' }, (response) => {
      this.profiles = response.profiles;
      this.updateProfileSelect();
      this.updateDeleteProfileSelect();
    });

    chrome.runtime.sendMessage({ action: 'listCards' }, (response) => {
      this.cards = response.cards;
      this.updateCardSelect();
      this.updateDeleteCardSelect();
    });

    this.updateStatus();
  }

  updateProfileSelect() {
    const select = document.getElementById('profile-select');
    select.innerHTML = '<option value="">-- 選擇個人資訊 --</option>';
    this.profiles.forEach(p => {
      select.innerHTML += `<option value="${p}">${p}</option>`;
    });
  }

  updateCardSelect() {
    const select = document.getElementById('card-select');
    select.innerHTML = '<option value="">-- 選擇信用卡 --</option>';
    this.cards.forEach(c => {
      select.innerHTML += `<option value="${c}">${c}</option>`;
    });
  }

  updateDeleteProfileSelect() {
    const select = document.getElementById('delete-profile-select');
    select.innerHTML = '<option value="">-- 選擇要刪除的資料 --</option>';
    this.profiles.forEach(p => {
      select.innerHTML += `<option value="${p}">${p}</option>`;
    });
  }

  updateDeleteCardSelect() {
    const select = document.getElementById('delete-card-select');
    select.innerHTML = '<option value="">-- 選擇要刪除的卡號 --</option>';
    this.cards.forEach(c => {
      select.innerHTML += `<option value="${c}">${c}</option>`;
    });
  }

  updateStatus() {
    chrome.runtime.sendMessage({ action: 'getStatus' }, (response) => {
      const statusBox = document.getElementById('status');
      const { profile, card } = response.status;

      if (!profile || !card) {
        statusBox.innerHTML = '<p>❌ 未載入任何資料</p>';
        statusBox.classList.remove('success');
        document.getElementById('auto-fill-btn').disabled = true;
      } else {
        statusBox.innerHTML = `
          <p>✅ 個人資訊: <strong>${profile.name}</strong></p>
          <p>   手機: ${profile.phone}</p>
          <p>   Email: ${profile.email}</p>
          <p>💳 信用卡: <strong>${card.number}</strong></p>
          <p>   有效期: ${card.exp}</p>
        `;
        statusBox.classList.add('success');
        document.getElementById('auto-fill-btn').disabled = false;
      }
    });
  }

  setupEventListeners() {
    // 載入按鈕
    document.getElementById('load-data-btn').addEventListener('click', () => {
      const profileId = document.getElementById('profile-select').value;
      if (!profileId) {
        this.showMessage('請選擇個人資訊', 'error');
        return;
      }
      chrome.runtime.sendMessage({
        action: 'loadData',
        data: { profileId }
      }, () => {
        this.showMessage(`已載入資料 ${profileId}`, 'success');
        this.updateStatus();
      });
    });

    document.getElementById('load-card-btn').addEventListener('click', () => {
      const cardId = document.getElementById('card-select').value;
      if (!cardId) {
        this.showMessage('請選擇信用卡', 'error');
        return;
      }
      chrome.runtime.sendMessage({
        action: 'loadCard',
        data: { cardId }
      }, () => {
        this.showMessage(`已載入卡號 ${cardId}`, 'success');
        this.updateStatus();
      });
    });

    // 快速組合按鈕
    const combos = {
      'combo-ab': ['A', 'A'],
      'combo-ac': ['A', 'B'],
      'combo-ba': ['B', 'A'],
      'combo-bb': ['B', 'B'],
      'combo-ca': ['C', 'A'],
      'combo-cb': ['C', 'B']
    };

    Object.entries(combos).forEach(([id, [profileId, cardId]]) => {
      const btn = document.getElementById(id);
      if (btn) {
        btn.addEventListener('click', () => {
          this.combine(profileId, cardId);
        });
      }
    });

    // 自動填表按鈕
    document.getElementById('auto-fill-btn').addEventListener('click', () => {
      this.autoFill();
    });

    // 新增資料
    document.getElementById('add-profile-btn').addEventListener('click', () => {
      this.addProfile();
    });

    document.getElementById('add-card-btn').addEventListener('click', () => {
      this.addCard();
    });

    // 刪除資料
    document.getElementById('delete-profile-btn').addEventListener('click', () => {
      this.deleteProfile();
    });

    document.getElementById('delete-card-btn').addEventListener('click', () => {
      this.deleteCard();
    });

    // 重置所有資料
    document.getElementById('reset-all-btn').addEventListener('click', () => {
      if (confirm('確定要重置所有資料嗎？')) {
        chrome.storage.local.clear(() => {
          chrome.runtime.reload();
          this.showMessage('已重置所有資料', 'success');
        });
      }
    });
  }

  combine(profileId, cardId) {
    chrome.runtime.sendMessage({
      action: 'combine',
      data: { profileId, cardId }
    }, (response) => {
      if (response.success) {
        this.showMessage(`✅ 已組合: 資料 ${profileId} + 卡號 ${cardId}`, 'success');
        this.updateStatus();
      } else {
        this.showMessage(`❌ ${response.error}`, 'error');
      }
    });
  }

  autoFill() {
    const tabs = chrome.tabs;
    tabs.query({ active: true, currentWindow: true }, (tabsArray) => {
      if (tabsArray.length === 0) {
        this.showMessage('無法取得當前標籤頁', 'error');
        return;
      }

      const tab = tabsArray[0];
      chrome.tabs.sendMessage(tab.id, { action: 'fillForm' }, () => {
        this.showMessage('✅ 自動填表已完成！請確認欄位內容', 'success');
      });
    });
  }

  addProfile() {
    const profileId = document.getElementById('new-profile-id').value;
    const name = document.getElementById('new-profile-name').value;
    const phone = document.getElementById('new-profile-phone').value;
    const id_number = document.getElementById('new-profile-id-number').value;
    const email = document.getElementById('new-profile-email').value;

    if (!profileId || !name || !phone || !id_number || !email) {
      this.showMessage('⚠️ 請填入所有欄位', 'error');
      return;
    }

    chrome.runtime.sendMessage({
      action: 'addProfile',
      data: { profileId, name, phone, id_number, email }
    }, () => {
      this.showMessage(`✅ 已新增資料 ${profileId}`, 'success');
      document.getElementById('new-profile-id').value = '';
      document.getElementById('new-profile-name').value = '';
      document.getElementById('new-profile-phone').value = '';
      document.getElementById('new-profile-id-number').value = '';
      document.getElementById('new-profile-email').value = '';
      this.loadData();
    });
  }

  addCard() {
    const cardId = document.getElementById('new-card-id').value;
    const card_number = document.getElementById('new-card-number').value;
    const exp_month = document.getElementById('new-card-month').value;
    const exp_year = document.getElementById('new-card-year').value;
    const cvv = document.getElementById('new-card-cvv').value;

    if (!cardId || !card_number || !exp_month || !exp_year || !cvv) {
      this.showMessage('⚠️ 請填入所有欄位', 'error');
      return;
    }

    chrome.runtime.sendMessage({
      action: 'addCard',
      data: { cardId, card_number, exp_month, exp_year, cvv }
    }, () => {
      this.showMessage(`✅ 已新增卡號 ${cardId}`, 'success');
      document.getElementById('new-card-id').value = '';
      document.getElementById('new-card-number').value = '';
      document.getElementById('new-card-month').value = '';
      document.getElementById('new-card-year').value = '';
      document.getElementById('new-card-cvv').value = '';
      this.loadData();
    });
  }

  deleteProfile() {
    const profileId = document.getElementById('delete-profile-select').value;
    if (!profileId) {
      this.showMessage('請選擇要刪除的資料', 'error');
      return;
    }

    if (confirm(`確定要刪除資料 ${profileId} 嗎？`)) {
      chrome.runtime.sendMessage({
        action: 'removeProfile',
        data: { profileId }
      }, () => {
        this.showMessage(`✅ 已刪除資料 ${profileId}`, 'success');
        this.loadData();
      });
    }
  }

  deleteCard() {
    const cardId = document.getElementById('delete-card-select').value;
    if (!cardId) {
      this.showMessage('請選擇要刪除的卡號', 'error');
      return;
    }

    if (confirm(`確定要刪除卡號 ${cardId} 嗎？`)) {
      chrome.runtime.sendMessage({
        action: 'removeCard',
        data: { cardId }
      }, () => {
        this.showMessage(`✅ 已刪除卡號 ${cardId}`, 'success');
        this.loadData();
      });
    }
  }

  switchTab(tabName) {
    // 隱藏所有標籤內容
    document.querySelectorAll('.tab-content').forEach(tab => {
      tab.style.display = 'none';
    });

    // 取消所有標籤按鈕的 active 狀態
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });

    // 顯示選擇的標籤內容
    if (tabName === 'main') {
      document.querySelector('.main-content').style.display = 'block';
    } else if (tabName === 'manage') {
      document.getElementById('manage-tab').style.display = 'block';
    } else if (tabName === 'settings') {
      document.getElementById('settings-tab').style.display = 'block';
    }

    // 標記按鈕為 active
    event.target.classList.add('active');
  }

  showMessage(message, type = 'info') {
    const messageBox = document.getElementById('message');
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`;
    messageBox.style.display = 'block';

    setTimeout(() => {
      messageBox.style.display = 'none';
    }, 3000);
  }
}

// 初始化應用
document.addEventListener('DOMContentLoaded', () => {
  new PopupApp();
});
