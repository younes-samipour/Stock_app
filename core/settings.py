"""
این ماژول مدیریت تنظیمات برنامه را بر عهده دارد.
این ماژول امکانات زیر را فراهم می‌کند:
- بارگذاری و ذخیره تنظیمات
- اعمال تنظیمات پیش‌فرض
- اعتبارسنجی تنظیمات
- مدیریت تنظیمات کاربر
"""

import json
import os
from .constants import DEFAULT_SETTINGS, FILE_PATHS
from .exceptions import ConfigError

class Settings:
    def __init__(self):
        """
        سازنده کلاس Settings
        بارگذاری تنظیمات از فایل یا اعمال تنظیمات پیش‌فرض
        """
        self.settings = {}
        self.config_file = FILE_PATHS['config']
        
        # ایجاد دایرکتوری تنظیمات اگر وجود نداشته باشد
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # بارگذاری تنظیمات
        self.load_settings()
    
    def load_settings(self):
        """
        بارگذاری تنظیمات از فایل
        در صورت عدم وجود فایل، از تنظیمات پیش‌فرض استفاده می‌شود
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # ادغام تنظیمات بارگذاری شده با تنظیمات پیش‌فرض
                    self.settings = self._merge_settings(DEFAULT_SETTINGS, loaded_settings)
            else:
                # استفاده از تنظیمات پیش‌فرض
                self.settings = DEFAULT_SETTINGS.copy()
                self.save_settings()
                
        except Exception as e:
            raise ConfigError(f"خطا در بارگذاری تنظیمات: {str(e)}")
    
    def save_settings(self):
        """
        ذخیره تنظیمات در فایل
        تنظیمات در فرمت JSON ذخیره می‌شوند
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise ConfigError(f"خطا در ذخیره تنظیمات: {str(e)}")
    
    def get_setting(self, category, key, default=None):
        """
        دریافت یک تنظیم خاص
        category: دسته تنظیم (مثلاً 'DISPLAY', 'API')
        key: کلید تنظیم
        default: مقدار پیش‌فرض در صورت عدم وجود تنظیم
        """
        try:
            return self.settings[category][key]
        except KeyError:
            return default
    
    def set_setting(self, category, key, value):
        """
        تنظیم یک مقدار جدید
        category: دسته تنظیم
        key: کلید تنظیم
        value: مقدار جدید
        """
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
    
    def reset_settings(self):
        """
        بازنشانی تمام تنظیمات به مقادیر پیش‌فرض
        """
        self.settings = DEFAULT_SETTINGS.copy()
        self.save_settings()
    
    def _merge_settings(self, default, loaded):
        """
        ادغام تنظیمات بارگذاری شده با تنظیمات پیش‌فرض
        default: تنظیمات پیش‌فرض
        loaded: تنظیمات بارگذاری شده
        return: تنظیمات ادغام شده
        """
        merged = default.copy()
        
        for category in loaded:
            if category in merged:
                for key, value in loaded[category].items():
                    if key in merged[category]:
                        merged[category][key] = value
        
        return merged
    
    def validate_settings(self):
        """
        اعتبارسنجی تنظیمات فعلی
        بررسی وجود تمام تنظیمات ضروری و صحت مقادیر آنها
        return: (bool, str) نتیجه اعتبارسنجی و پیام خطا
        """
        try:
            # بررسی وجود تمام دسته‌های ضروری
            required_categories = ['DISPLAY', 'FILTER', 'API']
            for category in required_categories:
                if category not in self.settings:
                    return False, f"دسته تنظیمات {category} یافت نشد"
            
            # بررسی مقادیر عددی
            if not isinstance(self.settings['DISPLAY']['font_size'], int):
                return False, "اندازه فونت باید عدد صحیح باشد"
            
            if not isinstance(self.settings['DISPLAY']['update_interval'], (int, float)):
                return False, "فاصله به‌روزرسانی باید عدد باشد"
            
            # بررسی محدوده مقادیر
            if self.settings['FILTER']['min_change'] < -100 or self.settings['FILTER']['max_change'] > 100:
                return False, "محدوده تغییرات باید بین -100 تا 100 باشد"
            
            return True, "تنظیمات معتبر هستند"
            
        except Exception as e:
            return False, f"خطا در اعتبارسنجی تنظیمات: {str(e)}" 