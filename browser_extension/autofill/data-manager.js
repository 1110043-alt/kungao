/**
 * 多帳號自動結帳填表 - 資料管理核心
 * 在 Service Worker 中管理所有資料
 */

class DataManager {
  constructor() {
    this.profiles = {};
    this.cards = {};
    this.currentProfile = null;
    this.currentCard = null;
    this.loadFromStorage();
  }

  // ===== 初始化預設資料 =====
  async initializeDefaults() {
    const defaults = {
      profiles: {
        "A": {
          name: "王小明",
          phone: "0912345678",
          id_number: "A123456789",
          email: "wang@example.com"
        },
        "B": {
          name: "李美琪",
          phone: "0987654321",
          id_number: "B987654321",
          email: "li@example.com"
        },
        "C": {
          name: "張大衛",
          phone: "0956789012",
          id_number: "C456789012",
          email: "chang@example.com"
        }
      },
      cards: {
        "A": {
          card_number: "4111111111111111",
          exp_month: "12",
          exp_year: "2025",
          cvv: "123"
        },
        "B": {
          card_number: "5555555555554444",
          exp_month: "08",
          exp_year: "2026",
          cvv: "456"
        },
        "C": {
          card_number: "378282246310005",
          exp_month: "03",
          exp_year: "2027",
          cvv: "789"
        }
      }
    };

    await chrome.storage.local.set(defaults);
    this.profiles = defaults.profiles;
    this.cards = defaults.cards;
  }

  // ===== 存儲操作 =====
  async loadFromStorage() {
    return new Promise((resolve) => {
      chrome.storage.local.get(['profiles', 'cards'], (result) => {
        this.profiles = result.profiles || {};
        this.cards = result.cards || {};
        
        if (Object.keys(this.profiles).length === 0) {
          this.initializeDefaults().then(resolve);
        } else {
          resolve();
        }
      });
    });
  }

  async saveToStorage() {
    return new Promise((resolve) => {
      chrome.storage.local.set({
        profiles: this.profiles,
        cards: this.cards
      }, resolve);
    });
  }

  // ===== 組合操作 =====
  combine(profileId, cardId) {
    const profile = this.profiles[profileId.toUpperCase()];
    const card = this.cards[cardId.toUpperCase()];

    if (!profile || !card) {
      return {
        success: false,
        error: !profile ? `找不到資料: ${profileId}` : `找不到卡號: ${cardId}`
      };
    }

    this.currentProfile = profile;
    this.currentCard = card;

    return {
      success: true,
      profile: profile,
      card: {
        card_number: `****${card.card_number.slice(-4)}`,
        exp_month: card.exp_month,
        exp_year: card.exp_year
      }
    };
  }

  // ===== 資料載入 =====
  loadData(profileId) {
    const profile = this.profiles[profileId.toUpperCase()];
    if (profile) {
      this.currentProfile = profile;
      return { success: true, profile };
    }
    return { success: false, error: `找不到資料: ${profileId}` };
  }

  loadCard(cardId) {
    const card = this.cards[cardId.toUpperCase()];
    if (card) {
      this.currentCard = card;
      return { success: true, card };
    }
    return { success: false, error: `找不到卡號: ${cardId}` };
  }

  // ===== 取得欄位值 =====
  getFieldValue(fieldType) {
    if (!this.currentProfile || !this.currentCard) {
      return null;
    }

    fieldType = fieldType.toLowerCase();

    // 個人資訊欄位
    if (['name', '姓名', 'fullname'].includes(fieldType)) {
      return this.currentProfile.name;
    } else if (['phone', '手機', '電話', 'mobile', 'cell'].includes(fieldType)) {
      return this.currentProfile.phone;
    } else if (['id', '身分證', '證件號碼', 'id_number'].includes(fieldType)) {
      return this.currentProfile.id_number;
    } else if (['email', '信箱', 'mail'].includes(fieldType)) {
      return this.currentProfile.email;
    }

    // 信用卡欄位
    else if (['card', '卡號', 'cardnumber', 'cc-number'].includes(fieldType)) {
      return this.currentCard.card_number;
    } else if (['month', '月份', 'exp_month', 'mm'].includes(fieldType)) {
      return this.currentCard.exp_month;
    } else if (['year', '年份', 'exp_year', 'yyyy'].includes(fieldType)) {
      return this.currentCard.exp_year;
    } else if (['cvv', 'cvc', '安全碼', 'security'].includes(fieldType)) {
      return this.currentCard.cvv;
    }

    return null;
  }

  // ===== 新增資料 =====
  async addProfile(profileId, name, phone, id_number, email) {
    this.profiles[profileId.toUpperCase()] = {
      name, phone, id_number, email
    };
    await this.saveToStorage();
    return { success: true };
  }

  async addCard(cardId, card_number, exp_month, exp_year, cvv) {
    this.cards[cardId.toUpperCase()] = {
      card_number, exp_month, exp_year, cvv
    };
    await this.saveToStorage();
    return { success: true };
  }

  // ===== 刪除資料 =====
  async removeProfile(profileId) {
    const id = profileId.toUpperCase();
    if (this.profiles[id]) {
      delete this.profiles[id];
      await this.saveToStorage();
      return { success: true };
    }
    return { success: false, error: `找不到資料: ${profileId}` };
  }

  async removeCard(cardId) {
    const id = cardId.toUpperCase();
    if (this.cards[id]) {
      delete this.cards[id];
      await this.saveToStorage();
      return { success: true };
    }
    return { success: false, error: `找不到卡號: ${cardId}` };
  }

  // ===== 查詢 =====
  listProfiles() {
    return Object.keys(this.profiles);
  }

  listCards() {
    return Object.keys(this.cards);
  }

  getStatus() {
    return {
      profile: this.currentProfile ? {
        name: this.currentProfile.name,
        phone: this.currentProfile.phone,
        id: this.currentProfile.id_number,
        email: this.currentProfile.email
      } : null,
      card: this.currentCard ? {
        number: `****${this.currentCard.card_number.slice(-4)}`,
        exp: `${this.currentCard.exp_month}/${this.currentCard.exp_year}`
      } : null
    };
  }
}

// 全域實例
const dataManager = new DataManager();
