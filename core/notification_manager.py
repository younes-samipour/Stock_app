"""
این ماژول مدیریت اعلان‌ها و هشدارهای برنامه را بر عهده دارد.
این ماژول امکانات زیر را فراهم می‌کند:
- ارسال اعلان‌های قیمتی
- ارسال هشدارهای تکنیکال
- مدیریت شرایط هشدار
- ذخیره و بازیابی تنظیمات هشدار
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
import os
from .exceptions import ValidationError

class NotificationManager:
    def __init__(self):
        """
        سازنده کلاس NotificationManager
        راه‌اندازی مدیریت اعلان‌ها با تنظیمات پایه
        """
        self.alerts = {}
        self.alert_conditions = {}
        self.settings_file = 'data/alerts.json'
        
        # بارگذاری تنظیمات هشدار
        self.load_alert_settings()
    
    def load_alert_settings(self):
        """
        بارگذاری تنظیمات هشدار از فایل
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.alerts = settings.get('alerts', {})
                    self.alert_conditions = settings.get('conditions', {})
        except Exception as e:
            print(f"Error loading alert settings: {str(e)}")
    
    def save_alert_settings(self):
        """
        ذخیره تنظیمات هشدار در فایل
        """
        try:
            settings = {
                'alerts': self.alerts,
                'conditions': self.alert_conditions
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving alert settings: {str(e)}")
    
    def add_price_alert(self, symbol, price, condition='above'):
        """
        افزودن هشدار قیمتی
        symbol: نماد سهم
        price: قیمت هشدار
        condition: شرط هشدار ('above' یا 'below')
        """
        if condition not in ['above', 'below']:
            raise ValidationError("شرط هشدار نامعتبر است")
            
        if symbol not in self.alerts:
            self.alerts[symbol] = []
            
        self.alerts[symbol].append({
            'type': 'price',
            'price': float(price),
            'condition': condition,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'active': True
        })
        
        self.save_alert_settings()
    
    def add_technical_alert(self, symbol, indicator, value, condition):
        """
        افزودن هشدار تکنیکال
        symbol: نماد سهم
        indicator: نام اندیکاتور
        value: مقدار هشدار
        condition: شرط هشدار
        """
        if symbol not in self.alerts:
            self.alerts[symbol] = []
            
        self.alerts[symbol].append({
            'type': 'technical',
            'indicator': indicator,
            'value': float(value),
            'condition': condition,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'active': True
        })
        
        self.save_alert_settings()
    
    def check_alerts(self, symbol, current_data):
        """
        بررسی هشدارها برای یک سهم
        symbol: نماد سهم
        current_data: داده‌های فعلی سهم
        return: لیست هشدارهای فعال شده
        """
        triggered_alerts = []
        
        if symbol in self.alerts:
            for alert in self.alerts[symbol]:
                if not alert['active']:
                    continue
                    
                if alert['type'] == 'price':
                    if self._check_price_condition(
                        current_data['close'],
                        alert['price'],
                        alert['condition']
                    ):
                        triggered_alerts.append(alert)
                        
                elif alert['type'] == 'technical':
                    if self._check_technical_condition(
                        current_data,
                        alert['indicator'],
                        alert['value'],
                        alert['condition']
                    ):
                        triggered_alerts.append(alert)
        
        return triggered_alerts
    
    def show_alert(self, symbol, alert):
        """
        نمایش هشدار به کاربر
        symbol: نماد سهم
        alert: اطلاعات هشدار
        """
        title = "هشدار سهام"
        if alert['type'] == 'price':
            message = (
                f"هشدار قیمتی برای {symbol}\n"
                f"قیمت {alert['condition']} {alert['price']:,}"
            )
        else:
            message = (
                f"هشدار تکنیکال برای {symbol}\n"
                f"{alert['indicator']} {alert['condition']} {alert['value']}"
            )
            
        messagebox.showinfo(title, message)
    
    def _check_price_condition(self, current_price, alert_price, condition):
        """
        بررسی شرط قیمتی
        current_price: قیمت فعلی
        alert_price: قیمت هشدار
        condition: شرط مقایسه
        return: نتیجه بررسی شرط
        """
        if condition == 'above':
            return current_price > alert_price
        elif condition == 'below':
            return current_price < alert_price
        return False
    
    def _check_technical_condition(self, data, indicator, value, condition):
        """
        بررسی شرط تکنیکال
        data: داده‌های سهم
        indicator: نام اندیکاتور
        value: مقدار هشدار
        condition: شرط مقایسه
        return: نتیجه بررسی شرط
        """
        # پیاده‌سازی بررسی شرط‌های تکنیکال
        pass 