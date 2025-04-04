"""
این ماژول صفحه لیست پیگیری را مدیریت می‌کند و شامل موارد زیر است:
- لیست سهام مورد علاقه
- تنظیم هشدار قیمت
- نمایش تغییرات
- مدیریت لیست پیگیری
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.database import DatabaseManager
from core.api_handler import StockAPI
from datetime import datetime
import threading
import time

class WatchlistPage(ttk.Frame):
    def __init__(self, parent):
        """
        سازنده کلاس WatchlistPage
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
        """راه‌اندازی رابط کاربری صفحه لیست پیگیری"""
        # ایجاد گرید برای چیدمان اجزا
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ایجاد کنترل‌های مدیریت
        self.setup_controls()
        
        # ایجاد جدول سهام
        self.setup_watchlist_table()
        
        # ایجاد نوار وضعیت
        self.setup_status_bar()
        
    def setup_controls(self):
        """راه‌اندازی کنترل‌های مدیریت"""
        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # دکمه‌های مدیریت
        add_btn = ttk.Button(control_frame, text="اضافه کردن", command=self.add_to_watchlist)
        add_btn.pack(side="right", padx=5)
        
        remove_btn = ttk.Button(control_frame, text="حذف", command=self.remove_from_watchlist)
        remove_btn.pack(side="right", padx=5)
        
        alert_btn = ttk.Button(control_frame, text="تنظیم هشدار", command=self.set_alert)
        alert_btn.pack(side="right", padx=5)
        
        # جستجو
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side="right", padx=5)
        
        ttk.Label(search_frame, text="جستجو:").pack(side="right", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="right", padx=5)
        search_entry.bind("<KeyRelease>", self.on_search)
        
    def setup_watchlist_table(self):
        """راه‌اندازی جدول لیست پیگیری"""
        # ایجاد جدول
        columns = ("نماد", "نام", "قیمت فعلی", "تغییر", "هشدار", "وضعیت هشدار")
        self.watchlist_table = ttk.Treeview(self, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            self.watchlist_table.heading(col, text=col)
            self.watchlist_table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.watchlist_table.yview)
        self.watchlist_table.configure(yscrollcommand=scrollbar.set)
        
        # قرار دادن جدول و اسکرول‌بار
        self.watchlist_table.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        # رویداد انتخاب سطر
        self.watchlist_table.bind("<<TreeviewSelect>>", self.on_select)
        
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
        """بارگذاری داده‌های لیست پیگیری"""
        try:
            # دریافت لیست پیگیری
            watchlist = self.db.get_watchlist()
            
            # پاک کردن جدول
            for item in self.watchlist_table.get_children():
                self.watchlist_table.delete(item)
                
            # اضافه کردن سهام به جدول
            for item in watchlist:
                # دریافت اطلاعات سهم
                stock = self.api.get_stock_info(item["symbol"])
                if not stock:
                    continue
                    
                # بررسی وضعیت هشدار
                alert_status = "فعال" if self.check_alert(stock, item) else "غیرفعال"
                
                self.watchlist_table.insert("", "end", values=(
                    item["symbol"],
                    stock["name"],
                    self.format_number(stock["last_price"]),
                    f"{stock['change']:.2f}%",
                    self.format_alert(item["alert"]),
                    alert_status
                ))
                
            # به‌روزرسانی وضعیت
            self.update_status(len(watchlist))
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {str(e)}")
            
    def add_to_watchlist(self):
        """اضافه کردن سهم به لیست پیگیری"""
        try:
            # دریافت نماد سهم
            symbol = self.get_input("نماد سهم:")
            if not symbol:
                return
                
            # بررسی وجود سهم در لیست پیگیری
            if self.db.get_watchlist_item(symbol):
                messagebox.showerror("خطا", "این سهم قبلاً به لیست پیگیری اضافه شده است")
                return
                
            # بررسی وجود سهم
            stock = self.api.get_stock_info(symbol)
            if not stock:
                messagebox.showerror("خطا", "اطلاعات سهم یافت نشد")
                return
                
            # ذخیره در دیتابیس
            self.db.add_to_watchlist({
                "symbol": symbol,
                "alert": None
            })
            
            # به‌روزرسانی جدول
            self.load_data()
            
            messagebox.showinfo("موفق", "سهم با موفقیت به لیست پیگیری اضافه شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در اضافه کردن سهم: {str(e)}")
            
    def remove_from_watchlist(self):
        """حذف سهم از لیست پیگیری"""
        try:
            # دریافت سهم انتخاب شده
            selection = self.watchlist_table.selection()
            if not selection:
                messagebox.showerror("خطا", "لطفاً یک سهم انتخاب کنید")
                return
                
            # دریافت نماد سهم
            symbol = self.watchlist_table.item(selection[0])["values"][0]
            
            # حذف از دیتابیس
            self.db.remove_from_watchlist(symbol)
            
            # به‌روزرسانی جدول
            self.load_data()
            
            messagebox.showinfo("موفق", "سهم با موفقیت از لیست پیگیری حذف شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در حذف سهم: {str(e)}")
            
    def set_alert(self):
        """تنظیم هشدار قیمت"""
        try:
            # دریافت سهم انتخاب شده
            selection = self.watchlist_table.selection()
            if not selection:
                messagebox.showerror("خطا", "لطفاً یک سهم انتخاب کنید")
                return
                
            # دریافت نماد سهم
            symbol = self.watchlist_table.item(selection[0])["values"][0]
            
            # دریافت قیمت هشدار
            price = self.get_input("قیمت هشدار:")
            if not price:
                return
                
            try:
                price = float(price)
            except:
                messagebox.showerror("خطا", "قیمت نامعتبر است")
                return
                
            # به‌روزرسانی در دیتابیس
            self.db.update_watchlist_alert(symbol, price)
            
            # به‌روزرسانی جدول
            self.load_data()
            
            messagebox.showinfo("موفق", "هشدار با موفقیت تنظیم شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در تنظیم هشدار: {str(e)}")
            
    def check_alert(self, stock, watchlist_item):
        """بررسی وضعیت هشدار"""
        if not watchlist_item["alert"]:
            return False
            
        current_price = stock["last_price"]
        alert_price = watchlist_item["alert"]
        
        return current_price >= alert_price
        
    def on_search(self, event):
        """رویداد جستجو"""
        try:
            # دریافت متن جستجو
            search_text = self.search_var.get().lower()
            
            # پاک کردن جدول
            for item in self.watchlist_table.get_children():
                self.watchlist_table.delete(item)
                
            # دریافت لیست پیگیری
            watchlist = self.db.get_watchlist()
            
            # فیلتر کردن سهام
            filtered_items = [
                item for item in watchlist
                if search_text in item["symbol"].lower()
            ]
            
            # اضافه کردن سهام فیلتر شده به جدول
            for item in filtered_items:
                # دریافت اطلاعات سهم
                stock = self.api.get_stock_info(item["symbol"])
                if not stock:
                    continue
                    
                # بررسی وضعیت هشدار
                alert_status = "فعال" if self.check_alert(stock, item) else "غیرفعال"
                
                self.watchlist_table.insert("", "end", values=(
                    item["symbol"],
                    stock["name"],
                    self.format_number(stock["last_price"]),
                    f"{stock['change']:.2f}%",
                    self.format_alert(item["alert"]),
                    alert_status
                ))
                
            # به‌روزرسانی وضعیت
            self.update_status(len(filtered_items))
            
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
            
    def format_alert(self, alert):
        """فرمت‌بندی هشدار"""
        if not alert:
            return "-"
        return self.format_number(alert) 