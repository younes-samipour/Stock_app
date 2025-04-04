"""
این ماژول مسئول تعریف و مدیریت خطاهای سفارشی برنامه است.
قابلیت‌های اصلی این ماژول عبارتند از:
- تعریف کلاس‌های خطای سفارشی
- مدیریت خطاهای API
- مدیریت خطاهای پایگاه داده
- مدیریت خطاهای اعتبارسنجی
"""

class StockAppError(Exception):
    """
    کلاس پایه برای تمام خطاهای برنامه
    این کلاس از Exception ارث‌بری می‌کند
    """
    def __init__(self, message="خطای نامشخص در برنامه"):
        self.message = message
        super().__init__(self.message)

class APIError(StockAppError):
    """
    خطاهای مربوط به API
    برای مدیریت خطاهای ارتباط با سرور و درخواست‌ها
    """
    def __init__(self, message="خطا در ارتباط با API"):
        super().__init__(message)

class DatabaseError(StockAppError):
    """
    خطاهای مربوط به پایگاه داده
    برای مدیریت خطاهای ذخیره و بازیابی اطلاعات
    """
    def __init__(self, message="خطا در عملیات پایگاه داده"):
        super().__init__(message)

class ValidationError(StockAppError):
    """
    خطاهای مربوط به اعتبارسنجی
    برای مدیریت خطاهای ورودی نامعتبر
    """
    def __init__(self, message="خطا در اعتبارسنجی داده‌ها"):
        super().__init__(message)

class ConfigError(StockAppError):
    """
    خطاهای مربوط به تنظیمات
    برای مدیریت خطاهای پیکربندی برنامه
    """
    def __init__(self, message="خطا در تنظیمات برنامه"):
        super().__init__(message)

class FileError(StockAppError):
    """
    خطاهای مربوط به فایل‌ها
    برای مدیریت خطاهای خواندن و نوشتن فایل‌ها
    """
    def __init__(self, message="خطا در عملیات فایل"):
        super().__init__(message)

class ChartError(StockAppError):
    """
    خطاهای مربوط به نمودارها
    برای مدیریت خطاهای رسم و ذخیره نمودارها
    """
    def __init__(self, message="خطا در عملیات نمودار"):
        super().__init__(message)

class NetworkError(StockAppError):
    """
    خطاهای مربوط به شبکه
    برای مدیریت خطاهای اتصال به اینترنت
    """
    def __init__(self, message="خطا در اتصال به شبکه"):
        super().__init__(message)

def handle_error(error, logger=None):
    """
    تابع مدیریت خطاها
    error: شیء خطا
    logger: شیء لاگر (اختیاری)
    return: پیام خطای مناسب برای نمایش به کاربر
    """
    # ثبت خطا در لاگ اگر logger موجود باشد
    if logger:
        logger.error(f"خطا: {str(error)}")
        
    # برگرداندن پیام مناسب بر اساس نوع خطا
    if isinstance(error, APIError):
        return "خطا در ارتباط با سرور. لطفاً دوباره تلاش کنید."
    elif isinstance(error, DatabaseError):
        return "خطا در عملیات پایگاه داده. لطفاً با پشتیبانی تماس بگیرید."
    elif isinstance(error, ValidationError):
        return f"خطای اعتبارسنجی: {str(error)}"
    elif isinstance(error, NetworkError):
        return "خطا در اتصال به اینترنت. لطفاً اتصال خود را بررسی کنید."
    else:
        return "خطای غیرمنتظره در برنامه. لطفاً دوباره تلاش کنید." 