"""
個人資訊資料庫 - 可自由新增、修改
格式：每組資料包含基本聯絡資訊
"""

PROFILES = {
    "A": {
        "name": "王小明",
        "phone": "0912345678",
        "id_number": "A123456789",
        "email": "wang@example.com"
    },
    "B": {
        "name": "李美琪",
        "phone": "0987654321",
        "id_number": "B987654321",
        "email": "li@example.com"
    },
    "C": {
        "name": "張大衛",
        "phone": "0956789012",
        "id_number": "C456789012",
        "email": "chang@example.com"
    }
}

def get_profile(profile_id):
    """取得指定的個人資訊"""
    return PROFILES.get(profile_id.upper())

def add_profile(profile_id, name, phone, id_number, email):
    """新增個人資訊"""
    PROFILES[profile_id.upper()] = {
        "name": name,
        "phone": phone,
        "id_number": id_number,
        "email": email
    }

def list_profiles():
    """列出所有可用的個人資訊"""
    return list(PROFILES.keys())

def remove_profile(profile_id):
    """刪除個人資訊"""
    if profile_id.upper() in PROFILES:
        del PROFILES[profile_id.upper()]
        return True
    return False
