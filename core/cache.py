"""
این ماژول مدیریت کش برنامه را بر عهده دارد.
این ماژول امکانات زیر را فراهم می‌کند:
- ذخیره موقت داده‌های پرکاربرد
- مدیریت زمان انقضای داده‌ها
- پاکسازی خودکار کش
- بهینه‌سازی عملکرد برنامه
"""

import os
import json
import time
from datetime import datetime, timedelta
from .constants import FILE_PATHS
from .exceptions import FileError

class Cache:
    def __init__(self):
        """
        سازنده کلاس Cache
        راه‌اندازی سیستم کش با تنظیمات پایه
        """
        self.cache_dir = FILE_PATHS['cache']
        self.cache = {}
        self.expiry_times = {}
        
        # ایجاد دایرکتوری کش اگر وجود نداشته باشد
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # بارگذاری کش موجود
        self.load_cache()
    
    def load_cache(self):
        """
        بارگذاری داده‌های کش از فایل
        حذف داده‌های منقضی شده
        """
        try:
            cache_file = os.path.join(self.cache_dir, 'cache.json')
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache = data.get('data', {})
                    self.expiry_times = data.get('expiry', {})
                    
                # حذف داده‌های منقضی شده
                self.cleanup_expired()
                
        except Exception as e:
            raise FileError(f"خطا در بارگذاری کش: {str(e)}", 'cache.json')
    
    def save_cache(self):
        """
        ذخیره داده‌های کش در فایل
        """
        try:
            cache_file = os.path.join(self.cache_dir, 'cache.json')
            data = {
                'data': self.cache,
                'expiry': self.expiry_times
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
        except Exception as e:
            raise FileError(f"خطا در ذخیره کش: {str(e)}", 'cache.json')
    
    def set(self, key, value, expire_minutes=60):
        """
        ذخیره یک داده در کش
        key: کلید داده
        value: مقدار داده
        expire_minutes: زمان انقضا به دقیقه
        """
        self.cache[key] = value
        self.expiry_times[key] = (
            datetime.now() + timedelta(minutes=expire_minutes)
        ).timestamp()
        self.save_cache()
    
    def get(self, key, default=None):
        """
        دریافت یک داده از کش
        key: کلید داده
        default: مقدار پیش‌فرض در صورت عدم وجود داده
        return: مقدار داده یا مقدار پیش‌فرض
        """
        if key in self.cache and not self.is_expired(key):
            return self.cache[key]
        return default
    
    def delete(self, key):
        """
        حذف یک داده از کش
        key: کلید داده
        """
        if key in self.cache:
            del self.cache[key]
            del self.expiry_times[key]
            self.save_cache()
    
    def clear(self):
        """
        پاک کردن تمام داده‌های کش
        """
        self.cache.clear()
        self.expiry_times.clear()
        self.save_cache()
    
    def is_expired(self, key):
        """
        بررسی انقضای یک داده
        key: کلید داده
        return: True اگر منقضی شده باشد
        """
        if key in self.expiry_times:
            return datetime.now().timestamp() > self.expiry_times[key]
        return True
    
    def cleanup_expired(self):
        """
        پاکسازی داده‌های منقضی شده
        """
        expired_keys = [
            key for key in self.cache.keys()
            if self.is_expired(key)
        ]
        
        for key in expired_keys:
            self.delete(key)
    
    def get_cache_size(self):
        """
        محاسبه حجم کش
        return: حجم کش به بایت
        """
        try:
            cache_file = os.path.join(self.cache_dir, 'cache.json')
            return os.path.getsize(cache_file)
        except:
            return 0
    
    def get_cache_stats(self):
        """
        دریافت آمار کش
        return: دیکشنری شامل آمار کش
        """
        return {
            'total_items': len(self.cache),
            'expired_items': len([k for k in self.cache if self.is_expired(k)]),
            'cache_size': self.get_cache_size(),
            'last_cleanup': getattr(self, 'last_cleanup', None)
        } 