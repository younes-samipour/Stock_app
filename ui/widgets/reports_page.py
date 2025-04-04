"""
این ماژول صفحه گزارشات را مدیریت می‌کند و شامل موارد زیر است:
- نمایش گزارشات معاملات
- نمایش گزارشات سود/زیان
- نمایش گزارشات عملکرد پورتفوی
- امکان فیلتر و جستجو در گزارشات
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.database import DatabaseManager
from datetime import datetime, timedelta
import threading
import time

class ReportsPage(ttk.Frame):
    def __init__(self, parent):
        """
        سازنده کلاس ReportsPage
        parent: والد ویجت (فریم اصلی)
        """
        super().__init__(parent)
        self.db = DatabaseManager()
        
        # تنظیمات اولیه
        self.setup_ui()
        
        # بارگذاری داده‌ها
        self.load_data()
        
        # شروع به‌روزرسانی خودکار
        self.start_auto_update()
        
    def setup_ui(self):
        """راه‌اندازی رابط کاربری صفحه گزارشات"""
        # ایجاد گرید برای چیدمان اجزا
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ایجاد کنترل‌های فیلتر
        self.setup_filter_controls()
        
        # ایجاد تب‌های گزارشات
        self.setup_tabs()
        
        # ایجاد نوار وضعیت
        self.setup_status_bar()
        
    def setup_filter_controls(self):
        """راه‌اندازی کنترل‌های فیلتر"""
        filter_frame = ttk.LabelFrame(self, text="فیلترها")
        filter_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # انتخاب نوع گزارش
        ttk.Label(filter_frame, text="نوع گزارش:").pack(side="right", padx=5)
        self.report_type_var = tk.StringVar()
        report_type_combo = ttk.Combobox(filter_frame, textvariable=self.report_type_var)
        report_type_combo["values"] = ("معاملات", "سود/زیان", "عملکرد")
        report_type_combo.set("معاملات")
        report_type_combo.pack(side="right", padx=5)
        
        # انتخاب بازه زمانی
        ttk.Label(filter_frame, text="بازه زمانی:").pack(side="right", padx=5)
        self.time_range_var = tk.StringVar()
        time_range_combo = ttk.Combobox(filter_frame, textvariable=self.time_range_var)
        time_range_combo["values"] = ("امروز", "هفته گذشته", "ماه گذشته", "سه ماه گذشته", "شش ماه گذشته", "یک سال گذشته")
        time_range_combo.set("امروز")
        time_range_combo.pack(side="right", padx=5)
        
        # دکمه اعمال فیلتر
        apply_btn = ttk.Button(filter_frame, text="اعمال فیلتر", command=self.apply_filters)
        apply_btn.pack(side="right", padx=5)
        
    def setup_tabs(self):
        """راه‌اندازی تب‌های گزارشات"""
        # ایجاد نوت‌بوک برای تب‌ها
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # ایجاد تب گزارشات معاملات
        self.trades_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.trades_tab, text="گزارشات معاملات")
        self.setup_trades_tab()
        
        # ایجاد تب گزارشات سود/زیان
        self.profit_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.profit_tab, text="گزارشات سود/زیان")
        self.setup_profit_tab()
        
        # ایجاد تب گزارشات عملکرد
        self.performance_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.performance_tab, text="گزارشات عملکرد")
        self.setup_performance_tab()
        
    def setup_trades_tab(self):
        """راه‌اندازی تب گزارشات معاملات"""
        # ایجاد جدول معاملات
        columns = ("تاریخ", "نوع", "نماد", "تعداد", "قیمت", "ارزش", "کارمزد")
        self.trades_table = ttk.Treeview(self.trades_tab, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            self.trades_table.heading(col, text=col)
            self.trades_table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self.trades_tab, orient="vertical", command=self.trades_table.yview)
        self.trades_table.configure(yscrollcommand=scrollbar.set)
        
        # قرار دادن جدول و اسکرول‌بار
        self.trades_table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
    def setup_profit_tab(self):
        """راه‌اندازی تب گزارشات سود/زیان"""
        # ایجاد جدول سود/زیان
        columns = ("تاریخ", "نماد", "تعداد", "قیمت خرید", "قیمت فعلی", "سود/زیان", "بازده")
        self.profit_table = ttk.Treeview(self.profit_tab, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            self.profit_table.heading(col, text=col)
            self.profit_table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self.profit_tab, orient="vertical", command=self.profit_table.yview)
        self.profit_table.configure(yscrollcommand=scrollbar.set)
        
        # قرار دادن جدول و اسکرول‌بار
        self.profit_table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
    def setup_performance_tab(self):
        """راه‌اندازی تب گزارشات عملکرد"""
        # ایجاد جدول عملکرد
        columns = ("تاریخ", "ارزش پورتفوی", "سود/زیان روزانه", "بازده روزانه", "سود/زیان کل", "بازده کل")
        self.performance_table = ttk.Treeview(self.performance_tab, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            self.performance_table.heading(col, text=col)
            self.performance_table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self.performance_tab, orient="vertical", command=self.performance_table.yview)
        self.performance_table.configure(yscrollcommand=scrollbar.set)
        
        # قرار دادن جدول و اسکرول‌بار
        self.performance_table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
    def setup_status_bar(self):
        """راه‌اندازی نوار وضعیت"""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # زمان آخرین به‌روزرسانی
        self.update_label = ttk.Label(status_frame, text="آخرین به‌روزرسانی: -")
        self.update_label.pack(side="right", padx=5)
        
    def load_data(self):
        """بارگذاری داده‌های گزارشات"""
        try:
            # دریافت گزارشات معاملات
            trades_data = self.db.get_trades_report()
            self.update_trades_table(trades_data)
            
            # دریافت گزارشات سود/زیان
            profit_data = self.db.get_profit_report()
            self.update_profit_table(profit_data)
            
            # دریافت گزارشات عملکرد
            performance_data = self.db.get_performance_report()
            self.update_performance_table(performance_data)
            
            # به‌روزرسانی وضعیت
            self.update_status()
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {str(e)}")
            
    def update_trades_table(self, data):
        """به‌روزرسانی جدول معاملات"""
        # پاک کردن داده‌های قبلی
        for item in self.trades_table.get_children():
            self.trades_table.delete(item)
            
        # اضافه کردن داده‌های جدید
        for item in data:
            self.trades_table.insert("", "end", values=(
                item["date"],
                item["type"],
                item["symbol"],
                self.format_number(item["quantity"]),
                self.format_number(item["price"]),
                self.format_number(item["value"]),
                self.format_number(item["fee"])
            ))
            
    def update_profit_table(self, data):
        """به‌روزرسانی جدول سود/زیان"""
        # پاک کردن داده‌های قبلی
        for item in self.profit_table.get_children():
            self.profit_table.delete(item)
            
        # اضافه کردن داده‌های جدید
        for item in data:
            self.profit_table.insert("", "end", values=(
                item["date"],
                item["symbol"],
                self.format_number(item["quantity"]),
                self.format_number(item["buy_price"]),
                self.format_number(item["current_price"]),
                self.format_number(item["profit"]),
                f"{item['return']:.2f}%"
            ))
            
    def update_performance_table(self, data):
        """به‌روزرسانی جدول عملکرد"""
        # پاک کردن داده‌های قبلی
        for item in self.performance_table.get_children():
            self.performance_table.delete(item)
            
        # اضافه کردن داده‌های جدید
        for item in data:
            self.performance_table.insert("", "end", values=(
                item["date"],
                self.format_number(item["portfolio_value"]),
                self.format_number(item["daily_profit"]),
                f"{item['daily_return']:.2f}%",
                self.format_number(item["total_profit"]),
                f"{item['total_return']:.2f}%"
            ))
            
    def apply_filters(self):
        """اعمال فیلترهای انتخاب شده"""
        try:
            # دریافت نوع گزارش و بازه زمانی
            report_type = self.report_type_var.get()
            time_range = self.time_range_var.get()
            
            # محاسبه تاریخ شروع بر اساس بازه زمانی
            end_date = datetime.now()
            if time_range == "امروز":
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_range == "هفته گذشته":
                start_date = end_date - timedelta(days=7)
            elif time_range == "ماه گذشته":
                start_date = end_date - timedelta(days=30)
            elif time_range == "سه ماه گذشته":
                start_date = end_date - timedelta(days=90)
            elif time_range == "شش ماه گذشته":
                start_date = end_date - timedelta(days=180)
            else:  # یک سال گذشته
                start_date = end_date - timedelta(days=365)
                
            # بارگذاری داده‌ها با فیلتر
            if report_type == "معاملات":
                trades_data = self.db.get_trades_report(start_date, end_date)
                self.update_trades_table(trades_data)
            elif report_type == "سود/زیان":
                profit_data = self.db.get_profit_report(start_date, end_date)
                self.update_profit_table(profit_data)
            else:  # عملکرد
                performance_data = self.db.get_performance_report(start_date, end_date)
                self.update_performance_table(performance_data)
                
            # به‌روزرسانی وضعیت
            self.update_status()
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در اعمال فیلتر: {str(e)}")
            
    def update_status(self):
        """به‌روزرسانی وضعیت"""
        self.update_label.config(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")
        
    def start_auto_update(self):
        """شروع به‌روزرسانی خودکار"""
        def update_loop():
            while True:
                self.load_data()
                time.sleep(60)  # به‌روزرسانی هر دقیقه
                
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        
    def format_number(self, number):
        """فرمت‌بندی اعداد با جداکننده هزارگان"""
        try:
            return "{:,}".format(int(number))
        except:
            return str(number) 