"""
این ماژول مسئول مدیریت و ثبت لاگ‌های برنامه است.
قابلیت‌های اصلی این ماژول عبارتند از:
- ثبت رویدادها و خطاها
- چرخش خودکار فایل‌های لاگ
- سطوح مختلف لاگ‌گیری
- فرمت‌دهی پیام‌های لاگ
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from .config import LOG_CONFIG, FILE_PATHS

class Logger:
    """
    کلاس مدیریت لاگ‌های برنامه
    این کلاس امکان ثبت رویدادها در سطوح مختلف را فراهم می‌کند
    """
    
    def __init__(self, name='stock_app'):
        """
        سازنده کلاس Logger
        name: نام لاگر (پیش‌فرض: stock_app)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_CONFIG['level']))
        
        # اطمینان از وجود پوشه لاگ
        os.makedirs(FILE_PATHS['logs'], exist_ok=True)
        
        # تنظیم handler فایل با قابلیت چرخش
        file_handler = RotatingFileHandler(
            LOG_CONFIG['path'],
            maxBytes=LOG_CONFIG['max_size'],
            backupCount=LOG_CONFIG['backup_count'],
            encoding='utf-8'
        )
        
        # تنظیم handler کنسول
        console_handler = logging.StreamHandler()
        
        # تنظیم فرمت لاگ‌ها
        formatter = logging.Formatter(LOG_CONFIG['format'])
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # اضافه کردن handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def info(self, message):
        """
        ثبت پیام اطلاع‌رسانی
        message: متن پیام
        """
        self.logger.info(message)
        
    def warning(self, message):
        """
        ثبت پیام هشدار
        message: متن پیام
        """
        self.logger.warning(message)
        
    def error(self, message):
        """
        ثبت پیام خطا
        message: متن پیام
        """
        self.logger.error(message)
        
    def critical(self, message):
        """
        ثبت پیام خطای بحرانی
        message: متن پیام
        """
        self.logger.critical(message)
        
    def debug(self, message):
        """
        ثبت پیام اشکال‌زدایی
        message: متن پیام
        """
        self.logger.debug(message)
        
    def log_api_request(self, endpoint, params=None, response=None, error=None):
        """
        ثبت درخواست‌های API
        endpoint: نقطه پایانی API
        params: پارامترهای درخواست (اختیاری)
        response: پاسخ دریافتی (اختیاری)
        error: خطای رخ داده (اختیاری)
        """
        message = f"API Request - Endpoint: {endpoint}"
        if params:
            message += f", Params: {params}"
        if response:
            message += f", Response: {response}"
        if error:
            message += f", Error: {error}"
            self.error(message)
        else:
            self.info(message)
            
    def log_db_operation(self, operation, table, data=None, error=None):
        """
        ثبت عملیات پایگاه داده
        operation: نوع عملیات
        table: نام جدول
        data: داده‌های عملیات (اختیاری)
        error: خطای رخ داده (اختیاری)
        """
        message = f"Database Operation - {operation} on {table}"
        if data:
            message += f", Data: {data}"
        if error:
            message += f", Error: {error}"
            self.error(message)
        else:
            self.info(message)

    def log_user_action(self, action, user=None, details=None):
        """
        ثبت اقدامات کاربر در برنامه
        action: نوع عمل انجام شده
        user: شناسه کاربر (اختیاری)
        details: جزئیات اضافی (اختیاری)
        """
        message = f"User Action - {action}"
        if user:
            message += f", User: {user}"
        if details:
            message += f", Details: {details}"
        self.info(message)

    def log_system_event(self, event_type, status, details=None):
        """
        ثبت رویدادهای سیستمی برنامه
        event_type: نوع رویداد
        status: وضعیت رویداد
        details: جزئیات اضافی (اختیاری)
        """
        message = f"System Event - Type: {event_type}, Status: {status}"
        if details:
            message += f", Details: {details}"
        self.info(message)

    def log_performance(self, operation, duration, success=True):
        """
        ثبت اطلاعات کارایی برنامه
        operation: نام عملیات
        duration: مدت زمان اجرا (به میلی‌ثانیه)
        success: موفقیت‌آمیز بودن عملیات
        """
        status = "Success" if success else "Failed"
        message = f"Performance - Operation: {operation}, Duration: {duration}ms, Status: {status}"
        self.debug(message)

    def log_market_data(self, symbol, data_type, data=None, error=None):
        """
        ثبت اطلاعات دریافتی از بازار
        symbol: نماد سهم
        data_type: نوع داده
        data: داده‌های دریافتی (اختیاری)
        error: خطای رخ داده (اختیاری)
        """
        message = f"Market Data - Symbol: {symbol}, Type: {data_type}"
        if data:
            message += f", Data: {data}"
        if error:
            message += f", Error: {error}"
            self.error(message)
        else:
            self.info(message)

    def log_export(self, export_type, file_path, status, error=None):
        """
        ثبت عملیات صدور فایل
        export_type: نوع صدور
        file_path: مسیر فایل
        status: وضعیت عملیات
        error: خطای رخ داده (اختیاری)
        """
        message = f"Export - Type: {export_type}, Path: {file_path}, Status: {status}"
        if error:
            message += f", Error: {error}"
            self.error(message)
        else:
            self.info(message)

    def cleanup_old_logs(self, days=30):
        """
        پاکسازی لاگ‌های قدیمی
        days: تعداد روزهای نگهداری لاگ
        """
        try:
            log_dir = FILE_PATHS['logs']
            current_time = datetime.now()
            
            for file in os.listdir(log_dir):
                file_path = os.path.join(log_dir, file)
                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (current_time - file_modified).days > days:
                    os.remove(file_path)
                    self.info(f"Removed old log file: {file}")
                
        except Exception as e:
            self.error(f"Error cleaning up old logs: {str(e)}") 