"""
این ماژول شامل توابع کمکی و ابزارهای مورد نیاز برنامه است.
قابلیت‌های اصلی این ماژول عبارتند از:
- تبدیل تاریخ و زمان
- فرمت‌دهی اعداد و ارقام
- محاسبات مالی
- توابع کمکی رابط کاربری
"""

import jdatetime
from datetime import datetime, timedelta
import locale
import re
from typing import Union, Dict, List
import json
import logging

def setup_logging():
    """
    راه‌اندازی سیستم ثبت رویدادها
    تنظیم فرمت و مسیر ذخیره لاگ‌ها
    """
    logging.basicConfig(
        filename='data/app.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def format_price(price: float) -> str:
    """
    فرمت‌دهی قیمت با جداکننده هزارگان
    price: قیمت به صورت عدد اعشاری
    return: رشته فرمت شده قیمت
    """
    try:
        return f"{price:,.0f}"
    except (ValueError, TypeError):
        return "0"

def format_volume(volume: int) -> str:
    """
    فرمت‌دهی حجم معاملات
    volume: حجم به صورت عدد صحیح
    return: رشته فرمت شده حجم (مثلا: 1.2M برای 1,200,000)
    """
    try:
        if volume >= 1_000_000:
            return f"{volume/1_000_000:.1f}M"
        elif volume >= 1_000:
            return f"{volume/1_000:.1f}K"
        return str(volume)
    except (ValueError, TypeError):
        return "0"

def jalali_to_gregorian(jdate: str) -> datetime:
    """
    تبدیل تاریخ شمسی به میلادی
    jdate: تاریخ شمسی به فرمت YYYY/MM/DD
    return: شیء datetime
    """
    try:
        jy, jm, jd = map(int, jdate.split('/'))
        return jdatetime.date(jy, jm, jd).togregorian()
    except ValueError:
        return None

def gregorian_to_jalali(date: datetime) -> str:
    """
    تبدیل تاریخ میلادی به شمسی
    date: شیء datetime
    return: تاریخ شمسی به فرمت YYYY/MM/DD
    """
    try:
        j_date = jdatetime.date.fromgregorian(date=date)
        return j_date.strftime("%Y/%m/%d")
    except ValueError:
        return None

def calculate_change_percent(current: float, previous: float) -> float:
    """
    محاسبه درصد تغییر
    current: مقدار فعلی
    previous: مقدار قبلی
    return: درصد تغییر
    """
    try:
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100
    except (ValueError, TypeError):
        return 0

def validate_symbol(symbol: str) -> bool:
    """
    اعتبارسنجی نماد سهم
    symbol: نماد مورد بررسی
    return: True اگر نماد معتبر باشد
    """
    # الگوی نماد: حروف فارسی یا انگلیسی + اعداد (اختیاری)
    pattern = r'^[\u0600-\u06FF\w]{2,}[0-9]*$'
    return bool(re.match(pattern, symbol))

def get_color_for_change(change: float) -> str:
    """
    تعیین رنگ برای نمایش تغییرات
    change: درصد تغییر
    return: کد رنگ مناسب
    """
    if change > 0:
        return '#1e8e3e'  # سبز
    elif change < 0:
        return '#d93025'  # قرمز
    return '#202124'  # خنثی

def format_datetime(dt: datetime, include_time: bool = True) -> str:
    """
    فرمت‌دهی تاریخ و زمان
    dt: شیء datetime
    include_time: شامل کردن زمان
    return: رشته فرمت شده تاریخ و زمان
    """
    try:
        j_date = jdatetime.date.fromgregorian(date=dt)
        if include_time:
            return f"{j_date.strftime('%Y/%m/%d')} {dt.strftime('%H:%M:%S')}"
        return j_date.strftime("%Y/%m/%d")
    except ValueError:
        return ""

def format_number(number, decimal_places=0):
    """
    فرمت‌بندی اعداد با جداکننده هزارگان
    number: عدد ورودی
    decimal_places: تعداد رقم اعشار
    return: رشته فرمت شده
    """
    try:
        if decimal_places == 0:
            return f"{int(number):,}"
        else:
            return f"{float(number):,.{decimal_places}f}"
    except (ValueError, TypeError):
        return str(number)

def format_percent(number):
    """
    فرمت‌بندی اعداد به صورت درصد
    number: عدد ورودی
    return: رشته فرمت شده با علامت درصد
    """
    try:
        return f"{float(number):.2f}%"
    except (ValueError, TypeError):
        return "0.00%"

def validate_stock_code(code):
    """
    اعتبارسنجی کد معاملاتی سهم
    code: کد معاملاتی
    return: True اگر معتبر باشد، False در غیر این صورت
    """
    if not code:
        return False
    
    # بررسی فرمت کد معاملاتی (باید با 1 یا 2 شروع شود و 12 رقم باشد)
    pattern = r'^[12]\d{11}$'
    return bool(re.match(pattern, str(code)))

def calculate_moving_average(data, period):
    """
    محاسبه میانگین متحرک
    data: لیست داده‌ها
    period: دوره میانگین‌گیری
    return: لیست میانگین‌های متحرک
    """
    if not data or period <= 0:
        return []
    
    results = []
    for i in range(len(data)):
        if i < period - 1:
            results.append(None)
        else:
            window = data[i-period+1:i+1]
            average = sum(window) / period
            results.append(average)
    
    return results

def save_to_json(data, filename):
    """
    ذخیره داده‌ها در فایل JSON
    data: داده‌های مورد نظر
    filename: نام فایل
    return: True در صورت موفقیت، False در صورت خطا
    """
    try:
        with open(f'data/{filename}', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file: {str(e)}")
        return False

def load_from_json(filename):
    """
    بارگذاری داده‌ها از فایل JSON
    filename: نام فایل
    return: داده‌های بارگذاری شده یا None در صورت خطا
    """
    try:
        with open(f'data/{filename}', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON file: {str(e)}")
        return None

def calculate_rsi(data: List[float], period: int = 14) -> List[float]:
    """
    محاسبه شاخص قدرت نسبی (RSI)
    data: لیست قیمت‌های پایانی
    period: دوره محاسبه (پیش‌فرض: 14)
    return: لیست مقادیر RSI
    """
    if len(data) < period:
        return []
        
    changes = [data[i] - data[i-1] for i in range(1, len(data))]
    gains = [max(0, change) for change in changes]
    losses = [max(0, -change) for change in changes]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    rsi_values = []
    for i in range(len(data)):
        if i < period:
            rsi_values.append(None)
            continue
            
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
        rsi_values.append(rsi)
        
        if i < len(data) - 1:
            avg_gain = (avg_gain * (period-1) + gains[i]) / period
            avg_loss = (avg_loss * (period-1) + losses[i]) / period
            
    return rsi_values

def encrypt_data(data: str, key: str) -> str:
    """
    رمزنگاری داده‌های حساس
    data: داده‌های ورودی
    key: کلید رمزنگاری
    return: داده‌های رمزنگاری شده
    """
    try:
        from cryptography.fernet import Fernet
        f = Fernet(key.encode())
        return f.encrypt(data.encode()).decode()
    except Exception as e:
        logging.error(f"Encryption error: {str(e)}")
        return None

def decrypt_data(encrypted_data: str, key: str) -> str:
    """
    رمزگشایی داده‌های رمزنگاری شده
    encrypted_data: داده‌های رمزنگاری شده
    key: کلید رمزنگاری
    return: داده‌های اصلی
    """
    try:
        from cryptography.fernet import Fernet
        f = Fernet(key.encode())
        return f.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        logging.error(f"Decryption error: {str(e)}")
        return None

def validate_api_key(api_key: str) -> bool:
    """
    اعتبارسنجی کلید API
    api_key: کلید API مورد بررسی
    return: True اگر معتبر باشد
    """
    if not api_key:
        return False
    
    # بررسی طول و فرمت کلید
    pattern = r'^[A-Za-z0-9_-]{32,}$'
    return bool(re.match(pattern, api_key))

def sanitize_input(text: str) -> str:
    """
    پاکسازی ورودی‌های کاربر
    text: متن ورودی
    return: متن پاکسازی شده
    """
    # حذف کاراکترهای خطرناک
    text = re.sub(r'[<>\'\"&]', '', text)
    # حذف فضاهای اضافی
    text = ' '.join(text.split())
    return text

def create_backup(filename: str) -> bool:
    """
    ایجاد نسخه پشتیبان از فایل
    filename: نام فایل
    return: True در صورت موفقیت
    """
    from shutil import copy2
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{filename}_{timestamp}.bak"
        copy2(f"data/{filename}", f"data/backup/{backup_name}")
        return True
    except Exception as e:
        logging.error(f"Backup error: {str(e)}")
        return False
