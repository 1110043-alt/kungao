"""
信用卡資訊資料庫 - 可自由新增、修改
格式：每張卡包含卡號、有效月份、有效年份、CVV
"""

CARDS = {
    "A": {
        "card_number": "4111111111111111",
        "exp_month": "12",
        "exp_year": "2025",
        "cvv": "123"
    },
    "B": {
        "card_number": "5555555555554444",
        "exp_month": "08",
        "exp_year": "2026",
        "cvv": "456"
    },
    "C": {
        "card_number": "378282246310005",
        "exp_month": "03",
        "exp_year": "2027",
        "cvv": "789"
    }
}

def get_card(card_id):
    """取得指定的信用卡資訊"""
    return CARDS.get(card_id.upper())

def add_card(card_id, card_number, exp_month, exp_year, cvv):
    """新增信用卡資訊"""
    CARDS[card_id.upper()] = {
        "card_number": card_number,
        "exp_month": exp_month,
        "exp_year": exp_year,
        "cvv": cvv
    }

def list_cards():
    """列出所有可用的信用卡"""
    return list(CARDS.keys())

def remove_card(card_id):
    """刪除信用卡資訊"""
    if card_id.upper() in CARDS:
        del CARDS[card_id.upper()]
        return True
    return False
