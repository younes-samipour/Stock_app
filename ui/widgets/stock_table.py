"""
این ماژول کلاس StockTable را برای نمایش جدول‌های سهام تعریف می‌کند.
این کلاس امکانات زیر را فراهم می‌کند:
- نمایش اطلاعات سهام در قالب جدول
- قابلیت مرتب‌سازی ستون‌ها
- اسکرول عمودی و افقی
- امکان انتخاب تک یا چند سهم
- تغییر رنگ ردیف‌ها برای نمایش وضعیت‌های مختلف
"""

import tkinter as tk
from tkinter import ttk

class StockTable(ttk.Treeview):
    def __init__(self, parent, columns, column_names, selectmode='browse', **kwargs):
        """
        سازنده کلاس StockTable
        parent: فریم والد که جدول در آن قرار می‌گیرد
        columns: لیست نام‌های ستون‌ها
        column_names: لیست عناوین نمایشی ستون‌ها
        selectmode: نوع انتخاب ('browse' یا 'extended')
        """
        # ایجاد فریم کانتینر برای جدول و اسکرول‌بارها
        self.container = ttk.Frame(parent)
        
        super().__init__(self.container, columns=columns, show='headings', 
                        selectmode=selectmode, **kwargs)
        
        # تنظیم ستون‌ها
        for col, col_name in zip(columns, column_names):
            self.heading(col, text=col_name, anchor='e')  # راست چین کردن عناوین
            self.column(col, width=100, anchor='e')       # راست چین کردن محتوا
        
        # ایجاد اسکرول‌بارها
        scroll_y = ttk.Scrollbar(self.container, orient=tk.VERTICAL, command=self.yview)
        scroll_x = ttk.Scrollbar(self.container, orient=tk.HORIZONTAL, command=self.xview)
        
        # اتصال اسکرول‌بارها به جدول
        self.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        # چیدمان اجزا در گرید
        self.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        # تنظیم وزن‌های گرید
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # اتصال رویداد دبل کلیک برای مرتب‌سازی
        self.bind('<Double-1>', self._handle_double_click)
        
        # متغیرهای مرتب‌سازی
        self._sort_column = None
        self._sort_reverse = False
    
    def insert_item(self, values, tags=None):
        """
        درج یک آیتم جدید در جدول
        values: مقادیر ستون‌ها
        tags: برچسب‌های مربوط به رنگ‌آمیزی ردیف
        """
        if tags:
            return self.insert('', tk.END, values=values, tags=(tags,))
        else:
            return self.insert('', tk.END, values=values)
    
    def clear(self):
        """پاک کردن تمام محتویات جدول"""
        self.delete(*self.get_children())
    
    def get_selected_items(self):
        """دریافت لیست آیتم‌های انتخاب شده"""
        return [self.item(item) for item in self.selection()]
    
    def get_all_items(self):
        """دریافت لیست تمام آیتم‌های جدول"""
        return [self.item(item) for item in self.get_children()]
    
    def change_item_color(self, item_id, color_tag):
        """
        تغییر رنگ یک ردیف خاص
        item_id: شناسه ردیف
        color_tag: برچسب رنگ
        """
        self.item(item_id, tags=(color_tag,))
    
    def _handle_double_click(self, event):
        """
        مدیریت رویداد دبل کلیک روی عنوان ستون‌ها
        برای مرتب‌سازی جدول بر اساس ستون انتخاب شده
        """
        region = self.identify('region', event.x, event.y)
        if region == "heading":
            column = self.identify_column(event.x)
            column_index = int(column[1]) - 1  # تبدیل #1, #2 و... به 0, 1 و...
            column_name = self['columns'][column_index]
            
            # تغییر جهت مرتب‌سازی اگر ستون قبلاً انتخاب شده بود
            if self._sort_column == column_name:
                self._sort_reverse = not self._sort_reverse
            else:
                self._sort_column = column_name
                self._sort_reverse = False
            
            self._sort_by_column(column_name)
    
    def _sort_by_column(self, column):
        """
        مرتب‌سازی محتویات جدول بر اساس ستون
        column: نام ستون برای مرتب‌سازی
        """
        column_index = self['columns'].index(column)
        items = [(self.set(item, column), item) for item in self.get_children('')]
        
        # تبدیل مقادیر برای مرتب‌سازی صحیح
        def convert_value(value):
            if column in ['volume', 'close', 'last']:  # ستون‌های عددی
                try:
                    return float(value.replace(',', ''))
                except ValueError:
                    return 0
            elif column == 'change':  # ستون درصد تغییرات
                try:
                    return float(value.rstrip('%'))
                except ValueError:
                    return 0
            return value
        
        # مرتب‌سازی آیتم‌ها
        items.sort(key=lambda x: convert_value(x[0]), reverse=self._sort_reverse)
        
        # جابجایی آیتم‌ها به ترتیب جدید
        for index, (_, item) in enumerate(items):
            self.move(item, '', index)