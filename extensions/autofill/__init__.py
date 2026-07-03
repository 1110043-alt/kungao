"""
多帳號自動結帳填表助手 - 擴充包
資料和信用卡分開管理，自由組合
"""

from .data_manager import DataManager

__version__ = "1.0.0"
__author__ = "AutoFill Assistant"

# 全域管理器實例
manager = DataManager()

__all__ = ["manager", "DataManager"]
