"""
این ماژول صفحه دانلود اطلاعات سهام را مدیریت می‌کند و شامل موارد زیر است:
- نمایش لیست سهام در سه تب (بورس، فرابورس، منتخب)
- امکان انتخاب سهام برای دانلود
- نمایش اطلاعات دانلود شده
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.database import DatabaseManager
from core.api_handler import StockAPI
from datetime import datetime
import threading

class DownloadPage(ttk.Frame):
    def __init__(self, parent):
        """
        سازنده کلاس DownloadPage
        parent: والد ویجت (فریم اصلی)
        """
        super().__init__(parent)
        self.db = DatabaseManager()
        self.api = StockAPI()
        
        # تنظیمات اولیه
        self.setup_ui()
        
        # بارگذاری داده‌ها
        self.load_data()
        
    def setup_ui(self):
        """راه‌اندازی رابط کاربری صفحه دانلود"""
        # ایجاد گرید برای چیدمان اجزا
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # ایجاد فریم‌های اصلی
        self.left_frame = ttk.Frame(self)
        self.left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.right_frame = ttk.Frame(self)
        self.right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # راه‌اندازی فریم سمت چپ
        self.setup_left_frame()
        
        # راه‌اندازی فریم سمت راست
        self.setup_right_frame()
        
    def setup_left_frame(self):
        """راه‌اندازی فریم سمت چپ"""
        # ایجاد نوت‌بوک برای تب‌ها
        self.left_notebook = ttk.Notebook(self.left_frame)
        self.left_notebook.pack(fill="both", expand=True)
        
        # ایجاد تب‌ها
        self.bourse_tab = ttk.Frame(self.left_notebook)
        self.farabourse_tab = ttk.Frame(self.left_notebook)
        self.selected_tab = ttk.Frame(self.left_notebook)
        
        self.left_notebook.add(self.bourse_tab, text="سهام بورس")
        self.left_notebook.add(self.farabourse_tab, text="سهام فرابورس")
        self.left_notebook.add(self.selected_tab, text="سهام منتخب")
        
        # راه‌اندازی جداول
        self.setup_stocks_table(self.bourse_tab, "bourse")
        self.setup_stocks_table(self.farabourse_tab, "farabourse")
        self.setup_stocks_table(self.selected_tab, "selected")
        
    def setup_stocks_table(self, parent, market_type):
        """راه‌اندازی جدول سهام"""
        # ایجاد جدول
        columns = ("نماد", "نام", "انتخاب")
        table = ttk.Treeview(parent, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        
        # چیدمان جدول و اسکرول‌بار
        table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
        # ذخیره جدول
        if market_type == "bourse":
            self.bourse_table = table
        elif market_type == "farabourse":
            self.farabourse_table = table
        else:
            self.selected_table = table
            
        # اضافه کردن چک‌باکس برای انتخاب
        table.bind("<Button-1>", lambda e: self.on_table_click(e, table))
        
    def setup_right_frame(self):
        """راه‌اندازی فریم سمت راست"""
        # ایجاد جدول اطلاعات دانلود شده
        columns = ("نماد", "تاریخ", "اطلاعات", "وضعیت")
        self.download_table = ttk.Treeview(self.right_frame, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            self.download_table.heading(col, text=col)
            self.download_table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.download_table.yview)
        self.download_table.configure(yscrollcommand=scrollbar.set)
        
        # چیدمان جدول و اسکرول‌بار
        self.download_table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
        # دکمه‌های کنترل
        control_frame = ttk.Frame(self.right_frame)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        download_btn = ttk.Button(control_frame, text="دانلود", command=self.download_data)
        download_btn.pack(side="right", padx=5)
        
        clear_btn = ttk.Button(control_frame, text="پاک کردن", command=self.clear_downloads)
        clear_btn.pack(side="right", padx=5)
        
    def load_data(self):
        """بارگذاری داده‌های سهام"""
        try:
            # دریافت اطلاعات سهام
            stocks_data = self.db.get_stock_list()
            
            # جداسازی سهام بر اساس بازار
            bourse_stocks = [s for s in stocks_data if s['market'] == 'بورس']
            farabourse_stocks = [s for s in stocks_data if s['market'] == 'فرابورس']
            
            # به‌روزرسانی جداول
            self.update_stocks_table(self.bourse_table, bourse_stocks)
            self.update_stocks_table(self.farabourse_table, farabourse_stocks)
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {str(e)}")
            
    def update_stocks_table(self, table, data):
        """به‌روزرسانی جدول سهام"""
        # پاک کردن داده‌های قبلی
        for item in table.get_children():
            table.delete(item)
            
        # اضافه کردن داده‌های جدید
        for stock in data:
            table.insert("", "end", values=(
                stock['symbol'],
                stock['name'],
                "□"  # چک‌باکس خالی
            ))
            
    def on_table_click(self, event, table):
        """رویداد کلیک روی جدول"""
        item = table.identify_row(event.y)
        if item:
            values = table.item(item)['values']
            if values:
                # تغییر وضعیت چک‌باکس
                if values[2] == "□":
                    table.set(item, 2, "■")
                else:
                    table.set(item, 2, "□")
                    
    def download_data(self):
        """دانلود اطلاعات سهام انتخاب شده"""
        try:
            # دریافت سهام انتخاب شده
            selected_stocks = []
            
            for table in [self.bourse_table, self.farabourse_table, self.selected_table]:
                for item in table.get_children():
                    values = table.item(item)['values']
                    if values and values[2] == "■":
                        selected_stocks.append(values[0])
                        
            if not selected_stocks:
                messagebox.showwarning("هشدار", "لطفا حداقل یک سهم را انتخاب کنید")
                return
                
            # شروع دانلود در thread جداگانه
            thread = threading.Thread(target=self.download_stocks_data, args=(selected_stocks,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در دانلود داده‌ها: {str(e)}")
            
    def download_stocks_data(self, symbols):
        """دانلود اطلاعات سهام در thread جداگانه"""
        for symbol in symbols:
            try:
                # دانلود اطلاعات
                data = self.api.get_stock_data(symbol)
                
                # به‌روزرسانی جدول در thread اصلی
                self.after(0, self.add_download_item, symbol, data)
                
            except Exception as e:
                self.after(0, self.add_download_item, symbol, None, str(e))
                
    def add_download_item(self, symbol, data, error=None):
        """اضافه کردن آیتم به جدول دانلودها"""
        if error:
            status = f"خطا: {error}"
            info = "-"
        else:
            status = "موفق"
            info = f"{len(data)} رکورد"
            
        self.download_table.insert("", "end", values=(
            symbol,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            info,
            status
        ))
        
    def clear_downloads(self):
        """پاک کردن جدول دانلودها"""
        for item in self.download_table.get_children():
            self.download_table.delete(item)
