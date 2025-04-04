"""
این ماژول مدیریت زمانبندی و اجرای خودکار وظایف را بر عهده دارد.
این ماژول امکانات زیر را فراهم می‌کند:
- زمانبندی به‌روزرسانی خودکار داده‌ها
- اجرای دوره‌ای وظایف مختلف
- مدیریت زمان‌های کاری بازار
- کنترل تواتر درخواست‌ها
"""

import threading
import time
from datetime import datetime, timedelta
from queue import Queue
import schedule
from .exceptions import ValidationError

class Scheduler:
    def __init__(self):
        """
        سازنده کلاس Scheduler
        راه‌اندازی زمانبندی با تنظیمات پایه
        """
        self.tasks = {}
        self.running = False
        self.task_queue = Queue()
        self.market_hours = {
            'start': '09:00',
            'end': '15:30'
        }
    
    def add_task(self, name, func, interval, args=None):
        """
        افزودن وظیفه جدید به زمانبند
        name: نام وظیفه
        func: تابع مورد نظر
        interval: فاصله زمانی اجرا (ثانیه)
        args: پارامترهای تابع
        """
        if name in self.tasks:
            raise ValidationError(f"وظیفه {name} قبلاً تعریف شده است")
            
        self.tasks[name] = {
            'function': func,
            'interval': interval,
            'args': args or [],
            'last_run': None,
            'next_run': None,
            'active': True
        }
        
        # تنظیم زمان اجرای بعدی
        self._schedule_next_run(name)
    
    def remove_task(self, name):
        """
        حذف یک وظیفه از زمانبند
        name: نام وظیفه
        """
        if name in self.tasks:
            del self.tasks[name]
    
    def start(self):
        """
        شروع زمانبند و اجرای وظایف
        """
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def stop(self):
        """
        توقف زمانبند
        """
        self.running = False
        if hasattr(self, 'scheduler_thread'):
            self.scheduler_thread.join()
    
    def _run_scheduler(self):
        """
        اجرای اصلی زمانبند
        بررسی و اجرای وظایف در زمان مقرر
        """
        while self.running:
            current_time = datetime.now()
            
            # بررسی زمان کاری بازار
            if not self._is_market_hours():
                time.sleep(60)  # بررسی هر دقیقه
                continue
            
            # بررسی وظایف
            for name, task in self.tasks.items():
                if not task['active']:
                    continue
                    
                if task['next_run'] and current_time >= task['next_run']:
                    self._execute_task(name, task)
                    self._schedule_next_run(name)
            
            time.sleep(1)  # بررسی هر ثانیه
    
    def _execute_task(self, name, task):
        """
        اجرای یک وظیفه
        name: نام وظیفه
        task: اطلاعات وظیفه
        """
        try:
            task['function'](*task['args'])
            task['last_run'] = datetime.now()
        except Exception as e:
            print(f"Error executing task {name}: {str(e)}")
    
    def _schedule_next_run(self, name):
        """
        تنظیم زمان اجرای بعدی وظیفه
        name: نام وظیفه
        """
        task = self.tasks[name]
        current_time = datetime.now()
        
        if task['last_run'] is None:
            next_run = current_time
        else:
            next_run = task['last_run'] + timedelta(seconds=task['interval'])
            
            # اگر زمان بعدی در گذشته است، تنظیم به زمان فعلی
            if next_run < current_time:
                next_run = current_time
        
        task['next_run'] = next_run
    
    def _is_market_hours(self):
        """
        بررسی ساعت کاری بازار
        return: True اگر بازار باز است
        """
        current_time = datetime.now().strftime('%H:%M')
        return self.market_hours['start'] <= current_time <= self.market_hours['end']
    
    def set_market_hours(self, start, end):
        """
        تنظیم ساعت کاری بازار
        start: زمان شروع (HH:MM)
        end: زمان پایان (HH:MM)
        """
        # اعتبارسنجی فرمت زمان
        try:
            datetime.strptime(start, '%H:%M')
            datetime.strptime(end, '%H:%M')
        except ValueError:
            raise ValidationError("فرمت زمان نامعتبر است")
        
        self.market_hours['start'] = start
        self.market_hours['end'] = end
    
    def get_task_status(self, name):
        """
        دریافت وضعیت یک وظیفه
        name: نام وظیفه
        return: دیکشنری وضعیت وظیفه
        """
        if name not in self.tasks:
            raise ValidationError(f"وظیفه {name} یافت نشد")
            
        task = self.tasks[name]
        return {
            'name': name,
            'active': task['active'],
            'last_run': task['last_run'],
            'next_run': task['next_run'],
            'interval': task['interval']
        } 