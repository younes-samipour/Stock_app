"""
این ماژول صفحه هشدارها را مدیریت می‌کند و شامل موارد زیر است:
- نمایش لیست هشدارهای فعال
- امکان تعریف هشدارهای جدید
- مدیریت هشدارها (فعال/غیرفعال کردن، ویرایش، حذف)
- نمایش تاریخچه هشدارها
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
        
        # ایجاد کنترل‌های هشدار جدید
        self.setup_new_alert_controls()
        
        # ایجاد تب‌های هشدارها و تاریخچه
        self.setup_tabs()
        
        # ایجاد نوار وضعیت
        self.setup_status_bar()
        
    def setup_new_alert_controls(self):
        """راه‌اندازی کنترل‌های تعریف هشدار جدید"""
        alert_frame = ttk.LabelFrame(self, text="تعریف هشدار جدید")
        alert_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # انتخاب سهام
        ttk.Label(alert_frame, text="نماد:").pack(side="right", padx=5)
        self.symbol_var = tk.StringVar()
        symbol_entry = ttk.Entry(alert_frame, textvariable=self.symbol_var, width=10)
        symbol_entry.pack(side="right", padx=5)
        
        # نوع هشدار
        ttk.Label(alert_frame, text="نوع هشدار:").pack(side="right", padx=5)
        self.alert_type_var = tk.StringVar()
        alert_type_combo = ttk.Combobox(alert_frame, textvariable=self.alert_type_var, width=15)
        alert_type_combo["values"] = ("تغییر قیمت", "حجم معاملات", "قیمت", "ارزش معاملات")
        alert_type_combo.pack(side="right", padx=5)
        
        # مقدار هشدار
        ttk.Label(alert_frame, text="مقدار:").pack(side="right", padx=5)
        self.value_var = tk.StringVar()
        value_entry = ttk.Entry(alert_frame, textvariable=self.value_var, width=10)
        value_entry.pack(side="right", padx=5)
        
        # دکمه اضافه کردن
        add_btn = ttk.Button(alert_frame, text="اضافه کردن", command=self.add_alert)
        add_btn.pack(side="right", padx=5)
        
    def setup_tabs(self):
        """راه‌اندازی تب‌های هشدارها و تاریخچه"""
        tabs = ttk.Notebook(self)
        tabs.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # تب هشدارهای فعال
        active_frame = ttk.Frame(tabs)
        tabs.add(active_frame, text="هشدارهای فعال")
        
        # تب تاریخچه هشدارها
        history_frame = ttk.Frame(tabs)
        tabs.add(history_frame, text="تاریخچه هشدارها")
        
        # راه‌اندازی جداول
        self.setup_active_alerts_table(active_frame)
        self.setup_history_table(history_frame)
        
    def setup_active_alerts_table(self, parent):
        """راه‌اندازی جدول هشدارهای فعال"""
        # ایجاد فریم برای جدول و اسکرول‌بار
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ایجاد اسکرول‌بار عمودی
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        # ایجاد جدول
        self.active_alerts_table = ttk.Treeview(
            table_frame,
            columns=("symbol", "type", "value", "status", "created_at"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.active_alerts_table.yview)
        
        # تنظیم ستون‌ها
        self.active_alerts_table.heading("symbol", text="نماد")
        self.active_alerts_table.heading("type", text="نوع هشدار")
        self.active_alerts_table.heading("value", text="مقدار")
        self.active_alerts_table.heading("status", text="وضعیت")
        self.active_alerts_table.heading("created_at", text="تاریخ ایجاد")
        
        # تنظیم عرض ستون‌ها
        self.active_alerts_table.column("symbol", width=80)
        self.active_alerts_table.column("type", width=120)
        self.active_alerts_table.column("value", width=100)
        self.active_alerts_table.column("status", width=80)
        self.active_alerts_table.column("created_at", width=150)
        
        # قرار دادن جدول در فریم
        self.active_alerts_table.pack(fill=tk.BOTH, expand=True)
        
        # اضافه کردن منوی راست کلیک
        self.setup_active_alerts_context_menu()
        
    def setup_history_table(self, parent):
        """راه‌اندازی جدول تاریخچه هشدارها"""
        # ایجاد فریم برای جدول و اسکرول‌بار
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ایجاد اسکرول‌بار عمودی
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        # ایجاد جدول
        self.history_table = ttk.Treeview(
            table_frame,
            columns=("symbol", "type", "value", "triggered_at", "status"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.history_table.yview)
        
        # تنظیم ستون‌ها
        self.history_table.heading("symbol", text="نماد")
        self.history_table.heading("type", text="نوع هشدار")
        self.history_table.heading("value", text="مقدار")
        self.history_table.heading("triggered_at", text="زمان فعال شدن")
        self.history_table.heading("status", text="وضعیت")
        
        # تنظیم عرض ستون‌ها
        self.history_table.column("symbol", width=80)
        self.history_table.column("type", width=120)
        self.history_table.column("value", width=100)
        self.history_table.column("triggered_at", width=150)
        self.history_table.column("status", width=80)
        
        # قرار دادن جدول در فریم
        self.history_table.pack(fill=tk.BOTH, expand=True)
        
    def setup_active_alerts_context_menu(self):
        """راه‌اندازی منوی راست کلیک برای هشدارهای فعال"""
        self.active_alerts_menu = tk.Menu(self, tearoff=0)
        self.active_alerts_menu.add_command(label="غیرفعال کردن", command=self.deactivate_alert)
        self.active_alerts_menu.add_command(label="ویرایش", command=self.edit_alert)
        self.active_alerts_menu.add_command(label="حذف", command=self.delete_alert)
        
        # اتصال منو به جدول
        self.active_alerts_table.bind("<Button-3>", self.show_active_alerts_menu)
        
    def setup_status_bar(self):
        """راه‌اندازی نوار وضعیت"""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # تعداد هشدارهای فعال
        self.active_count_label = ttk.Label(status_frame, text="تعداد هشدارهای فعال: 0")
        self.active_count_label.pack(side="right", padx=5)
        
        # زمان آخرین به‌روزرسانی
        self.update_label = ttk.Label(status_frame, text="آخرین به‌روزرسانی: -")
        self.update_label.pack(side="right", padx=5)
        
    def load_data(self):
        """بارگذاری داده‌های هشدارها"""
        try:
            # دریافت هشدارهای فعال از دیتابیس
            active_alerts = self.db.get_active_alerts()
            
            # پاک کردن جدول هشدارهای فعال
            for item in self.active_alerts_table.get_children():
                self.active_alerts_table.delete(item)
            
            # پر کردن جدول هشدارهای فعال
            for alert in active_alerts:
                self.active_alerts_table.insert("", "end", values=(
                    alert["symbol"],
                    alert["type"],
                    self.format_value(alert["value"], alert["type"]),
                    "فعال",
                    alert["created_at"]
                ))
            
            # دریافت تاریخچه هشدارها از دیتابیس
            history = self.db.get_alert_history()
            
            # پاک کردن جدول تاریخچه
            for item in self.history_table.get_children():
                self.history_table.delete(item)
            
            # پر کردن جدول تاریخچه
            for alert in history:
                self.history_table.insert("", "end", values=(
                    alert["symbol"],
                    alert["type"],
                    self.format_value(alert["value"], alert["type"]),
                    alert["triggered_at"],
                    alert["status"]
                ))
            
            # به‌روزرسانی وضعیت
            self.active_count_label.config(text=f"تعداد هشدارهای فعال: {len(active_alerts)}")
            self.update_label.config(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {str(e)}")
            
    def add_alert(self):
        """اضافه کردن هشدار جدید"""
        try:
            symbol = self.symbol_var.get().strip()
            alert_type = self.alert_type_var.get()
            value = self.value_var.get().strip()
            
            # اعتبارسنجی ورودی‌ها
            if not symbol or not alert_type or not value:
                messagebox.showerror("خطا", "لطفاً تمام فیلدها را پر کنید")
                return
                
            # اضافه کردن هشدار به دیتابیس
            self.db.add_alert(symbol, alert_type, value)
            
            # پاک کردن فیلدها
            self.symbol_var.set("")
            self.alert_type_var.set("")
            self.value_var.set("")
            
            # به‌روزرسانی داده‌ها
            self.load_data()
            
            messagebox.showinfo("موفق", "هشدار با موفقیت اضافه شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در اضافه کردن هشدار: {str(e)}")
            
    def deactivate_alert(self):
        """غیرفعال کردن هشدار"""
        selected = self.active_alerts_table.selection()
        if selected:
            alert_id = self.active_alerts_table.item(selected[0])["values"][0]
            try:
                self.db.deactivate_alert(alert_id)
                self.load_data()
                messagebox.showinfo("موفق", "هشدار با موفقیت غیرفعال شد")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در غیرفعال کردن هشدار: {str(e)}")
                
    def edit_alert(self):
        """ویرایش هشدار"""
        selected = self.active_alerts_table.selection()
        if selected:
            alert_id = self.active_alerts_table.item(selected[0])["values"][0]
            # TODO: نمایش پنجره ویرایش هشدار
            
    def delete_alert(self):
        """حذف هشدار"""
        selected = self.active_alerts_table.selection()
        if selected:
            alert_id = self.active_alerts_table.item(selected[0])["values"][0]
            try:
                self.db.delete_alert(alert_id)
                self.load_data()
                messagebox.showinfo("موفق", "هشدار با موفقیت حذف شد")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در حذف هشدار: {str(e)}")
                
    def show_active_alerts_menu(self, event):
        """نمایش منوی راست کلیک برای هشدارهای فعال"""
        item = self.active_alerts_table.identify_row(event.y)
        if item:
            self.active_alerts_table.selection_set(item)
            self.active_alerts_menu.post(event.x_root, event.y_root)
            
    def start_auto_update(self):
        """شروع به‌روزرسانی خودکار"""
        def update_loop():
            while True:
                self.load_data()
                time.sleep(60)  # به‌روزرسانی هر دقیقه
                
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        
    def format_value(self, value, alert_type):
        """فرمت‌بندی مقدار هشدار"""
        try:
            if alert_type == "تغییر قیمت":
                return f"{float(value):+.2f}%"
            elif alert_type in ("حجم معاملات", "ارزش معاملات"):
                return "{:,}".format(int(value))
            elif alert_type == "قیمت":
                return "{:,}".format(int(value))
            else:
                return str(value)
        except:
            return str(value) 