/**
 * 內容腳本 - Content Script
 * 在網頁中執行，自動偵測和填表
 */

class AutoFiller {
  constructor() {
    this.filled_count = 0;
    this.setupListeners();
  }

  // 設置事件監聽
  setupListeners() {
    // 監聽來自 popup 的自動填表命令
    window.addEventListener('message', (event) => {
      if (event.source !== window) return;

      if (event.data.type && event.data.type === 'AUTO_FILL_FORM') {
        this.fillForm();
      }
    });
  }

  // 自動掃描並填表
  async fillForm() {
    this.filled_count = 0;
    
    console.log("🤖 開始自動填表...");

    // 取得所有表單欄位
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], input[type="password"]');
    const selects = document.querySelectorAll('select');
    const textareas = document.querySelectorAll('textarea');

    console.log(`🔍 找到 ${inputs.length} 個輸入框`);

    // 處理所有 input
    for (const field of inputs) {
      await this._fillField(field);
    }

    // 處理所有 select
    for (const field of selects) {
      await this._fillSelect(field);
    }

    // 處理所有 textarea
    for (const field of textareas) {
      await this._fillField(field);
    }

    console.log(`✅ 填表完成！共填入 ${this.filled_count} 個欄位`);
    
    // 通知 popup 填表完成
    chrome.runtime.sendMessage({
      action: 'fillComplete',
      count: this.filled_count
    });
  }

  async _fillField(field) {
    try {
      // 取得所有可用的識別資訊
      const fieldType = field.getAttribute('type') || 'text';
      const fieldName = (field.getAttribute('name') || '').toLowerCase();
      const fieldId = (field.getAttribute('id') || '').toLowerCase();
      const placeholder = (field.getAttribute('placeholder') || '').toLowerCase();
      const label = this._getLabel(field);

      const allText = `${fieldName} ${fieldId} ${placeholder} ${label}`;

      let value = null;
      let fieldTypeName = '';

      // 比對規則
      if (this._matches(allText, ['name', '姓名', 'fullname', 'user'])) {
        value = await this._getValue('name');
        fieldTypeName = '姓名';
      } else if (this._matches(allText, ['phone', '手機', '電話', 'mobile', 'cell'])) {
        value = await this._getValue('phone');
        fieldTypeName = '手機';
      } else if (this._matches(allText, ['id', '身分證', '證件', 'id_number'])) {
        value = await this._getValue('id');
        fieldTypeName = '身分證';
      } else if (this._matches(allText, ['email', '信箱', 'mail'])) {
        value = await this._getValue('email');
        fieldTypeName = 'Email';
      } else if (this._matches(allText, ['card', '卡號', 'cardnumber', 'cc'])) {
        value = await this._getValue('card');
        fieldTypeName = '卡號';
      } else if (this._matches(allText, ['cvv', 'cvc', '安全碼', 'security', '驗證'])) {
        value = await this._getValue('cvv');
        fieldTypeName = 'CVV';
      }

      if (value) {
        field.value = value;
        field.dispatchEvent(new Event('input', { bubbles: true }));
        field.dispatchEvent(new Event('change', { bubbles: true }));
        console.log(`  ✓ ${fieldTypeName}: 已填入`);
        this.filled_count++;
      }
    } catch (e) {
      // 靜默跳過
    }
  }

  async _fillSelect(field) {
    try {
      const fieldName = (field.getAttribute('name') || '').toLowerCase();
      const fieldId = (field.getAttribute('id') || '').toLowerCase();
      const allText = `${fieldName} ${fieldId}`;

      let value = null;
      let fieldTypeName = '';

      if (this._matches(allText, ['month', '月份', 'exp_month', 'mm'])) {
        value = await this._getValue('month');
        fieldTypeName = '月份';
      } else if (this._matches(allText, ['year', '年份', 'exp_year', 'yyyy', 'yy'])) {
        value = await this._getValue('year');
        fieldTypeName = '年份';
      }

      if (value) {
        field.value = value;
        field.dispatchEvent(new Event('change', { bubbles: true }));
        console.log(`  ✓ ${fieldTypeName}: 已選擇`);
        this.filled_count++;
      }
    } catch (e) {
      // 靜默跳過
    }
  }

  async _getValue(fieldType) {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({
        action: 'getFieldValue',
        data: { fieldType }
      }, (response) => {
        resolve(response.value);
      });
    });
  }

  _matches(text, keywords) {
    return keywords.some(kw => text.includes(kw.toLowerCase()));
  }

  _getLabel(field) {
    const label = field.closest('label');
    if (label) return label.textContent.toLowerCase();
    
    const labelFor = document.querySelector(`label[for="${field.id}"]`);
    if (labelFor) return labelFor.textContent.toLowerCase();
    
    return '';
  }
}

// 初始化
const autoFiller = new AutoFiller();

// 監聽來自 popup 的自動填表命令
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'fillForm') {
    autoFiller.fillForm();
    sendResponse({ success: true });
  }
});

// 與 popup 通信
window.addEventListener('message', (event) => {
  if (event.source !== window) return;
  if (event.data.type && event.data.type === 'AUTO_FILL_FORM') {
    autoFiller.fillForm();
  }
});

console.log("✅ 自動填表擴充包已載入");
