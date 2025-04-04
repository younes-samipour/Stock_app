"""
این ماژول مدیریت تب‌های برنامه را بر عهده دارد و شامل موارد زیر است:
- مدیریت تب‌های بورس، فرابورس و علاقه‌مندی‌ها
- نمایش لیست سهام در هر تب
- مدیریت انتخاب سهام توسط کاربر
- نمایش کنترل‌های وضعیت برنامه
"""

import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from ui.widgets.stock_table import StockTable

class TabManager:
    def __init__(self, parent, main_window):
        """
        سازنده کلاس TabManager
        parent: فریم والد که تب‌ها در آن قرار می‌گیرند
        main_window: نمونه کلاس MainWindow برای دسترسی به توابع آن
        """
        self.parent = parent
        self.main_window = main_window
        self.selected_stocks = {}  # دیکشنری برای نگهداری سهام منتخب
        self.setup_tabs()
    
    def setup_tabs(self):
        """
        راه‌اندازی تب‌های اصلی برنامه
        شامل ایجاد کانتینر اصلی و تب‌های بورس، فرابورس و علاقه‌مندی‌ها
        """
        # ایجاد کانتینر اصلی سمت راست با عرض ثابت
        self.right_container = ttk.Frame(self.parent, width=300)
        self.right_container.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        self.right_container.pack_propagate(False)
        
        # ایجاد تب‌ها
        self.tab_control = ttk.Notebook(self.right_container)
        
        # ایجاد فریم‌های هر تب با اندازه ثابت
        self.bourse_frame = ttk.Frame(self.tab_control, width=300, height=450)
        self.farabourse_frame = ttk.Frame(self.tab_control, width=300, height=450)
        self.favorites_frame = ttk.Frame(self.tab_control, width=300, height=450)
        
        # جلوگیری از تغییر اندازه فریم‌ها
        for frame in (self.bourse_frame, self.farabourse_frame, self.favorites_frame):
            frame.pack_propagate(False)
            frame.grid_propagate(False)
        
        # اضافه کردن تب‌ها
        self.tab_control.add(self.bourse_frame, text='بورس')
        self.tab_control.add(self.farabourse_frame, text='فرابورس')
        self.tab_control.add(self.favorites_frame, text='علاقه‌مندی‌ها')
        
        self.tab_control.pack(fill=tk.BOTH)
        
        # راه‌اندازی محتوای هر تب
        self.setup_bourse_tab()
        self.setup_farabourse_tab()
        self.setup_favorites_tab()
        
        # ایجاد فریم کنترل‌ها در پایین
        self.setup_control_frame()
        
        # بارگذاری سهام منتخب از دیتابیس
        self.load_favorites_from_db()
    
    def setup_control_frame(self):
        """
        راه‌اندازی فریم کنترل‌های برنامه
        شامل نوار پیشرفت، وضعیت، ساعت و کرنومتر
        """
        self.control_frame = ttk.Frame(self.right_container, width=300)
        self.control_frame.pack(fill=tk.X, pady=5)
        self.control_frame.pack_propagate(False)
        
        # ایجاد نوار پیشرفت
        self.progress = ttk.Progressbar(
            self.control_frame,
            orient=tk.HORIZONTAL,
            mode='determinate',
            length=280
        )
        self.progress.pack(padx=10, pady=5)
        
        # ایجاد لیبل وضعیت
        self.status_var = tk.StringVar(value="آماده به کار")
        status_label = ttk.Label(
            self.control_frame,
            textvariable=self.status_var,
            anchor='center'
        )
        status_label.pack(fill=tk.X, padx=10)
        
        # ایجاد ساعت و کرنومتر
        time_frame = ttk.Frame(self.control_frame)
        time_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # ساعت دیجیتال
        self.clock_var = tk.StringVar()
        clock_label = ttk.Label(
            time_frame,
            textvariable=self.clock_var,
            font=('Arial', 10)
        )
        clock_label.pack(side=tk.LEFT)
        
        # کرنومتر
        self.stopwatch_var = tk.StringVar(value="00:00:00.000")
        stopwatch_label = ttk.Label(
            time_frame,
            textvariable=self.stopwatch_var,
            font=('Arial', 10)
        )
        stopwatch_label.pack(side=tk.RIGHT)
    
    def setup_bourse_tab(self):
        """
        راه‌اندازی تب بورس
        شامل جدول نمایش سهام بورس و دکمه‌های مدیریت آن
        """
        # ایجاد فریم اصلی
        container = ttk.Frame(self.bourse_frame)
        container.grid(row=0, column=0, sticky='nsew')
        
        # ایجاد جدول نمایش سهام بورس با ارتفاع محدود
        self.bourse_table = StockTable(
            container,
            columns=("code", "symbol"),
            column_names=("کد معاملاتی", "نماد"),
            selectmode='extended',
            height=10  # محدود کردن تعداد ردیف‌های قابل نمایش
        )
        
        # تنظیم رنگ برای سهام منتخب بورس
        self.bourse_table.tag_configure('bourse_favorite', background='#E6F7FF')
        
        # قرار دادن جدول در گرید
        self.bourse_table.container.grid(row=0, column=0, sticky='nsew')
        
        # پر کردن جدول با سهام بورس (کد با 1 شروع می‌شود)
        for symbol, code in self.main_window.all_stocks.items():
            if code.startswith('1'):
                self.bourse_table.insert_item((code, symbol))
        
        # اتصال رویداد دبل کلیک برای افزودن به منتخب‌ها
        self.bourse_table.bind('<Double-1>', self.add_bourse_to_favorites)
        
        # ایجاد فریم دکمه‌ها
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=1, column=0, sticky='ew')
        
        # دکمه‌های مدیریت جدول
        ttk.Button(
            btn_frame,
            text="انتخاب همه",
            command=lambda: self.bourse_table.selection_set(self.bourse_table.get_children())
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="حذف انتخاب‌ها",
            command=lambda: self.bourse_table.selection_remove(self.bourse_table.selection())
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="دریافت اطلاعات",
            command=lambda: self.start_fetching('bourse'),
            style='Accent.TButton'
        ).pack(side=tk.LEFT)
    
    def setup_farabourse_tab(self):
        """
        راه‌اندازی تب فرابورس
        شامل جدول نمایش سهام فرابورس و دکمه‌های مدیریت آن
        """
        # ایجاد فریم اصلی
        container = ttk.Frame(self.farabourse_frame)
        container.grid(row=0, column=0, sticky='nsew')
        
        # ایجاد جدول نمایش سهام فرابورس با ارتفاع محدود
        self.farabourse_table = StockTable(
            container,
            columns=("code", "symbol"),
            column_names=("کد معاملاتی", "نماد"),
            selectmode='extended',
            height=10  # محدود کردن تعداد ردیف‌های قابل نمایش
        )
        
        # تنظیم رنگ برای سهام منتخب فرابورس
        self.farabourse_table.tag_configure('farabourse_favorite', background='#E6FFE6')
        
        # قرار دادن جدول در گرید
        self.farabourse_table.container.grid(row=0, column=0, sticky='nsew')
        
        # پر کردن جدول با سهام فرابورس (کد با 2 شروع می‌شود)
        for symbol, code in self.main_window.all_stocks.items():
            if code.startswith('2'):
                self.farabourse_table.insert_item((code, symbol))
        
        # اتصال رویداد دبل کلیک برای افزودن به منتخب‌ها
        self.farabourse_table.bind('<Double-1>', self.add_farabourse_to_favorites)
        
        # ایجاد فریم دکمه‌ها
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=1, column=0, sticky='ew')
        
        # دکمه‌های مدیریت جدول
        ttk.Button(
            btn_frame,
            text="انتخاب همه",
            command=lambda: self.farabourse_table.selection_set(self.farabourse_table.get_children())
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="حذف انتخاب‌ها",
            command=lambda: self.farabourse_table.selection_remove(self.farabourse_table.selection())
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="دریافت اطلاعات",
            command=lambda: self.start_fetching('farabourse'),
            style='Accent.TButton'
        ).pack(side=tk.LEFT)
    
    def setup_favorites_tab(self):
        """
        راه‌اندازی تب علاقه‌مندی‌ها
        شامل جدول نمایش سهام منتخب و دکمه‌های مدیریت آن
        """
        # ایجاد فریم اصلی
        container = ttk.Frame(self.favorites_frame)
        container.grid(row=0, column=0, sticky='nsew')
        
        # ایجاد جدول نمایش سهام منتخب با ارتفاع محدود
        self.favorites_table = StockTable(
            container,
            columns=("code", "symbol"),
            column_names=("کد معاملاتی", "نماد"),
            selectmode='extended',
            height=10  # محدود کردن تعداد ردیف‌های قابل نمایش
        )
        
        # قرار دادن جدول در گرید
        self.favorites_table.container.grid(row=0, column=0, sticky='nsew')
        
        # ایجاد فریم دکمه‌ها
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=1, column=0, sticky='ew')
        
        # دکمه‌های مدیریت جدول
        ttk.Button(
            btn_frame,
            text="حذف از منتخب‌ها",
            command=self.remove_from_favorites
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="دریافت اطلاعات",
            command=lambda: self.start_fetching('favorites'),
            style='Accent.TButton'
        ).pack(side=tk.LEFT)
    
    def add_bourse_to_favorites(self, event):
        """
        افزودن سهام انتخاب شده بورس به لیست منتخب‌ها
        event: رویداد دبل کلیک
        """
        selected = self.bourse_table.selection()
        if selected:
            item = self.bourse_table.item(selected[0])
            symbol = item['values'][1]
            code = item['values'][0]
            
            # افزودن به لیست منتخب‌ها اگر قبلاً اضافه نشده باشد
            if symbol not in self.selected_stocks:
                self.selected_stocks[symbol] = code
                self.bourse_table.item(selected[0], tags=('bourse_favorite',))
                self.populate_favorites_stocks()
                self.save_favorites_to_db()
    
    def add_farabourse_to_favorites(self, event):
        """
        افزودن سهام انتخاب شده فرابورس به لیست منتخب‌ها
        event: رویداد دبل کلیک
        """
        selected = self.farabourse_table.selection()
        if selected:
            item = self.farabourse_table.item(selected[0])
            symbol = item['values'][1]
            code = item['values'][0]
            
            # افزودن به لیست منتخب‌ها اگر قبلاً اضافه نشده باشد
            if symbol not in self.selected_stocks:
                self.selected_stocks[symbol] = code
                self.farabourse_table.item(selected[0], tags=('farabourse_favorite',))
                self.populate_favorites_stocks()
                self.save_favorites_to_db()
    
    def remove_from_favorites(self):
        """
        حذف سهام انتخاب شده از لیست منتخب‌ها
        """
        selected = self.favorites_table.selection()
        if not selected:
            return
            
        for item in selected:
            values = self.favorites_table.item(item, 'values')
            symbol = values[1]
            
            if symbol in self.selected_stocks:
                del self.selected_stocks[symbol]
                
                # حذف رنگ از جدول اصلی
                code = values[0]
                if code.startswith('1'):  # بورس
                    for bourse_item in self.bourse_table.get_children():
                        if self.bourse_table.item(bourse_item, 'values')[1] == symbol:
                            self.bourse_table.item(bourse_item, tags=())
                            break
                else:  # فرابورس
                    for farabourse_item in self.farabourse_table.get_children():
                        if self.farabourse_table.item(farabourse_item, 'values')[1] == symbol:
                            self.farabourse_table.item(farabourse_item, tags=())
                            break
        
        # به‌روزرسانی جدول منتخب‌ها و ذخیره در دیتابیس
        self.populate_favorites_stocks()
        self.save_favorites_to_db()
    
    def load_favorites_from_db(self):
        """
        بارگذاری لیست سهام منتخب از دیتابیس
        """
        try:
            # ایجاد جدول favorites اگر وجود نداشته باشد
            self.main_window.db.cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL UNIQUE,
                    code TEXT NOT NULL UNIQUE
                )
            ''')
            
            # خواندن رکوردها از دیتابیس
            self.main_window.db.cursor.execute('SELECT symbol, code FROM favorites')
            rows = self.main_window.db.cursor.fetchall()
            
            # ذخیره در دیکشنری سهام منتخب
            self.selected_stocks = {symbol: code for symbol, code in rows}
            self.populate_favorites_stocks()
            
            # علامت‌گذاری سهام منتخب در جداول اصلی
            for symbol, code in self.selected_stocks.items():
                if code.startswith('1'):  # بورس
                    for item in self.bourse_table.get_children():
                        if self.bourse_table.item(item, 'values')[1] == symbol:
                            self.bourse_table.item(item, tags=('bourse_favorite',))
                            break
                else:  # فرابورس
                    for item in self.farabourse_table.get_children():
                        if self.farabourse_table.item(item, 'values')[1] == symbol:
                            self.farabourse_table.item(item, tags=('farabourse_favorite',))
                            break
            
        except Exception as e:
            print(f"Error loading favorites: {str(e)}")
    
    def populate_favorites_stocks(self):
        """
        به‌روزرسانی جدول سهام منتخب
        پاک کردن جدول و پر کردن مجدد آن با سهام منتخب
        """
        if hasattr(self, 'favorites_table'):
            self.favorites_table.clear()
            for symbol, code in self.selected_stocks.items():
                self.favorites_table.insert_item((code, symbol))
    
    def save_favorites_to_db(self):
        """
        ذخیره لیست سهام منتخب در دیتابیس
        """
        try:
            # پاک کردن رکوردهای قبلی
            self.main_window.db.cursor.execute('DELETE FROM favorites')
            
            # درج رکوردهای جدید
            for symbol, code in self.selected_stocks.items():
                self.main_window.db.cursor.execute(
                    'INSERT INTO favorites (symbol, code) VALUES (?, ?)', 
                    (symbol, code)
                )
            
            # ذخیره تغییرات
            self.main_window.db.conn.commit()
            
        except Exception as e:
            print(f"Error saving favorites: {str(e)}")
    
    def start_fetching(self, tab_name):
        """
        شروع دریافت اطلاعات سهام انتخاب شده
        tab_name: نام تب ('bourse', 'farabourse', یا 'favorites')
        """
        # تعیین جدول مورد نظر بر اساس نام تب
        if tab_name == 'bourse':
            selected_items = self.bourse_table.selection()
            tree = self.bourse_table
        elif tab_name == 'farabourse':
            selected_items = self.farabourse_table.selection()
            tree = self.farabourse_table
        else:
            selected_items = self.favorites_table.get_children()
            tree = self.favorites_table
            
        # بررسی انتخاب حداقل یک سهم
        if not selected_items:
            messagebox.showwarning("هشدار", "لطفاً حداقل یک نماد را انتخاب کنید")
            return
            
        # ایجاد دیکشنری سهام برای دریافت اطلاعات
        stocks_to_fetch = {}
        for item in selected_items:
            values = tree.item(item, 'values')
            stocks_to_fetch[values[1]] = values[0]
        
        # شروع دریافت اطلاعات در یک thread جداگانه
        fetch_thread = Thread(
            target=self.main_window.fetch_data,
            args=(stocks_to_fetch,),
            daemon=True
        )
        fetch_thread.start()