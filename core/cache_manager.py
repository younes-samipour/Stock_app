"""
این ماژول مسئول مدیریت کش برنامه است.
قابلیت‌های اصلی این ماژول عبارتند از:
- ذخیره موقت داده‌های پرکاربرد
- مدیریت زمان انقضای کش
- پاکسازی خودکار کش
- بهینه‌سازی عملکرد برنامه
"""

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from .exceptions import CacheError
from .config import FILE_PATHS

class CacheManager:
    def __init__(self, cache_dir=FILE_PATHS['cache']):
        """
        سازنده کلاس CacheManager
        cache_dir: مسیر پوشه کش
        """
        self.cache_dir = cache_dir
        self.cache = {}
        self.load_cache()
        
    def load_cache(self):
        """
        بارگذاری داده‌های کش از فایل
        در صورت خطا، کش خالی ایجاد می‌شود
        """
        try:
            cache_file = self.cache_dir / 'cache.json'
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                    
            # حذف داده‌های منقضی شده
            self._cleanup_expired()
            
        except Exception as e:
            self.cache = {}
            logging.error(f"خطا در بارگذاری کش: {str(e)}")
            
    def save_cache(self):
        """
        ذخیره داده‌های کش در فایل
        """
        try:
            cache_file = self.cache_dir / 'cache.json'
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"خطا در ذخیره کش: {str(e)}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        دریافت داده از کش
        key: کلید داده
        default: مقدار پیش‌فرض در صورت عدم وجود
        return: داده کش شده یا مقدار پیش‌فرض
        """
        if key not in self.cache:
            return default
            
        item = self.cache[key]
        if self._is_expired(item):
            del self.cache[key]
            return default
            
        return item['data']
        
    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        ذخیره داده در کش
        key: کلید داده
        value: مقدار داده
        ttl: زمان انقضا به ثانیه (پیش‌فرض: 1 ساعت)
        """
        self.cache[key] = {
            'data': value,
            'expires_at': time.time() + ttl
        }
        self.save_cache()
        
    def delete(self, key: str):
        """
        حذف داده از کش
        key: کلید داده
        """
        if key in self.cache:
            del self.cache[key]
            self.save_cache()
            
    def clear(self):
        """
        پاک کردن کل کش
        """
        self.cache = {}
        self.save_cache()
        
    def _is_expired(self, item: Dict) -> bool:
        """
        بررسی انقضای یک آیتم کش
        item: آیتم کش
        return: True اگر منقضی شده باشد
        """
        return time.time() > item['expires_at']
        
    def _cleanup_expired(self):
        """
        پاکسازی داده‌های منقضی شده از کش
        """
        expired_keys = [
            key for key, item in self.cache.items()
            if self._is_expired(item)
        ]
        for key in expired_keys:
            del self.cache[key] 

    def get_many(self, keys: list) -> Dict:
        """
        دریافت چندین داده از کش به صورت همزمان
        keys: لیست کلیدهای مورد نظر
        return: دیکشنری داده‌های یافت شده
        """
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def set_many(self, items: Dict, ttl: int = 3600):
        """
        ذخیره چندین داده در کش به صورت همزمان
        items: دیکشنری داده‌ها (کلید: مقدار)
        ttl: زمان انقضا به ثانیه
        """
        for key, value in items.items():
            self.set(key, value, ttl)

    def get_stats(self) -> Dict:
        """
        دریافت آمار کش
        return: دیکشنری شامل آمار کش
        """
        total_items = len(self.cache)
        expired_items = len([
            item for item in self.cache.values()
            if self._is_expired(item)
        ])
        
        return {
            'total_items': total_items,
            'active_items': total_items - expired_items,
            'expired_items': expired_items,
            'cache_size': len(json.dumps(self.cache).encode('utf-8'))
        }

    def optimize(self):
        """
        بهینه‌سازی کش
        - حذف داده‌های منقضی
        - فشرده‌سازی حافظه
        return: تعداد آیتم‌های حذف شده
        """
        initial_count = len(self.cache)
        self._cleanup_expired()
        final_count = len(self.cache)
        
        # ذخیره مجدد برای فشرده‌سازی
        self.save_cache()
        return initial_count - final_count

    def create_backup(self):
        """
        ایجاد نسخه پشتیبان از کش
        return: مسیر فایل پشتیبان یا None در صورت خطا
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.cache_dir / f'cache_backup_{timestamp}.json'
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=4)
            
            return str(backup_file)
        except Exception as e:
            logging.error(f"خطا در ایجاد پشتیبان: {str(e)}")
            return None

    def restore_backup(self, backup_file: str) -> bool:
        """
        بازیابی کش از نسخه پشتیبان
        backup_file: مسیر فایل پشتیبان
        return: True در صورت موفقیت
        """
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
            self.save_cache()
            return True
        except Exception as e:
            logging.error(f"خطا در بازیابی پشتیبان: {str(e)}")
            return False 