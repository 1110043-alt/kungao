"""
資料管理器 - 核心邏輯
負責載入資料和信用卡，以及自動填表
"""

from . import data_profiles
from . import payment_cards

class DataManager:
    """多帳號自動結帳填表管理器"""
    
    def __init__(self):
        self.current_profile = None
        self.current_card = None
    
    # ===== 資料管理 =====
    def load_data(self, profile_id):
        """載入指定的個人資訊"""
        profile = data_profiles.get_profile(profile_id)
        if profile:
            self.current_profile = profile
            print(f"✅ 已載入資料: {profile_id} ({profile['name']})")
            return profile
        else:
            print(f"❌ 找不到資料: {profile_id}")
            return None
    
    def load_card(self, card_id):
        """載入指定的信用卡"""
        card = payment_cards.get_card(card_id)
        if card:
            self.current_card = card
            print(f"✅ 已載入卡號: {card_id} (****{card['card_number'][-4:]})")
            return card
        else:
            print(f"❌ 找不到卡號: {card_id}")
            return None
    
    def combine(self, profile_id, card_id):
        """組合個人資訊和信用卡，一次性載入"""
        print(f"\n🔄 正在組合: 資料 {profile_id} + 卡號 {card_id}")
        profile = self.load_data(profile_id)
        card = self.load_card(card_id)
        
        if profile and card:
            print(f"✅ 組合成功！已準備好填表\n")
            return self.get_combined()
        else:
            print(f"❌ 組合失敗\n")
            return None
    
    def get_combined(self):
        """取得當前已組合的完整資料"""
        if not self.current_profile or not self.current_card:
            return None
        
        return {
            "profile": self.current_profile,
            "card": self.current_card
        }
    
    # ===== 查詢功能 =====
    def list_available_data(self):
        """列出所有可用的個人資訊"""
        profiles = data_profiles.list_profiles()
        print(f"可用的個人資訊: {', '.join(profiles)}")
        return profiles
    
    def list_available_cards(self):
        """列出所有可用的信用卡"""
        cards = payment_cards.list_cards()
        print(f"可用的信用卡: {', '.join(cards)}")
        return cards
    
    # ===== 新增資料 =====
    def add_new_data(self, profile_id, name, phone, id_number, email):
        """新增個人資訊"""
        data_profiles.add_profile(profile_id, name, phone, id_number, email)
        print(f"✅ 已新增資料: {profile_id}")
    
    def add_new_card(self, card_id, card_number, exp_month, exp_year, cvv):
        """新增信用卡"""
        payment_cards.add_card(card_id, card_number, exp_month, exp_year, cvv)
        print(f"✅ 已新增卡號: {card_id}")
    
    # ===== 刪除資料 =====
    def remove_data(self, profile_id):
        """刪除個人資訊"""
        if data_profiles.remove_profile(profile_id):
            print(f"✅ 已刪除資料: {profile_id}")
        else:
            print(f"❌ 找不到資料: {profile_id}")
    
    def remove_card(self, card_id):
        """刪除信用卡"""
        if payment_cards.remove_card(card_id):
            print(f"✅ 已刪除卡號: {card_id}")
        else:
            print(f"❌ 找不到卡號: {card_id}")
    
    # ===== 取得填表資料 =====
    def get_field_value(self, field_type):
        """根據欄位類型取得對應的值"""
        if not self.current_profile or not self.current_card:
            return None
        
        field_type = field_type.lower()
        
        # 個人資訊欄位
        if field_type in ["name", "姓名", "聯絡人", "收件人"]:
            return self.current_profile.get("name")
        elif field_type in ["phone", "手機", "電話", "聯絡電話"]:
            return self.current_profile.get("phone")
        elif field_type in ["id", "身分證", "證件號碼", "身分證字號"]:
            return self.current_profile.get("id_number")
        elif field_type in ["email", "信箱", "電子郵件"]:
            return self.current_profile.get("email")
        
        # 信用卡欄位
        elif field_type in ["card", "卡號", "credit card", "card number"]:
            return self.current_card.get("card_number")
        elif field_type in ["month", "月份", "exp month", "mm"]:
            return self.current_card.get("exp_month")
        elif field_type in ["year", "年份", "exp year", "yyyy"]:
            return self.current_card.get("exp_year")
        elif field_type in ["cvv", "cvc", "安全碼", "驗證碼"]:
            return self.current_card.get("cvv")
        
        return None
    
    # ===== 狀態顯示 =====
    def show_status(self):
        """顯示當前載入的資訊"""
        print("\n" + "="*50)
        print("📋 目前狀態")
        print("="*50)
        
        if self.current_profile:
            print(f"✅ 個人資訊: {self.current_profile['name']}")
            print(f"   - 手機: {self.current_profile['phone']}")
            print(f"   - 身分證: {self.current_profile['id_number']}")
            print(f"   - Email: {self.current_profile['email']}")
        else:
            print("❌ 未載入個人資訊")
        
        if self.current_card:
            print(f"✅ 信用卡: ****{self.current_card['card_number'][-4:]}")
            print(f"   - 有效期: {self.current_card['exp_month']}/{self.current_card['exp_year']}")
        else:
            print("❌ 未載入信用卡")
        
        print("="*50 + "\n")
