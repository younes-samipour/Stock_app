"""
این ماژول کلاس FilterControls را برای مدیریت فیلترهای جدول سهام تعریف می‌کند.
این کلاس امکانات زیر را فراهم می‌کند:
- انتخاب ستون برای فیلتر کردن
- تعیین محدوده مقادیر (حداقل و حداکثر)
- اعمال فیلتر و پاک کردن آن
"""

import tkinter as tk
from tkinter import ttk

class FilterControls(ttk.Frame):
    def __init__(self, parent, columns, column_names):
        """
        سازنده کلاس FilterControls
        parent: فریم والد که کنترل‌های فیلتر در آن قرار می‌گیرند
        columns: لیست نام‌های ستون‌ها
        column_names: لیست عناوین نمایشی ستون‌ها
        """
        super().__init__(parent)
        
        # ذخیره اطلاعات ستون‌ها
        self.columns = columns
        self.column_names = column_names
        
        # ایجاد کنترل‌های فیلتر
        self.setup_controls()
    
    def setup_controls(self):
        """راه‌اندازی کنترل‌های فیلتر"""
        # فریم انتخاب ستون
        column_frame = ttk.Frame(self)
        column_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(column_frame, text="ستون:").pack(side=tk.LEFT)
        
        # کامبوباکس انتخاب ستون
        self.column_var = tk.StringVar()
        self.column_combo = ttk.Combobox(
            column_frame,
            textvariable=self.column_var,
            values=self.column_names,
            state='readonly',
            width=15
        )
        self.column_combo.pack(side=tk.LEFT, padx=5)
        self.column_combo.set(self.column_names[0])
        
        # فریم مقادیر حداقل و حداکثر
        value_frame = ttk.Frame(self)
        value_frame.pack(side=tk.LEFT, padx=5)
        
        # ورودی حداقل مقدار
        ttk.Label(value_frame, text="از:").pack(side=tk.LEFT)
        self.min_value = ttk.Entry(value_frame, width=10)
        self.min_value.pack(side=tk.LEFT, padx=5)
        
        # ورودی حداکثر مقدار
        ttk.Label(value_frame, text="تا:").pack(side=tk.LEFT)
        self.max_value = ttk.Entry(value_frame, width=10)
        self.max_value.pack(side=tk.LEFT, padx=5)
        
        # فریم دکمه‌ها
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.LEFT, padx=5)
        
        # دکمه اعمال فیلتر
        self.apply_btn = ttk.Button(
            button_frame,
            text="اعمال فیلتر",
            style='Filter.TButton'
        )
        self.apply_btn.pack(side=tk.LEFT, padx=5)
        
        # دکمه پاک کردن فیلتر
        self.reset_btn = ttk.Button(
            button_frame,
            text="پاک کردن",
            style='Filter.TButton'
        )
        self.reset_btn.pack(side=tk.LEFT)
    
    def get_filter_values(self):
        """
        دریافت مقادیر فیلتر
        return: دیکشنری شامل ستون انتخاب شده و مقادیر حداقل و حداکثر
        """
        return {
            'column': self.column_var.get(),
            'min_value': self.min_value.get(),
            'max_value': self.max_value.get()
        }
    
    def reset_filters(self):
        """پاک کردن تمام فیلترها"""
        self.column_combo.set(self.column_names[0])
        self.min_value.delete(0, tk.END)
        self.max_value.delete(0, tk.END) 