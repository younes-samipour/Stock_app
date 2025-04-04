"""
ماژول تقویم بازار
قابلیت‌های اصلی:
- مدیریت روزهای معاملاتی
- تشخیص تعطیلات بازار
- محاسبه روزهای کاری
- مدیریت ساعات معاملاتی
"""

from datetime import datetime, time, timedelta
from typing import Dict, List, Optional
import pandas as pd
from .exceptions import ValidationError

class MarketCalendar:
    def __init__(self):
        """
        سازنده کلاس MarketCalendar
        تنظیم پارامترهای پایه تقویم بازار
        """
        self.market_start = time(9, 0)  # ساعت شروع بازار
        self.market_end = time(15, 30)  # ساعت پایان بازار
        self.holidays = set()  # مجموعه تعطیلات
        self.special_days = {}  # روزهای خاص با ساعت متفاوت
        
    def add_holiday(self, date: datetime):
        """
        اضافه کردن روز تعطیل به تقویم
        date: تاریخ تعطیلی
        """
        self.holidays.add(date.date())
        
    def add_special_day(self, date: datetime, start_time: time, end_time: time):
        """
        اضافه کردن روز خاص با ساعت کاری متفاوت
        date: تاریخ روز خاص
        start_time: ساعت شروع
        end_time: ساعت پایان
        """
        self.special_days[date.date()] = {
            'start': start_time,
            'end': end_time
        }
    
    def is_trading_day(self, date=None):
        """
        بررسی روز معاملاتی
        date: تاریخ مورد نظر (پیش‌فرض: امروز)
        return: True اگر روز معاملاتی باشد
        """
        if date is None:
            date = datetime.now()
            
        # بررسی تعطیلات آخر هفته
        if date.weekday() in [3, 4]:  # 3=پنجشنبه، 4=جمعه
            return False
            
        # بررسی تعطیلات رسمی
        if date.date() in self.holidays:
            return False
            
        return True
    
    def is_trading_hours(self, time=None):
        """
        بررسی ساعت معاملاتی
        time: زمان مورد نظر (پیش‌فرض: اکنون)
        return: True اگر در ساعت معاملاتی باشد
        """
        if time is None:
            time = datetime.now().time()
            
        return self.market_start <= time <= self.market_end
    
    def get_next_trading_day(self, date=None):
        """
        یافتن روز معاملاتی بعدی
        date: تاریخ مبدا (پیش‌فرض: امروز)
        return: تاریخ روز معاملاتی بعدی
        """
        if date is None:
            date = datetime.now()
            
        next_day = date + timedelta(days=1)
        while not self.is_trading_day(next_day):
            next_day += timedelta(days=1)
            
        return next_day
    
    def get_previous_trading_day(self, date=None):
        """
        یافتن روز معاملاتی قبلی
        date: تاریخ مبدا (پیش‌فرض: امروز)
        return: تاریخ روز معاملاتی قبلی
        """
        if date is None:
            date = datetime.now()
            
        prev_day = date - timedelta(days=1)
        while not self.is_trading_day(prev_day):
            prev_day -= timedelta(days=1)
            
        return prev_day
    
    def get_trading_days_between(self, start_date, end_date):
        """
        یافتن روزهای معاملاتی بین دو تاریخ
        start_date: تاریخ شروع
        end_date: تاریخ پایان
        return: لیست روزهای معاملاتی
        """
        trading_days = []
        current_date = start_date
        
        while current_date <= end_date:
            if self.is_trading_day(current_date):
                trading_days.append(current_date)
            current_date += timedelta(days=1)
            
        return trading_days
    
    def get_market_status(self):
        """
        دریافت وضعیت فعلی بازار
        return: دیکشنری وضعیت بازار
        """
        now = datetime.now()
        
        if not self.is_trading_day(now):
            return {
                'status': 'closed',
                'reason': 'non_trading_day',
                'next_open': self.get_next_trading_day()
            }
            
        if now.time() < self.market_start or now.time() > self.market_end:
            return {
                'status': 'closed',
                'reason': 'outside_trading_hours',
                'next_open': self.market_start
            }
            
        return {
            'status': 'open',
            'period': 'regular',
            'closing_time': self.market_end
        }

    def get_trading_sessions(self, date=None):
        """
        دریافت جلسات معاملاتی روز
        date: تاریخ مورد نظر (پیش‌فرض: امروز)
        return: دیکشنری جلسات معاملاتی
        """
        if date is None:
            date = datetime.now()
        
        if not self.is_trading_day(date):
            return None
        
        # بررسی روز خاص
        if date.date() in self.special_days:
            special_hours = self.special_days[date.date()]
            return {
                'pre_market': {
                    'start': None,
                    'end': None
                },
                'regular': {
                    'start': special_hours['start'],
                    'end': special_hours['end']
                },
                'post_market': {
                    'start': None,
                    'end': None
                }
            }
        
        # ساعات معمول
        return {
            'pre_market': {
                'start': None,
                'end': None
            },
            'regular': {
                'start': self.market_start,
                'end': self.market_end
            },
            'post_market': {
                'start': None,
                'end': None
            }
        }

    def get_trading_minutes(self, date=None):
        """
        محاسبه دقایق معاملاتی روز
        date: تاریخ مورد نظر (پیش‌فرض: امروز)
        return: تعداد دقایق معاملاتی
        """
        sessions = self.get_trading_sessions(date)
        if not sessions:
            return 0
        
        regular_session = sessions['regular']
        start = datetime.combine(date.date(), regular_session['start'])
        end = datetime.combine(date.date(), regular_session['end'])
        
        return int((end - start).total_seconds() / 60)

    def is_valid_trading_datetime(self, dt: datetime):
        """
        اعتبارسنجی تاریخ و زمان معاملاتی
        dt: تاریخ و زمان مورد بررسی
        return: True اگر زمان معاملاتی معتبر باشد
        """
        return (
            self.is_trading_day(dt) and
            self.is_trading_hours(dt.time())
        ) 