"""
این ماژول تنظیمات برنامه را مدیریت می‌کند.
"""

import json
import os

class Config:
    """کلاس مدیریت تنظیمات برنامه"""
    
    def __init__(self):
        """سازنده کلاس Config"""
        self.config_file = "config.json"
        self.default_config = {
            "api": {
                "base_url": "http://www.tsetmc.com/tsev2/data/TseClient2.aspx",
                "timeout": 30,
                "retry_count": 3
            },
            "database": {
                "path": "data/stock_app.db",
                "backup_path": "data/backup"
            },
            "ui": {
                "theme": "clam",
                "font_family": "Arial",
                "font_size": 10,
                "update_interval": 60
            },
            "logging": {
                "level": "INFO",
                "file": "logs/app.log",
                "max_size": 1048576,  # 1MB
                "backup_count": 5
            }
        }
        self.config = self.load_config()
        
    def load_config(self):
        """بارگذاری تنظیمات از فایل"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return self.default_config.copy()
            
    def save_config(self):
        """ذخیره تنظیمات در فایل"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            
    def get(self, section, key=None):
        """
        دریافت مقدار تنظیمات
        section: بخش تنظیمات
        key: کلید تنظیمات (اختیاری)
        """
        try:
            if key is None:
                return self.config.get(section, self.default_config.get(section))
            return self.config.get(section, {}).get(key, 
                self.default_config.get(section, {}).get(key))
        except Exception as e:
            print(f"Error getting config: {str(e)}")
            return None
            
    def set(self, section, key, value):
        """
        تنظیم مقدار تنظیمات
        section: بخش تنظیمات
        key: کلید تنظیمات
        value: مقدار تنظیمات
        """
        try:
            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = value
            self.save_config()
        except Exception as e:
            print(f"Error setting config: {str(e)}")
            
    def reset(self):
        """بازنشانی تنظیمات به حالت پیش‌فرض"""
        self.config = self.default_config.copy()
        self.save_config()