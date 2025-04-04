"""
این ماژول صفحه هشدارها را مدیریت می‌کند و شامل موارد زیر است:
- نمایش هشدارهای فعال
- تنظیم هشدار جدید
- تاریخچه هشدارها
- مدیریت هشدارها
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.database import DatabaseManager
from core.api_handler import StockAPI
from datetime import datetime
import threading
import time

class AlertsPage(ttk.Frame):
    def __init__(self, parent):
        """
        سازنده کلاس AlertsPage
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
        """راه‌اندازی رابط کاربری صفحه هشدارها"""
        # ایجاد گرید برای چیدمان اجزا
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ایجاد کنترل‌های مدیریت
        self.setup_controls()
        
        # ایجاد تب‌های نمایش
        self.setup_tabs()
        
        # ایجاد نوار وضعیت
        self.setup_status_bar()
        
    def setup_controls(self):
        """راه‌اندازی کنترل‌های مدیریت"""
        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # دکمه‌های مدیریت
        add_btn = ttk.Button(control_frame, text="هشدار جدید", command=self.add_alert)
        add_btn.pack(side="right", padx=5)
        
        remove_btn = ttk.Button(control_frame, text="حذف", command=self.remove_alert)
        remove_btn.pack(side="right", padx=5)
        
        clear_btn = ttk.Button(control_frame, text="پاک کردن همه", command=self.clear_alerts)
        clear_btn.pack(side="right", padx=5)
        
        # جستجو
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side="right", padx=5)
        
        ttk.Label(search_frame, text="جستجو:").pack(side="right", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="right", padx=5)
        search_entry.bind("<KeyRelease>", self.on_search)
        
    def setup_tabs(self):
        """راه‌اندازی تب‌های نمایش"""
        # ایجاد تب‌ها
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # تب هشدارهای فعال
        self.active_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.active_frame, text="هشدارهای فعال")
        self.setup_active_alerts()
        
        # تب تاریخچه
        self.history_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.history_frame, text="تاریخچه")
        self.setup_history()
        
    def setup_active_alerts(self):
        """راه‌اندازی نمایش هشدارهای فعال"""
        # ایجاد جدول
        columns = ("نماد", "نام", "نوع", "قیمت", "وضعیت", "زمان")
        self.active_table = ttk.Treeview(self.active_frame, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            self.active_table.heading(col, text=col)
            self.active_table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self.active_frame, orient="vertical", command=self.active_table.yview)
        self.active_table.configure(yscrollcommand=scrollbar.set)
        
        # قرار دادن جدول و اسکرول‌بار
        self.active_table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
        # رویداد انتخاب سطر
        self.active_table.bind("<<TreeviewSelect>>", self.on_select)
        
    def setup_history(self):
        """راه‌اندازی نمایش تاریخچه"""
        # ایجاد جدول
        columns = ("نماد", "نام", "نوع", "قیمت", "وضعیت", "زمان")
        self.history_table = ttk.Treeview(self.history_frame, columns=columns, show="headings")
        
        # تنظیم ستون‌ها
        for col in columns:
            self.history_table.heading(col, text=col)
            self.history_table.column(col, width=100)
            
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(self.history_frame, orient="vertical", command=self.history_table.yview)
        self.history_table.configure(yscrollcommand=scrollbar.set)
        
        # قرار دادن جدول و اسکرول‌بار
        self.history_table.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
    def setup_status_bar(self):
        """راه‌اندازی نوار وضعیت"""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # تعداد هشدارها
        self.count_label = ttk.Label(status_frame, text="تعداد هشدارها: 0")
        self.count_label.pack(side="right", padx=5)
        
        # زمان آخرین به‌روزرسانی
        self.update_label = ttk.Label(status_frame, text="آخرین به‌روزرسانی: -")
        self.update_label.pack(side="right", padx=5)
        
    def load_data(self):
        """بارگذاری داده‌های هشدارها"""
        try:
            # دریافت هشدارهای فعال
            active_alerts = self.db.get_active_alerts()
            
            # پاک کردن جدول
            for item in self.active_table.get_children():
                self.active_table.delete(item)
                
            # اضافه کردن هشدارها به جدول
            for alert in active_alerts:
                # دریافت اطلاعات سهم
                stock = self.api.get_stock_info(alert["symbol"])
                if not stock:
                    continue
                    
                self.active_table.insert("", "end", values=(
                    alert["symbol"],
                    stock["name"],
                    alert["type"],
                    self.format_number(alert["price"]),
                    alert["status"],
                    alert["time"]
                ))
                
            # دریافت تاریخچه هشدارها
            history = self.db.get_alert_history()
            
            # پاک کردن جدول
            for item in self.history_table.get_children():
                self.history_table.delete(item)
                
            # اضافه کردن هشدارها به جدول
            for alert in history:
                # دریافت اطلاعات سهم
                stock = self.api.get_stock_info(alert["symbol"])
                if not stock:
                    continue
                    
                self.history_table.insert("", "end", values=(
                    alert["symbol"],
                    stock["name"],
                    alert["type"],
                    self.format_number(alert["price"]),
                    alert["status"],
                    alert["time"]
                ))
                
            # به‌روزرسانی وضعیت
            self.update_status(len(active_alerts))
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {str(e)}")
            
    def add_alert(self):
        """اضافه کردن هشدار جدید"""
        try:
            # دریافت اطلاعات هشدار
            symbol = self.get_input("نماد سهم:")
            if not symbol:
                return
                
            # بررسی وجود سهم
            stock = self.api.get_stock_info(symbol)
            if not stock:
                messagebox.showerror("خطا", "اطلاعات سهم یافت نشد")
                return
                
            # دریافت نوع هشدار
            alert_type = self.get_alert_type()
            if not alert_type:
                return
                
            # دریافت قیمت هشدار
            price = self.get_input("قیمت هشدار:")
            if not price:
                return
                
            try:
                price = float(price)
            except:
                messagebox.showerror("خطا", "قیمت نامعتبر است")
                return
                
            # ذخیره در دیتابیس
            self.db.add_alert({
                "symbol": symbol,
                "type": alert_type,
                "price": price,
                "status": "فعال",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # به‌روزرسانی جدول
            self.load_data()
            
            messagebox.showinfo("موفق", "هشدار با موفقیت اضافه شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در اضافه کردن هشدار: {str(e)}")
            
    def remove_alert(self):
        """حذف هشدار"""
        try:
            # دریافت هشدار انتخاب شده
            selection = self.active_table.selection()
            if not selection:
                messagebox.showerror("خطا", "لطفاً یک هشدار انتخاب کنید")
                return
                
            # دریافت اطلاعات هشدار
            alert = self.active_table.item(selection[0])["values"]
            
            # حذف از دیتابیس
            self.db.remove_alert(alert[0], alert[2], alert[3])
            
            # به‌روزرسانی جدول
            self.load_data()
            
            messagebox.showinfo("موفق", "هشدار با موفقیت حذف شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در حذف هشدار: {str(e)}")
            
    def clear_alerts(self):
        """پاک کردن همه هشدارها"""
        try:
            if messagebox.askyesno("تایید", "آیا مطمئن هستید که می‌خواهید همه هشدارها را پاک کنید؟"):
                # پاک کردن از دیتابیس
                self.db.clear_alerts()
                
                # به‌روزرسانی جدول
                self.load_data()
                
                messagebox.showinfo("موفق", "همه هشدارها با موفقیت پاک شدند")
                
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در پاک کردن هشدارها: {str(e)}")
            
    def get_alert_type(self):
        """دریافت نوع هشدار"""
        dialog = tk.Toplevel(self)
        dialog.title("نوع هشدار")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="نوع هشدار را انتخاب کنید:").pack(pady=5)
        
        var = tk.StringVar()
        
        ttk.Radiobutton(dialog, text="بالاتر از قیمت", variable=var, value="above").pack(pady=5)
        ttk.Radiobutton(dialog, text="پایین‌تر از قیمت", variable=var, value="below").pack(pady=5)
        
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
        
    def on_search(self, event):
        """رویداد جستجو"""
        try:
            # دریافت متن جستجو
            search_text = self.search_var.get().lower()
            
            # پاک کردن جدول
            for item in self.active_table.get_children():
                self.active_table.delete(item)
                
            # دریافت هشدارهای فعال
            alerts = self.db.get_active_alerts()
            
            # فیلتر کردن هشدارها
            filtered_alerts = [
                alert for alert in alerts
                if search_text in alert["symbol"].lower()
            ]
            
            # اضافه کردن هشدارهای فیلتر شده به جدول
            for alert in filtered_alerts:
                # دریافت اطلاعات سهم
                stock = self.api.get_stock_info(alert["symbol"])
                if not stock:
                    continue
                    
                self.active_table.insert("", "end", values=(
                    alert["symbol"],
                    stock["name"],
                    alert["type"],
                    self.format_number(alert["price"]),
                    alert["status"],
                    alert["time"]
                ))
                
            # به‌روزرسانی وضعیت
            self.update_status(len(filtered_alerts))
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در جستجو: {str(e)}")
            
    def on_select(self, event):
        """رویداد انتخاب سطر"""
        # این متد می‌تواند برای نمایش اطلاعات بیشتر استفاده شود
        pass
        
    def update_status(self, count):
        """به‌روزرسانی وضعیت"""
        self.count_label.config(text=f"تعداد هشدارها: {count}")
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