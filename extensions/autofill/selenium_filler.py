"""
Selenium 網頁自動填表整合模組
自動偵測表單欄位並填入資料
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

class AutoFiller:
    """Selenium 自動填表助手"""
    
    def __init__(self, driver):
        """初始化填表助手
        Args:
            driver: Selenium WebDriver 實例
        """
        self.driver = driver
        self.filled_count = 0
    
    def fill_form(self, manager):
        """自動掃描並填表
        Args:
            manager: DataManager 實例（已載入資料和卡號）
        Returns:
            已填入的欄位數量
        """
        self.filled_count = 0
        
        # 取得所有表單欄位
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
        
        print(f"\n🔍 掃描表單... (找到 {len(inputs)} 個輸入框)")
        
        # 處理所有 input 和 textarea
        all_fields = inputs + textareas
        for field in all_fields:
            self._fill_field(field, manager)
        
        # 處理所有 select
        for select_field in selects:
            self._fill_select(select_field, manager)
        
        print(f"✅ 自動填表完成！共填入 {self.filled_count} 個欄位\n")
        return self.filled_count
    
    def _fill_field(self, field, manager):
        """填入單個欄位"""
        try:
            field_type = field.get_attribute("type") or "text"
            field_name = field.get_attribute("name") or ""
            field_id = field.get_attribute("id") or ""
            placeholder = field.get_attribute("placeholder") or ""
            label_text = self._get_label_text(field)
            
            # 組合所有可用的文字資訊進行比對
            all_text = (field_name + " " + field_id + " " + placeholder + " " + label_text).lower()
            
            value = None
            
            # 比對規則
            if any(kw in all_text for kw in ["name", "姓名", "聯絡人", "收件人", "full"]):
                value = manager.get_field_value("name")
                if value:
                    field.clear()
                    field.send_keys(value)
                    print(f"  ✓ 姓名: {value}")
                    self.filled_count += 1
            
            elif any(kw in all_text for kw in ["phone", "手機", "電話", "mobile", "cell"]):
                value = manager.get_field_value("phone")
                if value:
                    field.clear()
                    field.send_keys(value)
                    print(f"  ✓ 手機: {value}")
                    self.filled_count += 1
            
            elif any(kw in all_text for kw in ["id", "身分證", "証件", "id_number"]):
                value = manager.get_field_value("id")
                if value:
                    field.clear()
                    field.send_keys(value)
                    print(f"  ✓ 身分證: {value}")
                    self.filled_count += 1
            
            elif any(kw in all_text for kw in ["email", "信箱", "mail", "e-mail"]):
                value = manager.get_field_value("email")
                if value:
                    field.clear()
                    field.send_keys(value)
                    print(f"  ✓ Email: {value}")
                    self.filled_count += 1
            
            elif any(kw in all_text for kw in ["card", "卡號", "cardnumber", "cc-number"]):
                value = manager.get_field_value("card")
                if value:
                    field.clear()
                    field.send_keys(value)
                    print(f"  ✓ 卡號: ****{value[-4:]}")
                    self.filled_count += 1
            
            elif any(kw in all_text for kw in ["cvv", "cvc", "安全碼", "security"]):
                value = manager.get_field_value("cvv")
                if value:
                    field.clear()
                    field.send_keys(value)
                    print(f"  ✓ CVV: {value}")
                    self.filled_count += 1
        
        except Exception as e:
            pass  # 靜默跳過無法填入的欄位
    
    def _fill_select(self, select_field, manager):
        """填入 select 欄位"""
        try:
            field_name = select_field.get_attribute("name") or ""
            field_id = select_field.get_attribute("id") or ""
            all_text = (field_name + " " + field_id).lower()
            
            select = Select(select_field)
            value = None
            
            if any(kw in all_text for kw in ["month", "月份", "mm", "exp_month"]):
                value = manager.get_field_value("month")
                if value:
                    try:
                        select.select_by_value(value)
                        print(f"  ✓ 月份: {value}")
                        self.filled_count += 1
                    except:
                        try:
                            select.select_by_visible_text(value)
                            self.filled_count += 1
                        except:
                            pass
            
            elif any(kw in all_text for kw in ["year", "年份", "yyyy", "yy", "exp_year"]):
                value = manager.get_field_value("year")
                if value:
                    try:
                        select.select_by_value(value)
                        print(f"  ✓ 年份: {value}")
                        self.filled_count += 1
                    except:
                        try:
                            select.select_by_visible_text(value)
                            self.filled_count += 1
                        except:
                            pass
        
        except Exception as e:
            pass  # 靜默跳過無法填入的欄位
    
    def _get_label_text(self, field):
        """取得欄位對應的 label 文字"""
        try:
            field_id = field.get_attribute("id")
            if field_id:
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                return label.text
        except:
            pass
        return ""
