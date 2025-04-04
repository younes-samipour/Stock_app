"""
این ماژول صفحه بازار را مدیریت می‌کند و شامل موارد زیر است:
- نمایش لیست سهام با فیلتر و جستجو
- نمایش تغییرات قیمت و حجم معاملات
- نمایش شاخص‌های بازار
- نمایش اخبار و اطلاعیه‌ها
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.database import DatabaseManager
from core.api_handler import StockAPI
from datetime import datetime
import threading
import time

class MarketPage(ttk.Frame):
    def __init__(self, parent):
        """
        سازنده کلاس MarketPage
        parent: والد ویجت (فریم اصلی)
        """
        super().__init__(parent)
        self.db = DatabaseManager()
        self.api = StockAPI()
        self.master = parent.winfo_toplevel()  # Store the master window reference
        
        # تنظیمات اولیه
        self.setup_ui()
        
        # بارگذاری داده‌ها
        self.load_data()
        
        # شروع به‌روزرسانی خودکار
        self.start_auto_update()
        
    def setup_ui(self):
        """راه‌اندازی رابط کاربری صفحه بازار"""
        # ایجاد گرید برای چیدمان اجزا
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ایجاد کنترل‌های فیلتر و جستجو
        self.setup_controls()
        
        # ایجاد تب‌های اطلاعات
        self.setup_tabs()
        
        # ایجاد نوار وضعیت
        self.setup_status_bar()
        
    def setup_controls(self):
        """راه‌اندازی کنترل‌های فیلتر و جستجو"""
        control_frame = ttk.LabelFrame(self, text="کنترل‌ها")
        control_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # جستجو
        ttk.Label(control_frame, text="جستجو:").pack(side="right", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="right", padx=5)
        search_entry.bind("<KeyRelease>", self.filter_stocks)
        
        # فیلتر بازار
        ttk.Label(control_frame, text="بازار:").pack(side="right", padx=5)
        self.market_var = tk.StringVar()
        market_combo = ttk.Combobox(control_frame, textvariable=self.market_var, width=10)
        market_combo["values"] = ("همه", "بورس", "فرابورس", "بازار پایه")
        market_combo.set("همه")
        market_combo.pack(side="right", padx=5)
        market_combo.bind("<<ComboboxSelected>>", self.filter_stocks)
        
        # فیلتر صنعت
        ttk.Label(control_frame, text="صنعت:").pack(side="right", padx=5)
        self.industry_var = tk.StringVar()
        industry_combo = ttk.Combobox(control_frame, textvariable=self.industry_var, width=15)
        industry_combo["values"] = ("همه", "فلزات", "بانک", "خودرو", "سیمان", "پتروشیمی")
        industry_combo.set("همه")
        industry_combo.pack(side="right", padx=5)
        industry_combo.bind("<<ComboboxSelected>>", self.filter_stocks)
        
        # دکمه به‌روزرسانی
        update_btn = ttk.Button(control_frame, text="به‌روزرسانی", command=self.load_data)
        update_btn.pack(side="right", padx=5)
        
    def setup_tabs(self):
        """راه‌اندازی تب‌های اطلاعات"""
        # ایجاد نوت‌بوک برای تب‌ها
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # ایجاد تب سهام
        self.stocks_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.stocks_tab, text="سهام")
        self.setup_stocks_tab()
        
        # ایجاد تب شاخص‌ها
        self.indices_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.indices_tab, text="شاخص‌ها")
        self.setup_indices_tab()
        
        # ایجاد تب اخبار
        self.news_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.news_tab, text="اخبار")
        self.setup_news_tab()
        
    def setup_stocks_tab(self):
        """راه‌اندازی تب سهام"""
        # ایجاد جدول سهام
        columns = ("نماد", "نام", "آخرین قیمت", "تغییر", "حجم", "ارزش", "تعداد", "کمترین", "بیشترین")
        self.stocks_table = ttk.Treeview(self.stocks_tab, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            self.stocks_table.heading(col, text=col)
            self.stocks_table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self.stocks_tab, orient="vertical", command=self.stocks_table.yview)
        self.stocks_table.configure(yscrollcommand=scrollbar.set)
        
        # قرار دادن جدول و اسکرول‌بار
        self.stocks_table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
    def setup_indices_tab(self):
        """راه‌اندازی تب شاخص‌ها"""
        # ایجاد جدول شاخص‌ها
        columns = ("نام", "مقدار", "تغییر", "درصد تغییر")
        self.indices_table = ttk.Treeview(self.indices_tab, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            self.indices_table.heading(col, text=col)
            self.indices_table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self.indices_tab, orient="vertical", command=self.indices_table.yview)
        self.indices_table.configure(yscrollcommand=scrollbar.set)
        
        # قرار دادن جدول و اسکرول‌بار
        self.indices_table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
    def setup_news_tab(self):
        """راه‌اندازی تب اخبار"""
        # ایجاد لیست‌باکس اخبار
        self.news_listbox = tk.Listbox(self.news_tab, width=100, height=20)
        self.news_listbox.pack(side="right", fill="both", expand=True)
        
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self.news_tab, orient="vertical", command=self.news_listbox.yview)
        self.news_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="left", fill="y")
        
    def setup_status_bar(self):
        """راه‌اندازی نوار وضعیت"""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # تعداد سهام
        self.stocks_count_label = ttk.Label(status_frame, text="تعداد سهام: -")
        self.stocks_count_label.pack(side="right", padx=5)
        
        # زمان آخرین به‌روزرسانی
        self.update_label = ttk.Label(status_frame, text="آخرین به‌روزرسانی: -")
        self.update_label.pack(side="right", padx=5)
        
    def load_data(self):
        """بارگذاری داده‌های بازار"""
        try:
            # دریافت اطلاعات سهام
            stocks_data = self.db.get_stock_list()
            
            # به‌روزرسانی جدول در thread اصلی
            self.master.after(0, self.update_stocks_table, stocks_data)
            
        except Exception as e:
            # نمایش خطا در thread اصلی
            self.master.after(0, lambda: messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {str(e)}"))
            
    def update_stocks_table(self, stocks_data):
        """به‌روزرسانی جدول سهام"""
        try:
            # پاک کردن داده‌های قبلی
            for item in self.stocks_table.get_children():
                self.stocks_table.delete(item)
                
            # اضافه کردن داده‌های جدید
            for stock in stocks_data:
                self.stocks_table.insert("", "end", values=(
                    stock['symbol'],
                    stock['name'],
                    stock['code'],
                    stock['sector'],
                    stock['market'],
                    stock['last_update']
                ))
                
            # به‌روزرسانی وضعیت
            self.update_status(len(stocks_data))
                
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("خطا", f"خطا در به‌روزرسانی جدول: {str(e)}"))
            
    def update_indices_table(self, data):
        """به‌روزرسانی جدول شاخص‌ها"""
        # پاک کردن داده‌های قبلی
        for item in self.indices_table.get_children():
            self.indices_table.delete(item)
            
        # اضافه کردن داده‌های جدید
        for item in data:
            self.indices_table.insert("", "end", values=(
                item["name"],
                self.format_number(item["value"]),
                self.format_number(item["change"]),
                f"{item['change_percent']:.2f}%"
            ))
            
    def update_news_list(self, data):
        """به‌روزرسانی لیست اخبار"""
        # پاک کردن داده‌های قبلی
        self.news_listbox.delete(0, tk.END)
        
        # اضافه کردن داده‌های جدید
        for item in data:
            self.news_listbox.insert(tk.END, f"{item['time']} - {item['title']}")
            
    def filter_stocks(self, event=None):
        """فیلتر کردن سهام بر اساس جستجو و فیلترها"""
        try:
            search_text = self.search_var.get().strip().lower()
            market = self.market_var.get()
            industry = self.industry_var.get()
            
            # پاک کردن داده‌های قبلی
            for item in self.stocks_table.get_children():
                self.stocks_table.delete(item)
                
            # دریافت داده‌های فیلتر شده
            filtered_data = self.api.get_filtered_stocks(search_text, market, industry)
            
            # به‌روزرسانی جدول
            self.update_stocks_table(filtered_data)
            
            # به‌روزرسانی وضعیت
            self.update_status(len(filtered_data))
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در فیلتر کردن داده‌ها: {str(e)}")
            
    def update_status(self, count):
        """به‌روزرسانی وضعیت"""
        self.stocks_count_label.config(text=f"تعداد سهام: {count}")
        self.update_label.config(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")
        
    def start_auto_update(self):
        """شروع به‌روزرسانی خودکار"""
        def update_loop():
            while True:
                try:
                    self.master.after(0, self.load_data)
                    time.sleep(60)  # به‌روزرسانی هر دقیقه
                except Exception as e:
                    print(f"خطا در به‌روزرسانی خودکار: {str(e)}")
                    time.sleep(60)  # در صورت خطا، یک دقیقه صبر کن
                    
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        
    def format_number(self, number):
        """فرمت‌بندی اعداد با جداکننده هزارگان"""
        try:
            return "{:,}".format(int(number))
        except:
            return str(number)
            
    def format_change(self, change):
        """فرمت‌بندی تغییرات قیمت"""
        try:
            return f"{change:+.2f}%"
        except:
            return str(change)

    def update_loop(self):
        """حلقه به‌روزرسانی خودکار"""
        while True:
            try:
                self.load_data()
                time.sleep(60)  # به‌روزرسانی هر دقیقه
            except Exception as e:
                print(f"Error in update loop: {str(e)}")
                time.sleep(60)  # در صورت خطا، یک دقیقه صبر کن 