"""
این ماژول صفحه داشبورد را مدیریت می‌کند و شامل موارد زیر است:
- نمایش خلاصه وضعیت پورتفوی
- نمایش نمودار تغییرات ارزش پورتفوی
- نمایش سهام برتر پورتفوی
- نمایش اخبار مهم بازار
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.database import DatabaseManager
from core.api_handler import StockAPI
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')  # تنظیم backend برای استفاده در Tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time

class Dashboard(ttk.Frame):
    def __init__(self, parent):
        """
        سازنده کلاس Dashboard
        parent: والد ویجت (فریم اصلی)
        """
        super().__init__(parent)
        self.db = DatabaseManager()
        self.api = StockAPI()
        
        # تنظیمات اولیه
        self.setup_ui()
        
        # بارگذاری داده‌ها
        self.load_data()
        
        # شروع به‌روزرسانی خودکار
        self.start_auto_update()
        
    def setup_ui(self):
        """راه‌اندازی رابط کاربری صفحه داشبورد"""
        # ایجاد گرید برای چیدمان اجزا
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ایجاد خلاصه وضعیت
        self.setup_summary()
        
        # ایجاد نمودارها و جداول
        self.setup_charts_and_tables()
        
        # ایجاد نوار وضعیت
        self.setup_status_bar()
        
    def setup_summary(self):
        """راه‌اندازی خلاصه وضعیت پورتفوی"""
        summary_frame = ttk.LabelFrame(self, text="خلاصه وضعیت")
        summary_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # ارزش کل پورتفوی
        ttk.Label(summary_frame, text="ارزش کل پورتفوی:").pack(side="right", padx=5)
        self.total_value_label = ttk.Label(summary_frame, text="-")
        self.total_value_label.pack(side="right", padx=5)
        
        # سود/زیان کل
        ttk.Label(summary_frame, text="سود/زیان کل:").pack(side="right", padx=5)
        self.total_profit_label = ttk.Label(summary_frame, text="-")
        self.total_profit_label.pack(side="right", padx=5)
        
        # بازده کل
        ttk.Label(summary_frame, text="بازده کل:").pack(side="right", padx=5)
        self.total_return_label = ttk.Label(summary_frame, text="-")
        self.total_return_label.pack(side="right", padx=5)
        
        # تعداد سهام
        ttk.Label(summary_frame, text="تعداد سهام:").pack(side="right", padx=5)
        self.stocks_count_label = ttk.Label(summary_frame, text="-")
        self.stocks_count_label.pack(side="right", padx=5)
        
    def setup_charts_and_tables(self):
        """راه‌اندازی نمودارها و جداول"""
        # ایجاد فریم برای نمودارها و جداول
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # ایجاد نمودار ارزش پورتفوی
        chart_frame = ttk.LabelFrame(content_frame, text="تغییرات ارزش پورتفوی")
        chart_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.portfolio_fig = Figure(figsize=(8, 4))
        self.portfolio_ax = self.portfolio_fig.add_subplot(111)
        self.portfolio_canvas = FigureCanvasTkAgg(self.portfolio_fig, master=chart_frame)
        self.portfolio_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # ایجاد جدول سهام برتر
        table_frame = ttk.LabelFrame(content_frame, text="سهام برتر پورتفوی")
        table_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        columns = ("نماد", "تعداد", "ارزش", "سود/زیان", "بازده")
        self.top_stocks_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.top_stocks_table.heading(col, text=col)
            self.top_stocks_table.column(col, width=80)
            
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.top_stocks_table.yview)
        self.top_stocks_table.configure(yscrollcommand=scrollbar.set)
        
        self.top_stocks_table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
        # ایجاد لیست اخبار
        news_frame = ttk.LabelFrame(content_frame, text="اخبار مهم")
        news_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        self.news_listbox = tk.Listbox(news_frame, width=100, height=5)
        self.news_listbox.pack(side="right", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(news_frame, orient="vertical", command=self.news_listbox.yview)
        self.news_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="left", fill="y")
        
    def setup_status_bar(self):
        """راه‌اندازی نوار وضعیت"""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # زمان آخرین به‌روزرسانی
        self.update_label = ttk.Label(status_frame, text="آخرین به‌روزرسانی: -")
        self.update_label.pack(side="right", padx=5)
        
    def load_data(self):
        """بارگذاری داده‌های داشبورد"""
        try:
            # دریافت اطلاعات پورتفوی
            portfolio_data = self.db.get_portfolio_summary()
            self.update_summary(portfolio_data)
            
            # دریافت تاریخچه ارزش پورتفوی
            history_data = self.db.get_portfolio_history()
            self.update_portfolio_chart(history_data)
            
            # دریافت سهام برتر
            top_stocks = self.db.get_top_stocks()
            self.update_top_stocks_table(top_stocks)
            
            # دریافت اخبار مهم
            news_data = self.api.get_important_news()
            self.update_news_list(news_data)
            
            # به‌روزرسانی وضعیت
            self.update_status()
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {str(e)}")
            
    def update_summary(self, data):
        """به‌روزرسانی خلاصه وضعیت"""
        self.total_value_label.config(text=self.format_number(data["total_value"]))
        self.total_profit_label.config(text=self.format_number(data["total_profit"]))
        self.total_return_label.config(text=f"{data['total_return']:.2f}%")
        self.stocks_count_label.config(text=str(data["stocks_count"]))
        
    def update_portfolio_chart(self, data):
        """به‌روزرسانی نمودار ارزش پورتفوی"""
        # پاک کردن نمودار قبلی
        self.portfolio_ax.clear()
        
        # رسم نمودار جدید
        dates = [d["date"] for d in data]
        values = [d["value"] for d in data]
        self.portfolio_ax.plot(dates, values)
        
        # تنظیمات نمودار
        self.portfolio_ax.set_title("تغییرات ارزش پورتفوی")
        self.portfolio_ax.grid(True)
        
        # به‌روزرسانی نمودار
        self.portfolio_canvas.draw()
        
    def update_top_stocks_table(self, data):
        """به‌روزرسانی جدول سهام برتر"""
        # پاک کردن داده‌های قبلی
        for item in self.top_stocks_table.get_children():
            self.top_stocks_table.delete(item)
            
        # اضافه کردن داده‌های جدید
        for item in data:
            self.top_stocks_table.insert("", "end", values=(
                item["symbol"],
                self.format_number(item["quantity"]),
                self.format_number(item["value"]),
                self.format_number(item["profit"]),
                f"{item['return']:.2f}%"
            ))
            
    def update_news_list(self, data):
        """به‌روزرسانی لیست اخبار"""
        # پاک کردن لیست قبلی
        self.news_listbox.delete(0, tk.END)
        
        # اضافه کردن اخبار جدید
        for item in data:
            self.news_listbox.insert(tk.END, f"{item['time']} - {item['title']}")
            
    def update_status(self):
        """به‌روزرسانی وضعیت"""
        self.update_label.config(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")
        
    def start_auto_update(self):
        """شروع به‌روزرسانی خودکار"""
        def update_loop():
            try:
                self.load_data()
                self.update_status()
            except Exception as e:
                print(f"Error in auto update: {str(e)}")
            finally:
                # برنامه‌ریزی به‌روزرسانی بعدی
                self.after(60000, update_loop)  # هر 1 دقیقه
        
        # شروع اولین به‌روزرسانی
        self.after(0, update_loop)
        
    def format_number(self, number):
        """قالب‌بندی اعداد با جداکننده هزارگان"""
        return f"{number:,}" 