"""
این ماژول صفحه تحلیل بنیادی را مدیریت می‌کند و شامل موارد زیر است:
- نمایش اطلاعات بنیادی سهام
- نسبت‌های مالی
- صورت‌های مالی
- تحلیل سودآوری و رشد
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.database import DatabaseManager
from core.api_handler import StockAPI
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import threading
import time

class FundamentalAnalysis(ttk.Frame):
    def __init__(self, parent):
        """
        سازنده کلاس FundamentalAnalysis
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
        """راه‌اندازی رابط کاربری صفحه تحلیل بنیادی"""
        # ایجاد گرید برای چیدمان اجزا
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ایجاد کنترل‌های انتخاب سهم
        self.setup_controls()
        
        # ایجاد تب‌های نمایش اطلاعات
        self.setup_tabs()
        
        # ایجاد نوار وضعیت
        self.setup_status_bar()
        
    def setup_controls(self):
        """راه‌اندازی کنترل‌های انتخاب سهم"""
        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # انتخاب سهم
        ttk.Label(control_frame, text="نماد:").pack(side="right", padx=5)
        self.symbol_var = tk.StringVar()
        self.symbol_combo = ttk.Combobox(control_frame, textvariable=self.symbol_var)
        self.symbol_combo.pack(side="right", padx=5)
        self.symbol_combo.bind("<<ComboboxSelected>>", self.on_symbol_selected)
        
        # دکمه به‌روزرسانی
        update_btn = ttk.Button(control_frame, text="به‌روزرسانی", command=self.update_data)
        update_btn.pack(side="right", padx=5)
        
    def setup_tabs(self):
        """راه‌اندازی تب‌های نمایش اطلاعات"""
        # ایجاد تب‌ها
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # تب اطلاعات بنیادی
        self.basic_info_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.basic_info_frame, text="اطلاعات بنیادی")
        self.setup_basic_info()
        
        # تب نسبت‌های مالی
        self.ratios_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.ratios_frame, text="نسبت‌های مالی")
        self.setup_financial_ratios()
        
        # تب صورت‌های مالی
        self.statements_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.statements_frame, text="صورت‌های مالی")
        self.setup_financial_statements()
        
        # تب تحلیل سودآوری
        self.profitability_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.profitability_frame, text="تحلیل سودآوری")
        self.setup_profitability_analysis()
        
    def setup_basic_info(self):
        """راه‌اندازی نمایش اطلاعات بنیادی"""
        # ایجاد جدول اطلاعات
        columns = ("عنوان", "مقدار")
        self.basic_info_table = ttk.Treeview(self.basic_info_frame, columns=columns, show="headings")
        
        for col in columns:
            self.basic_info_table.heading(col, text=col)
            self.basic_info_table.column(col, width=150)
            
        scrollbar = ttk.Scrollbar(self.basic_info_frame, orient="vertical", command=self.basic_info_table.yview)
        self.basic_info_table.configure(yscrollcommand=scrollbar.set)
        
        self.basic_info_table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
    def setup_financial_ratios(self):
        """راه‌اندازی نمایش نسبت‌های مالی"""
        # ایجاد جدول نسبت‌ها
        columns = ("نسبت", "مقدار", "تغییر", "رتبه")
        self.ratios_table = ttk.Treeview(self.ratios_frame, columns=columns, show="headings")
        
        for col in columns:
            self.ratios_table.heading(col, text=col)
            self.ratios_table.column(col, width=100)
            
        scrollbar = ttk.Scrollbar(self.ratios_frame, orient="vertical", command=self.ratios_table.yview)
        self.ratios_table.configure(yscrollcommand=scrollbar.set)
        
        self.ratios_table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
    def setup_financial_statements(self):
        """راه‌اندازی نمایش صورت‌های مالی"""
        # ایجاد تب‌های صورت‌های مالی
        statements_tabs = ttk.Notebook(self.statements_frame)
        statements_tabs.pack(fill="both", expand=True)
        
        # تب ترازنامه
        balance_sheet_frame = ttk.Frame(statements_tabs)
        statements_tabs.add(balance_sheet_frame, text="ترازنامه")
        
        # تب صورت سود و زیان
        income_statement_frame = ttk.Frame(statements_tabs)
        statements_tabs.add(income_statement_frame, text="صورت سود و زیان")
        
        # تب صورت جریان وجوه نقد
        cash_flow_frame = ttk.Frame(statements_tabs)
        statements_tabs.add(cash_flow_frame, text="صورت جریان وجوه نقد")
        
    def setup_profitability_analysis(self):
        """راه‌اندازی تحلیل سودآوری"""
        # ایجاد نمودار سودآوری
        self.profitability_fig = Figure(figsize=(10, 6))
        self.profitability_ax = self.profitability_fig.add_subplot(111)
        self.profitability_canvas = FigureCanvasTkAgg(self.profitability_fig, master=self.profitability_frame)
        self.profitability_canvas.get_tk_widget().pack(fill="both", expand=True)
        
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
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {str(e)}")
            
    def on_symbol_selected(self, event):
        """رویداد انتخاب سهم"""
        self.update_data()
        
    def update_data(self):
        """به‌روزرسانی داده‌ها"""
        try:
            # دریافت نماد انتخاب شده
            symbol = self.symbol_var.get()
            if not symbol:
                return
                
            # دریافت اطلاعات پایه
            basic_info = self.api.get_basic_info(symbol)
            if basic_info:
                self.update_basic_info(basic_info)
                
            # دریافت نسبت‌های مالی
            financial_ratios = self.api.get_financial_ratios(symbol)
            if financial_ratios:
                self.update_financial_ratios(financial_ratios)
                
            # دریافت صورت‌های مالی
            financial_statements = self.api.get_financial_statements(symbol)
            if financial_statements:
                self.update_financial_statements(financial_statements)
                
            # دریافت تحلیل سودآوری
            profitability = self.api.get_profitability_analysis(symbol)
            if profitability:
                self.update_profitability_analysis(profitability)
                
        except Exception as e:
            print(f"Error updating data: {str(e)}")
            
    def update_basic_info(self, data):
        """به‌روزرسانی اطلاعات بنیادی"""
        # پاک کردن داده‌های قبلی
        for item in self.basic_info_table.get_children():
            self.basic_info_table.delete(item)
            
        # اضافه کردن داده‌های جدید
        for key, value in data.items():
            self.basic_info_table.insert("", "end", values=(key, value))
            
    def update_financial_ratios(self, data):
        """به‌روزرسانی نسبت‌های مالی"""
        # پاک کردن داده‌های قبلی
        for item in self.ratios_table.get_children():
            self.ratios_table.delete(item)
            
        # اضافه کردن داده‌های جدید
        for ratio in data:
            self.ratios_table.insert("", "end", values=(
                ratio["name"],
                ratio["value"],
                ratio["change"],
                ratio["rank"]
            ))
            
    def update_financial_statements(self, data):
        """به‌روزرسانی صورت‌های مالی"""
        # این متد باید در کلاس‌های فرزند پیاده‌سازی شود
        pass
        
    def update_profitability_analysis(self, data):
        """به‌روزرسانی تحلیل سودآوری"""
        # پاک کردن نمودار قبلی
        self.profitability_ax.clear()
        
        # رسم نمودار جدید
        df = pd.DataFrame(data)
        self.profitability_ax.plot(df["year"], df["profit"], label="سود")
        self.profitability_ax.plot(df["year"], df["growth"], label="رشد")
        
        # تنظیمات نمودار
        self.profitability_ax.set_title("تحلیل سودآوری و رشد")
        self.profitability_ax.grid(True)
        self.profitability_ax.legend()
        
        # به‌روزرسانی نمودار
        self.profitability_canvas.draw()
        
    def update_status(self):
        """به‌روزرسانی وضعیت"""
        self.update_label.config(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")
        
    def start_auto_update(self):
        """شروع به‌روزرسانی خودکار داده‌ها"""
        def update_loop():
            while True:
                self.update_data()
                time.sleep(60)  # به‌روزرسانی هر دقیقه
                
        # اجرای به‌روزرسانی در یک نخ جداگانه
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

    def update_loop(self):
        """حلقه به‌روزرسانی خودکار"""
        while True:
            try:
                self.after(0, self.update_data)
                time.sleep(60)  # به‌روزرسانی هر 1 دقیقه
            except Exception as e:
                print(f"Error in update loop: {str(e)}")
                time.sleep(60)  # در صورت خطا، 1 دقیقه صبر کن 