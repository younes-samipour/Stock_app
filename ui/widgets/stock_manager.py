"""
این ماژول صفحه مدیریت سهام را مدیریت می‌کند و شامل موارد زیر است:
- مدیریت لیست سهام
- اضافه/حذف سهام
- دسته‌بندی سهام
- تنظیمات نمایش
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.database import DatabaseManager
from core.api_handler import StockAPI
from datetime import datetime
import threading
import time

class StockManager(ttk.Frame):
    def __init__(self, parent):
        """
        سازنده کلاس StockManager
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
        """راه‌اندازی رابط کاربری صفحه مدیریت سهام"""
        # ایجاد گرید برای چیدمان اجزا
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ایجاد کنترل‌های مدیریت
        self.setup_controls()
        
        # ایجاد جدول سهام
        self.setup_stock_table()
        
        # ایجاد نوار وضعیت
        self.setup_status_bar()
        
    def setup_controls(self):
        """راه‌اندازی کنترل‌های مدیریت"""
        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # دکمه‌های مدیریت
        add_btn = ttk.Button(control_frame, text="اضافه کردن", command=self.add_stock)
        add_btn.pack(side="right", padx=5)
        
        remove_btn = ttk.Button(control_frame, text="حذف", command=self.remove_stock)
        remove_btn.pack(side="right", padx=5)
        
        edit_btn = ttk.Button(control_frame, text="ویرایش", command=self.edit_stock)
        edit_btn.pack(side="right", padx=5)
        
        # جستجو
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side="right", padx=5)
        
        ttk.Label(search_frame, text="جستجو:").pack(side="right", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="right", padx=5)
        search_entry.bind("<KeyRelease>", self.on_search)
        
    def setup_stock_table(self):
        """راه‌اندازی جدول سهام"""
        # ایجاد جدول
        columns = ("نماد", "نام", "دسته‌بندی", "وضعیت", "آخرین قیمت", "تغییر", "حجم")
        self.stock_table = ttk.Treeview(self, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            self.stock_table.heading(col, text=col)
            self.stock_table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.stock_table.yview)
        self.stock_table.configure(yscrollcommand=scrollbar.set)
        
        # قرار دادن جدول و اسکرول‌بار
        self.stock_table.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        # رویداد انتخاب سطر
        self.stock_table.bind("<<TreeviewSelect>>", self.on_select)
        
    def setup_status_bar(self):
        """راه‌اندازی نوار وضعیت"""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # تعداد سهام
        self.count_label = ttk.Label(status_frame, text="تعداد سهام: 0")
        self.count_label.pack(side="right", padx=5)
        
        # زمان آخرین به‌روزرسانی
        self.update_label = ttk.Label(status_frame, text="آخرین به‌روزرسانی: -")
        self.update_label.pack(side="right", padx=5)
        
    def load_data(self):
        """بارگذاری داده‌های سهام"""
        try:
            # دریافت لیست سهام
            stocks = self.db.get_stock_list()
            
            # پاک کردن جدول
            for item in self.stock_table.get_children():
                self.stock_table.delete(item)
                
            # اضافه کردن سهام به جدول
            for stock in stocks:
                self.stock_table.insert("", "end", values=(
                    stock["symbol"],
                    stock["name"],
                    stock["category"],
                    stock["status"],
                    self.format_number(stock["last_price"]),
                    f"{stock['change']:.2f}%",
                    self.format_number(stock["volume"])
                ))
                
            # به‌روزرسانی وضعیت
            self.update_status(len(stocks))
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {str(e)}")
            
    def add_stock(self):
        """اضافه کردن سهم جدید"""
        try:
            # دریافت اطلاعات سهم
            symbol = self.get_input("نماد سهم:")
            if not symbol:
                return
                
            # بررسی وجود سهم
            if self.db.get_stock(symbol):
                messagebox.showerror("خطا", "این سهم قبلاً اضافه شده است")
                return
                
            # دریافت اطلاعات از API
            stock_info = self.api.get_stock_info(symbol)
            if not stock_info:
                messagebox.showerror("خطا", "اطلاعات سهم یافت نشد")
                return
                
            # ذخیره در دیتابیس
            self.db.add_stock({
                "symbol": symbol,
                "name": stock_info["name"],
                "category": stock_info["category"],
                "status": "فعال",
                "last_price": stock_info["last_price"],
                "change": stock_info["change"],
                "volume": stock_info["volume"]
            })
            
            # به‌روزرسانی جدول
            self.load_data()
            
            messagebox.showinfo("موفق", "سهم با موفقیت اضافه شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در اضافه کردن سهم: {str(e)}")
            
    def remove_stock(self):
        """حذف سهم"""
        try:
            # دریافت سهم انتخاب شده
            selection = self.stock_table.selection()
            if not selection:
                messagebox.showerror("خطا", "لطفاً یک سهم انتخاب کنید")
                return
                
            # دریافت نماد سهم
            symbol = self.stock_table.item(selection[0])["values"][0]
            
            # حذف از دیتابیس
            self.db.remove_stock(symbol)
            
            # به‌روزرسانی جدول
            self.load_data()
            
            messagebox.showinfo("موفق", "سهم با موفقیت حذف شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در حذف سهم: {str(e)}")
            
    def edit_stock(self):
        """ویرایش سهم"""
        try:
            # دریافت سهم انتخاب شده
            selection = self.stock_table.selection()
            if not selection:
                messagebox.showerror("خطا", "لطفاً یک سهم انتخاب کنید")
                return
                
            # دریافت اطلاعات سهم
            symbol = self.stock_table.item(selection[0])["values"][0]
            stock = self.db.get_stock(symbol)
            
            # دریافت اطلاعات جدید
            name = self.get_input("نام:", stock["name"])
            category = self.get_input("دسته‌بندی:", stock["category"])
            
            # به‌روزرسانی در دیتابیس
            self.db.update_stock(symbol, {
                "name": name,
                "category": category
            })
            
            # به‌روزرسانی جدول
            self.load_data()
            
            messagebox.showinfo("موفق", "سهم با موفقیت ویرایش شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ویرایش سهم: {str(e)}")
            
    def on_search(self, event):
        """رویداد جستجو"""
        try:
            # دریافت متن جستجو
            search_text = self.search_var.get().lower()
            
            # پاک کردن جدول
            for item in self.stock_table.get_children():
                self.stock_table.delete(item)
                
            # دریافت لیست سهام
            stocks = self.db.get_stock_list()
            
            # فیلتر کردن سهام
            filtered_stocks = [
                stock for stock in stocks
                if search_text in stock["symbol"].lower() or
                search_text in stock["name"].lower() or
                search_text in stock["category"].lower()
            ]
            
            # اضافه کردن سهام فیلتر شده به جدول
            for stock in filtered_stocks:
                self.stock_table.insert("", "end", values=(
                    stock["symbol"],
                    stock["name"],
                    stock["category"],
                    stock["status"],
                    self.format_number(stock["last_price"]),
                    f"{stock['change']:.2f}%",
                    self.format_number(stock["volume"])
                ))
                
            # به‌روزرسانی وضعیت
            self.update_status(len(filtered_stocks))
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در جستجو: {str(e)}")
            
    def on_select(self, event):
        """رویداد انتخاب سطر"""
        # این متد می‌تواند برای نمایش اطلاعات بیشتر استفاده شود
        pass
        
    def update_status(self, count):
        """به‌روزرسانی وضعیت"""
        self.count_label.config(text=f"تعداد سهام: {count}")
        self.update_label.config(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")
        
    def start_auto_update(self):
        """شروع به‌روزرسانی خودکار"""
        def update_loop():
            while True:
                self.load_data()
                time.sleep(60)  # به‌روزرسانی هر دقیقه
                
        # اجرای به‌روزرسانی در یک نخ جداگانه
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        
    def get_input(self, prompt, default=""):
        """دریافت ورودی از کاربر"""
        dialog = tk.Toplevel(self)
        dialog.title("ورودی")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text=prompt).pack(pady=5)
        
        var = tk.StringVar(value=default)
        entry = ttk.Entry(dialog, textvariable=var)
        entry.pack(pady=5)
        
        result = [None]
        
        def on_ok():
            result[0] = var.get()
            dialog.destroy()
            
        def on_cancel():
            dialog.destroy()
            
        ttk.Button(dialog, text="تایید", command=on_ok).pack(side="right", padx=5)
        ttk.Button(dialog, text="انصراف", command=on_cancel).pack(side="right", padx=5)
        
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)
        
        return result[0]
        
    def format_number(self, number):
        """فرمت‌بندی اعداد با جداکننده هزارگان"""
        try:
            return "{:,}".format(int(number))
        except:
            return str(number) 