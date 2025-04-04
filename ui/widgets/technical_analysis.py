"""
این ماژول صفحه تحلیل تکنیکال را مدیریت می‌کند و شامل موارد زیر است:
- نمایش نمودار قیمت سهم
- نمایش اندیکاتورهای تکنیکال
- امکان رسم خطوط روند و کانال
- نمایش حجم معاملات
- قابلیت ذخیره و بارگذاری تحلیل‌ها
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.database import DatabaseManager
from core.api_handler import StockAPI
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from tkcalendar import DateEntry
import threading
import time

class TechnicalAnalysis(ttk.Frame):
    def __init__(self, parent):
        """
        سازنده کلاس TechnicalAnalysis
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
        """راه‌اندازی رابط کاربری صفحه تحلیل تکنیکال"""
        # ایجاد گرید برای چیدمان اجزا
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ایجاد کنترل‌های انتخاب سهم و بازه زمانی
        self.setup_controls()
        
        # ایجاد نمودارها
        self.setup_charts()
        
        # ایجاد نوار وضعیت
        self.setup_status_bar()
        
    def setup_controls(self):
        """راه‌اندازی کنترل‌های انتخاب سهم و بازه زمانی"""
        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # انتخاب سهم
        ttk.Label(control_frame, text="نماد:").pack(side="right", padx=5)
        self.symbol_var = tk.StringVar()
        self.symbol_combo = ttk.Combobox(control_frame, textvariable=self.symbol_var)
        self.symbol_combo.pack(side="right", padx=5)
        self.symbol_combo.bind("<<ComboboxSelected>>", self.on_symbol_selected)
        
        # انتخاب بازه زمانی
        ttk.Label(control_frame, text="از:").pack(side="right", padx=5)
        self.start_date = DateEntry(control_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.start_date.pack(side="right", padx=5)
        
        ttk.Label(control_frame, text="تا:").pack(side="right", padx=5)
        self.end_date = DateEntry(control_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2)
        self.end_date.pack(side="right", padx=5)
        
        # دکمه به‌روزرسانی
        update_btn = ttk.Button(control_frame, text="به‌روزرسانی", command=self.update_chart)
        update_btn.pack(side="right", padx=5)
        
        # دکمه‌های اندیکاتورها
        indicators_frame = ttk.Frame(control_frame)
        indicators_frame.pack(side="right", padx=5)
        
        self.ma_var = tk.BooleanVar()
        ma_check = ttk.Checkbutton(indicators_frame, text="میانگین متحرک", variable=self.ma_var)
        ma_check.pack(side="right", padx=5)
        
        self.macd_var = tk.BooleanVar()
        macd_check = ttk.Checkbutton(indicators_frame, text="MACD", variable=self.macd_var)
        macd_check.pack(side="right", padx=5)
        
        self.rsi_var = tk.BooleanVar()
        rsi_check = ttk.Checkbutton(indicators_frame, text="RSI", variable=self.rsi_var)
        rsi_check.pack(side="right", padx=5)
        
    def setup_charts(self):
        """راه‌اندازی نمودارها"""
        # ایجاد فریم برای نمودارها
        chart_frame = ttk.Frame(self)
        chart_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)
        
        # ایجاد نمودار قیمت
        self.price_fig = Figure(figsize=(10, 6))
        self.price_ax = self.price_fig.add_subplot(111)
        self.price_canvas = FigureCanvasTkAgg(self.price_fig, master=chart_frame)
        self.price_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # ایجاد نمودار حجم
        self.volume_fig = Figure(figsize=(10, 2))
        self.volume_ax = self.volume_fig.add_subplot(111)
        self.volume_canvas = FigureCanvasTkAgg(self.volume_fig, master=chart_frame)
        self.volume_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_status_bar(self):
        """راه‌اندازی نوار وضعیت"""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # زمان آخرین به‌روزرسانی
        self.update_label = ttk.Label(status_frame, text="آخرین به‌روزرسانی: -")
        self.update_label.pack(side="right", padx=5)
        
    def load_data(self):
        """بارگذاری داده‌های اولیه"""
        try:
            # دریافت لیست سهام
            stocks = self.db.get_stock_list()
            self.symbol_combo["values"] = [s["symbol"] for s in stocks]
            
            # تنظیم تاریخ‌های پیش‌فرض
            self.end_date.set_date(datetime.now())
            self.start_date.set_date(datetime.now() - timedelta(days=30))
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {str(e)}")
            
    def on_symbol_selected(self, event):
        """رویداد انتخاب سهم"""
        self.update_chart()
        
    def update_chart(self):
        """به‌روزرسانی نمودارها"""
        try:
            symbol = self.symbol_var.get()
            if not symbol:
                return
                
            # دریافت داده‌های قیمت
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            data = self.api.get_stock_history(symbol, start_date, end_date)
            
            if not data:
                messagebox.showwarning("هشدار", "داده‌ای برای نمایش وجود ندارد")
                return
                
            # تبدیل داده‌ها به DataFrame
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            
            # رسم نمودار قیمت
            self.price_ax.clear()
            self.price_ax.plot(df.index, df["close"], label="قیمت بسته شدن")
            
            # رسم میانگین متحرک
            if self.ma_var.get():
                ma20 = df["close"].rolling(window=20).mean()
                ma50 = df["close"].rolling(window=50).mean()
                self.price_ax.plot(df.index, ma20, label="MA20")
                self.price_ax.plot(df.index, ma50, label="MA50")
                
            # رسم MACD
            if self.macd_var.get():
                exp1 = df["close"].ewm(span=12, adjust=False).mean()
                exp2 = df["close"].ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                self.price_ax.plot(df.index, macd, label="MACD")
                self.price_ax.plot(df.index, signal, label="Signal")
                
            # رسم RSI
            if self.rsi_var.get():
                delta = df["close"].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                self.price_ax.plot(df.index, rsi, label="RSI")
                
            # تنظیمات نمودار قیمت
            self.price_ax.set_title(f"نمودار قیمت {symbol}")
            self.price_ax.grid(True)
            self.price_ax.legend()
            
            # رسم نمودار حجم
            self.volume_ax.clear()
            self.volume_ax.bar(df.index, df["volume"])
            self.volume_ax.set_title("حجم معاملات")
            self.volume_ax.grid(True)
            
            # به‌روزرسانی نمودارها
            self.price_canvas.draw()
            self.volume_canvas.draw()
            
            # به‌روزرسانی وضعیت
            self.update_status()
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در به‌روزرسانی نمودار: {str(e)}")
            
    def update_status(self):
        """به‌روزرسانی وضعیت"""
        self.update_label.config(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")
        
    def start_auto_update(self):
        """شروع به‌روزرسانی خودکار داده‌ها"""
        def update_loop():
            while True:
                self.update_chart()
                time.sleep(60)  # به‌روزرسانی هر دقیقه
                
        # اجرای به‌روزرسانی در یک نخ جداگانه
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start() 