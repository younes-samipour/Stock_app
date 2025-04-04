"""
این ماژول صفحه مدیریت پورتفوی را مدیریت می‌کند و شامل موارد زیر است:
- نمایش لیست سهام موجود در پورتفوی
- امکان خرید و فروش سهام
- نمایش سود/زیان هر سهم
- نمایش تخصیص دارایی
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.database import DatabaseManager
from core.api_handler import StockAPI
from datetime import datetime
import threading
import time

class PortfolioManager(ttk.Frame):
    def __init__(self, parent):
        """
        سازنده کلاس PortfolioManager
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
        """راه‌اندازی رابط کاربری صفحه مدیریت پورتفوی"""
        # ایجاد گرید برای چیدمان اجزا
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ایجاد خلاصه وضعیت
        self.setup_summary()
        
        # ایجاد تب‌های اطلاعات
        self.setup_tabs()
        
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
        
    def setup_tabs(self):
        """راه‌اندازی تب‌های اطلاعات"""
        # ایجاد نوت‌بوک برای تب‌ها
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # ایجاد تب لیست سهام
        self.stocks_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.stocks_tab, text="لیست سهام")
        self.setup_stocks_tab()
        
        # ایجاد تب خرید و فروش
        self.trade_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.trade_tab, text="خرید و فروش")
        self.setup_trade_tab()
        
        # ایجاد تب تخصیص دارایی
        self.allocation_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.allocation_tab, text="تخصیص دارایی")
        self.setup_allocation_tab()
        
    def setup_stocks_tab(self):
        """راه‌اندازی تب لیست سهام"""
        # ایجاد جدول سهام
        columns = ("نماد", "تعداد", "قیمت میانگین", "قیمت فعلی", "ارزش", "سود/زیان", "بازده")
        self.stocks_table = ttk.Treeview(self.stocks_tab, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            self.stocks_table.heading(col, text=col)
            self.stocks_table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self.stocks_tab, orient="vertical", command=self.stocks_table.yview)
        self.stocks_table.configure(yscrollcommand=scrollbar.set)
        
        # چیدمان جدول و اسکرول‌بار
        self.stocks_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def setup_trade_tab(self):
        """راه‌اندازی تب خرید و فروش"""
        # ایجاد فریم برای فرم خرید و فروش
        form_frame = ttk.LabelFrame(self.trade_tab, text="فرم خرید و فروش")
        form_frame.pack(padx=5, pady=5, fill="x")
        
        # انتخاب نوع معامله
        ttk.Label(form_frame, text="نوع معامله:").grid(row=0, column=0, padx=5, pady=5)
        self.trade_type_var = tk.StringVar()
        trade_type_combo = ttk.Combobox(form_frame, textvariable=self.trade_type_var)
        trade_type_combo["values"] = ("خرید", "فروش")
        trade_type_combo.set("خرید")
        trade_type_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # انتخاب نماد
        ttk.Label(form_frame, text="نماد:").grid(row=1, column=0, padx=5, pady=5)
        self.symbol_var = tk.StringVar()
        symbol_entry = ttk.Entry(form_frame, textvariable=self.symbol_var)
        symbol_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # تعداد سهام
        ttk.Label(form_frame, text="تعداد:").grid(row=2, column=0, padx=5, pady=5)
        self.quantity_var = tk.StringVar()
        quantity_entry = ttk.Entry(form_frame, textvariable=self.quantity_var)
        quantity_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # قیمت
        ttk.Label(form_frame, text="قیمت:").grid(row=3, column=0, padx=5, pady=5)
        self.price_var = tk.StringVar()
        price_entry = ttk.Entry(form_frame, textvariable=self.price_var)
        price_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # دکمه ثبت معامله
        submit_btn = ttk.Button(form_frame, text="ثبت معامله", command=self.submit_trade)
        submit_btn.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
    def setup_allocation_tab(self):
        """راه‌اندازی تب تخصیص دارایی"""
        # ایجاد جدول تخصیص دارایی
        columns = ("نماد", "ارزش", "درصد")
        self.allocation_table = ttk.Treeview(self.allocation_tab, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            self.allocation_table.heading(col, text=col)
            self.allocation_table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self.allocation_tab, orient="vertical", command=self.allocation_table.yview)
        self.allocation_table.configure(yscrollcommand=scrollbar.set)
        
        # قرار دادن جدول و اسکرول‌بار
        self.allocation_table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
    def setup_status_bar(self):
        """راه‌اندازی نوار وضعیت"""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # زمان آخرین به‌روزرسانی
        self.update_label = ttk.Label(status_frame, text="آخرین به‌روزرسانی: -")
        self.update_label.pack(side="right", padx=5)
        
    def load_data(self):
        """بارگذاری داده‌های پورتفوی"""
        try:
            # دریافت اطلاعات از دیتابیس
            self.db.cursor.execute('''
                SELECT 
                    symbol,
                    quantity,
                    avg_price,
                    total_value,
                    last_update
                FROM portfolio
            ''')
            rows = self.db.cursor.fetchall()
            
            # تبدیل به لیست دیکشنری
            data = []
            for row in rows:
                symbol = row[0]
                quantity = row[1]
                avg_price = row[2]
                total_value = row[3]
                
                # دریافت قیمت فعلی
                current_price = self.api.get_current_price(symbol)
                if current_price:
                    profit_loss = (current_price - avg_price) * quantity
                    profit_loss_percent = (profit_loss / (avg_price * quantity)) * 100
                else:
                    current_price = 0
                    profit_loss = 0
                    profit_loss_percent = 0
                
                data.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'avg_price': avg_price,
                    'current_price': current_price,
                    'total_value': total_value,
                    'profit_loss': profit_loss,
                    'profit_loss_percent': profit_loss_percent
                })
            
            # به‌روزرسانی جداول
            self.update_stocks_table(data)
            self.update_allocation_table(data)
            
            # به‌روزرسانی خلاصه وضعیت
            summary = self.get_portfolio_summary()
            self.update_summary(summary)
            
        except Exception as e:
            print(f"Error loading portfolio data: {str(e)}")
            
    def update_summary(self, data):
        """به‌روزرسانی خلاصه وضعیت"""
        self.total_value_label.config(text=self.format_number(data["total_value"]))
        self.total_profit_label.config(text=self.format_number(data["total_profit"]))
        self.total_return_label.config(text=f"{data['total_return']:.2f}%")
        self.stocks_count_label.config(text=str(data["stocks_count"]))
        
    def update_stocks_table(self, data):
        """به‌روزرسانی جدول سهام"""
        # پاک کردن داده‌های قبلی
        for item in self.stocks_table.get_children():
            self.stocks_table.delete(item)
            
        # اضافه کردن داده‌های جدید
        for item in data:
            self.stocks_table.insert("", "end", values=(
                item["symbol"],
                self.format_number(item["quantity"]),
                self.format_number(item["avg_price"]),
                self.format_number(item["current_price"]),
                self.format_number(item["total_value"]),
                self.format_number(item["profit_loss"]),
                f"{item['profit_loss_percent']:.2f}%"
            ))
            
    def update_allocation_table(self, data):
        """به‌روزرسانی جدول تخصیص دارایی"""
        # پاک کردن داده‌های قبلی
        for item in self.allocation_table.get_children():
            self.allocation_table.delete(item)
            
        # اضافه کردن داده‌های جدید
        for item in data:
            self.allocation_table.insert("", "end", values=(
                item["symbol"],
                self.format_number(item["total_value"]),
                f"{item['profit_loss_percent']:.2f}%"
            ))
            
    def submit_trade(self):
        """ثبت معامله جدید"""
        try:
            # دریافت اطلاعات از فرم
            symbol = self.symbol_var.get()
            quantity = int(self.quantity_var.get())
            price = float(self.price_var.get())
            
            # محاسبه ارزش کل
            total_value = quantity * price
            
            # بررسی وجود سهم در پورتفوی
            self.db.cursor.execute('SELECT quantity, avg_price FROM portfolio WHERE symbol = ?', (symbol,))
            row = self.db.cursor.fetchone()
            
            if row:
                # به‌روزرسانی سهم موجود
                old_quantity = row[0]
                old_avg_price = row[1]
                new_quantity = old_quantity + quantity
                new_avg_price = ((old_quantity * old_avg_price) + total_value) / new_quantity
                
                self.db.cursor.execute('''
                    UPDATE portfolio 
                    SET quantity = ?, avg_price = ?, total_value = ?, last_update = ?
                    WHERE symbol = ?
                ''', (new_quantity, new_avg_price, new_quantity * new_avg_price, 
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S'), symbol))
            else:
                # اضافه کردن سهم جدید
                self.db.cursor.execute('''
                    INSERT INTO portfolio (symbol, quantity, avg_price, total_value, last_update)
                    VALUES (?, ?, ?, ?, ?)
                ''', (symbol, quantity, price, total_value, 
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # ذخیره تغییرات
            self.db.conn.commit()
            
            # به‌روزرسانی داده‌ها
            self.load_data()
            
            # پاک کردن فرم
            self.symbol_var.set('')
            self.quantity_var.set('')
            self.price_var.set('')
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ثبت معامله: {str(e)}")
            
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
        """فرمت‌بندی اعداد با جداکننده هزارگان"""
        try:
            return "{:,}".format(int(number))
        except:
            return str(number) 