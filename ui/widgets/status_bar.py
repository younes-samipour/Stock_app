"""
این ماژول کلاس StatusBar را برای نمایش نوار وضعیت برنامه تعریف می‌کند.
این کلاس امکانات زیر را فراهم می‌کند:
- نمایش پیام‌های وضعیت برنامه
- نمایش نوار پیشرفت برای عملیات‌های زمان‌بر
- قابلیت به‌روزرسانی پویای وضعیت و پیشرفت
"""

import tkinter as tk
from tkinter import ttk

class StatusBar(ttk.Frame):
    def __init__(self, parent):
        """
        سازنده کلاس StatusBar
        parent: فریم والد که نوار وضعیت در آن قرار می‌گیرد
        """
        super().__init__(parent)
        
        # متغیر نگهداری پیام وضعیت
        self.status_var = tk.StringVar()
        self.status_var.set("آماده به کار")
        
        # ایجاد لیبل نمایش وضعیت
        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            relief=tk.SUNKEN,  # ایجاد حاشیه فرورفته
            anchor=tk.W,       # چپ چین کردن متن
            padding=5
        )
        self.status_label.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # ایجاد نوار پیشرفت
        self.progress = ttk.Progressbar(
            self,
            orient=tk.HORIZONTAL,
            mode='determinate',  # حالت پیشرفت قطعی (0 تا 100)
            length=200
        )
        self.progress.pack(fill=tk.X, side=tk.RIGHT)
    
    def set_status(self, message):
        """
        تنظیم پیام وضعیت جدید
        message: پیام وضعیت
        """
        self.status_var.set(message)
    
    def update_progress(self, value):
        """
        به‌روزرسانی مقدار نوار پیشرفت
        value: مقدار جدید (0 تا 100)
        """
        self.progress['value'] = value