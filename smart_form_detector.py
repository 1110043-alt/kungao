#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智能表單字段檢測和自動填寫引擎"""

import asyncio
import random
from typing import Dict, List, Tuple

class SmartFormDetector:
    """使用 AI 邏輯的智能表單檢測器"""
    
    def __init__(self, progress_callback=None):
        """
        初始化智能檢測器
        
        progress_callback: 用於輸出日誌的回調函數
        """
        self.progress = progress_callback or print
        
        # 字段用途關鍵詞匹配
        self.field_patterns = {
            'email': ['email', 'mail', '郵件', '電郵', '信箱', 'e-mail'],
            'address': ['address', '地址', '收件', '街道', '路號', '住址', 'addr'],
            'name': ['name', '名字', '姓名', '全名', 'fullname'],
            'phone': ['phone', '電話', '手機', '號碼', 'mobile', 'tel'],
            'id': ['identity', 'id', '身分', '證件', '編號', 'number'],
            'birthdate': ['birth', '生日', '出生', 'date'],
            'gender': ['gender', '性別', 'sex'],
            'city': ['city', '縣市', '城市', 'county'],
            'district': ['district', '區', '鄉鎮', 'township'],
        }
    
    async def scan_all_fields(self, page) -> List[Dict]:
        """
        掃描頁面上的所有表單字段
        
        返回: [{"name": "...", "id": "...", "tag": "...", "score": 0.8, "type": "email", ...}]
        """
        self.progress("[智能] 🔍 掃描頁面所有表單字段...")
        
        all_fields = []
        
        # 掃描所有 input、select、textarea
        field_selectors = [
            "input",
            "select", 
            "textarea"
        ]
        
        for selector in field_selectors:
            try:
                fields = await page.locator(selector).all()
                self.progress(f"[智能]   找到 {len(fields)} 個 <{selector}> 元素")
                
                for idx, field in enumerate(fields):
                    try:
                        field_info = await self._analyze_field(page, field, selector)
                        if field_info:
                            all_fields.append(field_info)
                    except Exception as e:
                        pass
            except:
                pass
        
        self.progress(f"[智能] ✅ 掃描完成：找到 {len(all_fields)} 個可用欄位")
        
        # 按匹配度排序
        all_fields.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return all_fields
    
    async def _analyze_field(self, page, field, tag_name) -> Dict:
        """分析單個字段，返回其特徵"""
        try:
            field_info = {
                'tag': tag_name,
                'attributes': {}
            }
            
            # 收集字段屬性
            attrs = ['name', 'id', 'type', 'placeholder', 'aria-label', 'class', 'value']
            for attr in attrs:
                try:
                    val = await field.get_attribute(attr)
                    if val:
                        field_info['attributes'][attr] = val
                except:
                    pass
            
            # 收集相關的 label 文本
            try:
                # 尋找 for 屬性
                field_id = field_info['attributes'].get('id')
                if field_id:
                    label = await page.locator(f"label[for='{field_id}']").first.text_content()
                    if label:
                        field_info['label'] = label.strip()
            except:
                pass
            
            # 收集周圍文本（上下文）
            try:
                parent = await field.evaluate("el => el.parentElement.textContent")
                if parent:
                    field_info['context'] = parent[:200]
            except:
                pass
            
            # 推斷字段用途（評分）
            field_info['type_scores'] = self._score_field_type(field_info)
            
            # 取最高分的類型
            if field_info['type_scores']:
                best_type = max(field_info['type_scores'], key=field_info['type_scores'].get)
                field_info['predicted_type'] = best_type
                field_info['confidence'] = field_info['type_scores'][best_type]
            
            return field_info
        except:
            return None
    
    def _score_field_type(self, field_info: Dict) -> Dict[str, float]:
        """根據字段特徵計算各類型的匹配度"""
        scores = {}
        
        # 收集所有可用的文本信息
        all_text = ""
        all_text += field_info['attributes'].get('name', '').lower() + " "
        all_text += field_info['attributes'].get('id', '').lower() + " "
        all_text += field_info['attributes'].get('placeholder', '').lower() + " "
        all_text += field_info['attributes'].get('aria-label', '').lower() + " "
        all_text += field_info.get('label', '').lower() + " "
        all_text += field_info.get('context', '').lower() + " "
        
        # 對每種字段類型評分
        for field_type, keywords in self.field_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in all_text:
                    score += 1
            scores[field_type] = score
        
        return scores
    
    async def auto_fill_smart(self, page, fields: List[Dict], data: Dict) -> int:
        """
        智能自動填寫表單
        
        data: {"name": "楊柏宏", "email": "...", "address": "...", ...}
        返回: 填寫的欄位數量
        """
        self.progress("[智能] 📝 開始智能填寫表單...")
        
        filled_count = 0
        used_fields = set()  # 追蹤已使用的欄位，避免重複
        
        # 按用途匹配數據和字段
        type_to_data = {
            'email': data.get('email', ''),
            'address': data.get('address', ''),
            'name': data.get('name', ''),
            'phone': data.get('phone', ''),
            'id': data.get('id', ''),
            'birthdate': data.get('birthdate', ''),
        }
        
        for field_info in fields:
            if not type_to_data or not field_info:
                break
            
            field_id = id(field_info)
            if field_id in used_fields:
                continue
            
            predicted_type = field_info.get('predicted_type')
            confidence = field_info.get('confidence', 0)
            
            if predicted_type and confidence > 0:
                value_to_fill = type_to_data.get(predicted_type, '')
                
                if value_to_fill:
                    try:
                        # 根據字段 ID/name 重新獲取元素
                        field = None
                        field_id_attr = field_info['attributes'].get('id')
                        field_name_attr = field_info['attributes'].get('name')
                        
                        if field_id_attr:
                            field = page.locator(f"#{field_id_attr}").first
                        elif field_name_attr:
                            field = page.locator(f"[name='{field_name_attr}']").first
                        
                        if field:
                            tag = field_info.get('tag')
                            
                            if tag == 'select':
                                # 下拉菜單
                                if predicted_type in ['city', 'district']:
                                    options = await field.locator("option").all()
                                    if len(options) > 1:
                                        selected = random.choice(options[1:])
                                        opt_value = await selected.get_attribute("value")
                                        await field.select_option(opt_value)
                                        self.progress(f"[智能] ✓ {predicted_type} 已選 (信心度: {confidence:.2f})")
                                        filled_count += 1
                                        used_fields.add(field_id)
                            else:
                                # 文本輸入
                                try:
                                    await field.fill(value_to_fill, timeout=2000)
                                except:
                                    await field.clear()
                                    await field.type(value_to_fill, delay=30)
                                
                                self.progress(f"[智能] ✓ {predicted_type} 已填 (信心度: {confidence:.2f})")
                                filled_count += 1
                                used_fields.add(field_id)
                                
                                await asyncio.sleep(0.2)
                    except Exception as e:
                        self.progress(f"[智能] ✗ {predicted_type} 填寫失敗: {str(e)[:30]}")
        
        self.progress(f"[智能] 📊 自動填寫完成: {filled_count} 個欄位")
        return filled_count
    
    def print_field_analysis(self, fields: List[Dict]):
        """打印字段分析結果（用於調試）"""
        self.progress("\n" + "=" * 70)
        self.progress("📊 表單欄位分析結果")
        self.progress("=" * 70)
        
        for idx, field in enumerate(fields[:15], 1):
            predicted = field.get('predicted_type', '未知')
            confidence = field.get('confidence', 0)
            name = field['attributes'].get('name', 'N/A')
            field_id = field['attributes'].get('id', 'N/A')
            placeholder = field['attributes'].get('placeholder', '')
            label = field.get('label', '')
            
            self.progress(f"\n[{idx}] {predicted.upper()} (信心度: {confidence:.2f})")
            self.progress(f"     name={name}, id={field_id}")
            self.progress(f"     placeholder={placeholder}")
            if label:
                self.progress(f"     label={label[:50]}")
        
        self.progress("\n" + "=" * 70)
