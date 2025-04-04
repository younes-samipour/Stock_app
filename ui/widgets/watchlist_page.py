"""
این ماژول صفحه دیده‌بان را مدیریت می‌کند و شامل موارد زیر است:
- نمایش لیست سهام دیده‌بان شده
- نمایش تغییرات قیمت و حجم معاملات
- امکان حذف سهام از دیده‌بان
- نمایش هشدارها برای تغییرات قیمت
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
        self.master = parent.winfo_toplevel()  # Store the master window reference
        
        # تنظیمات اولیه
        self.setup_ui()
        
        # بارگذاری داده‌ها
        self.load_data()
        
        # شروع به‌روزرسانی خودکار
        self.start_auto_update()
        
    def setup_ui(self):
        """راه‌اندازی رابط کاربری صفحه دیده‌بان"""
        # ایجاد گرید برای چیدمان اجزا
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ایجاد کنترل‌های هشدار
        self.setup_alert_controls()
        
        # ایجاد جدول سهام
        self.setup_stock_table()
        
        # ایجاد نوار وضعیت
        self.setup_status_bar()
        
    def setup_alert_controls(self):
        """راه‌اندازی کنترل‌های هشدار"""
        alert_frame = ttk.LabelFrame(self, text="تنظیمات هشدار")
        alert_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # حد تغییر قیمت
        ttk.Label(alert_frame, text="حد تغییر قیمت (%):").pack(side="right", padx=5)
        self.price_alert_var = tk.StringVar()
        self.price_alert_var.set("5")
        price_alert_entry = ttk.Entry(alert_frame, textvariable=self.price_alert_var, width=5)
        price_alert_entry.pack(side="right", padx=5)
        
        # حد حجم معاملات
        ttk.Label(alert_frame, text="حد حجم معاملات:").pack(side="right", padx=5)
        self.volume_alert_var = tk.StringVar()
        self.volume_alert_var.set("1000000")
        volume_alert_entry = ttk.Entry(alert_frame, textvariable=self.volume_alert_var, width=10)
        volume_alert_entry.pack(side="right", padx=5)
        
        # فعال/غیرفعال کردن هشدارها
        self.alert_enabled_var = tk.BooleanVar()
        self.alert_enabled_var.set(True)
        alert_check = ttk.Checkbutton(alert_frame, text="فعال کردن هشدارها", variable=self.alert_enabled_var)
        alert_check.pack(side="right", padx=5)
        
    def setup_stock_table(self):
        """راه‌اندازی جدول سهام"""
        # ایجاد فریم برای جدول و اسکرول‌بار
        table_frame = ttk.Frame(self)
        table_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # ایجاد اسکرول‌بار عمودی
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # ایجاد جدول
        self.stock_table = ttk.Treeview(
            table_frame,
            columns=("symbol", "name", "last_price", "close_price", "change", "volume", "value", "count", "min_price", "max_price", "alert"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.stock_table.yview)
        
        # تنظیم ستون‌ها
        self.stock_table.heading("symbol", text="نماد")
        self.stock_table.heading("name", text="نام شرکت")
        self.stock_table.heading("last_price", text="آخرین قیمت")
        self.stock_table.heading("close_price", text="قیمت پایانی")
        self.stock_table.heading("change", text="تغییر")
        self.stock_table.heading("volume", text="حجم")
        self.stock_table.heading("value", text="ارزش")
        self.stock_table.heading("count", text="تعداد")
        self.stock_table.heading("min_price", text="کمترین")
        self.stock_table.heading("max_price", text="بیشترین")
        self.stock_table.heading("alert", text="وضعیت")
        
        # تنظیم عرض ستون‌ها
        self.stock_table.column("symbol", width=80)
        self.stock_table.column("name", width=200)
        self.stock_table.column("last_price", width=100)
        self.stock_table.column("close_price", width=100)
        self.stock_table.column("change", width=80)
        self.stock_table.column("volume", width=100)
        self.stock_table.column("value", width=120)
        self.stock_table.column("count", width=80)
        self.stock_table.column("min_price", width=100)
        self.stock_table.column("max_price", width=100)
        self.stock_table.column("alert", width=100)
        
        # قرار دادن جدول در فریم
        self.stock_table.grid(row=0, column=0, sticky="nsew")
        
        # تنظیم رنگ‌ها برای تغییرات قیمت
        self.stock_table.tag_configure("increase", foreground="green")
        self.stock_table.tag_configure("decrease", foreground="red")
        self.stock_table.tag_configure("alert", background="yellow")
        
        # اضافه کردن منوی راست کلیک
        self.setup_context_menu()
        
    def setup_context_menu(self):
        """راه‌اندازی منوی راست کلیک"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="حذف از دیده‌بان", command=self.remove_from_watchlist)
        
        # اتصال منو به جدول
        self.stock_table.bind("<Button-3>", self.show_context_menu)
        
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
        """بارگذاری داده‌های سهام دیده‌بان"""
        try:
            # دریافت لیست سهام دیده‌بان از دیتابیس
            watchlist = self.db.get_watchlist()
            
            # به‌روزرسانی UI در thread اصلی
            self.master.after(0, self.update_stock_table, watchlist)
            
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {str(e)}"))
            
    def update_stock_table(self, watchlist):
        """به‌روزرسانی جدول سهام در thread اصلی"""
        try:
            # پاک کردن جدول
            for item in self.stock_table.get_children():
                self.stock_table.delete(item)
            
            # پر کردن جدول
            for stock in watchlist:
                self.stock_table.insert("", "end", values=(
                    stock["symbol"],
                    stock["name"],
                    self.format_number(stock["last_price"]),
                    self.format_number(stock["close_price"]),
                    self.format_change(stock["change"]),
                    self.format_number(stock["volume"]),
                    self.format_number(stock["value"]),
                    self.format_number(stock["count"]),
                    self.format_number(stock["min_price"]),
                    self.format_number(stock["max_price"]),
                    self.check_alerts(stock)
                ), tags=("increase" if stock["change"] > 0 else "decrease" if stock["change"] < 0 else ""))
            
            # به‌روزرسانی وضعیت
            self.count_label.config(text=f"تعداد سهام: {len(watchlist)}")
            self.update_label.config(text=f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("خطا", f"خطا در به‌روزرسانی جدول: {str(e)}"))
            
    def check_alerts(self, stock):
        """بررسی هشدارها برای یک سهم"""
        if not self.alert_enabled_var.get():
            return ""
            
        alerts = []
        
        # بررسی تغییر قیمت
        try:
            price_alert = float(self.price_alert_var.get())
            if abs(stock["change"]) >= price_alert:
                alerts.append(f"تغییر قیمت {abs(stock['change'])}%")
        except:
            pass
            
        # بررسی حجم معاملات
        try:
            volume_alert = float(self.volume_alert_var.get())
            if stock["volume"] >= volume_alert:
                alerts.append(f"حجم {self.format_number(stock['volume'])}")
        except:
            pass
            
        return "، ".join(alerts) if alerts else ""
        
    def show_context_menu(self, event):
        """نمایش منوی راست کلیک"""
        item = self.stock_table.identify_row(event.y)
        if item:
            self.stock_table.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def remove_from_watchlist(self):
        """حذف سهام از دیده‌بان"""
        selected = self.stock_table.selection()
        if selected:
            symbol = self.stock_table.item(selected[0])["values"][0]
            try:
                self.db.remove_from_watchlist(symbol)
                self.load_data()
                messagebox.showinfo("موفق", f"سهام {symbol} از دیده‌بان حذف شد")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در حذف از دیده‌بان: {str(e)}")
                
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