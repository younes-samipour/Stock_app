"""
این ماژول پنجره اصلی برنامه را مدیریت می‌کند و شامل موارد زیر است:
- مدیریت رابط کاربری اصلی برنامه
- مدیریت تب‌های نمایش اطلاعات سهام
- مدیریت ارتباط با دیتابیس و API
- مدیریت نمایش وضعیت و کنترل‌های برنامه
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.database import DatabaseManager
from core.api_handler import StockAPI
from ui.widgets.dashboard import Dashboard
from ui.widgets.portfolio_manager import PortfolioManager
from ui.widgets.technical_analysis import TechnicalAnalysis
from ui.widgets.fundamental_analysis import FundamentalAnalysis
from ui.widgets.market_page import MarketPage
from ui.widgets.reports_page import ReportsPage
from ui.widgets.settings_page import SettingsPage
from ui.widgets.stock_manager import StockManager
from ui.widgets.watchlist_page import WatchlistPage
from ui.widgets.alerts_page import AlertsPage
from ui.widgets.download_page import DownloadPage
from datetime import datetime
import threading
import time

class MainWindow:
    def __init__(self, root):
        """
        سازنده کلاس MainWindow
        root: پنجره اصلی برنامه (Tk instance)
        """
        self.root = root
        self.setup_window()  # تنظیمات اولیه پنجره
        self.db = DatabaseManager()  # راه‌اندازی دیتابیس
        self.api = StockAPI()  # راه‌اندازی API
        self.load_stock_data()  # بارگذاری اطلاعات سهام
        self.setup_ui()  # راه‌اندازی رابط کاربری
        self.update_clock()  # شروع به‌روزرسانی ساعت
        
    def setup_window(self):
        """تنظیمات اولیه پنجره اصلی برنامه"""
        self.root.title("سامانه تحلیل بازار بورس ایران - نسخه 2.0")
        self.root.state('zoomed')  # نمایش در حالت تمام صفحه
        
        # تنظیم تم و استایل برنامه
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Treeview', rowheight=25)
        self.style.configure('Accent.TButton', foreground='white', background='#0078d7')
        self.style.configure('Filter.TButton', foreground='white', background='#4CAF50')
        
    def load_stock_data(self):
        """بارگذاری اطلاعات سهام از دیتابیس"""
        try:
            # دریافت لیست سهام از دیتابیس
            self.all_stocks = {}
            stocks = self.db.get_stock_list()
            for stock in stocks:
                self.all_stocks[stock['symbol']] = {
                    'code': stock['code'],
                    'name': stock['name'],
                    'sector': stock['sector'],
                    'market': stock['market']
                }
        except Exception as e:
            messagebox.showerror("خطای بارگذاری", 
                f"خطا در بارگذاری اطلاعات سهام از دیتابیس:\n{str(e)}")
            self.all_stocks = {}
    
    def save_stock_list_to_db(self):
        """
        ذخیره لیست سهام در دیتابیس
        این متد لیست کامل سهام را در جدول stock_list ذخیره می‌کند
        """
        try:
            # پاک کردن رکوردهای قبلی
            self.db.cursor.execute('DELETE FROM stock_list')
            # درج رکوردهای جدید
            for symbol, data in self.all_stocks.items():
                self.db.cursor.execute('''
                    INSERT INTO stock_list (symbol, name, code, sector, market, last_update) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (symbol, data['name'], data['code'], data['sector'], data['market'], datetime.now()))
            self.db.conn.commit()
        except Exception as e:
            print(f"Error saving stock list: {str(e)}")
    
    def setup_ui(self):
        """
        راه‌اندازی رابط کاربری اصلی برنامه
        شامل ایجاد فریم اصلی، تب‌ها و کنترل‌های وضعیت
        """
        # ایجاد فریم اصلی با padding مناسب
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ایجاد تب‌های اصلی
        self.main_tabs = ttk.Notebook(self.main_frame)
        self.main_tabs.pack(fill=tk.BOTH, expand=True)
        
        # ایجاد تب‌های مختلف
        self.setup_dashboard_tab()
        self.setup_market_tab()
        self.setup_portfolio_tab()
        self.setup_watchlist_tab()
        self.setup_alerts_tab()
        self.setup_reports_tab()
        self.setup_settings_tab()
        self.setup_download_tab()
        
        # ایجاد نوار وضعیت
        self.setup_status_bar()
        
    def setup_dashboard_tab(self):
        """راه‌اندازی تب داشبورد"""
        self.dashboard = Dashboard(self.main_tabs)
        self.main_tabs.add(self.dashboard, text="داشبورد")
        
    def setup_market_tab(self):
        """راه‌اندازی تب بازار"""
        self.market = MarketPage(self.main_tabs)
        self.main_tabs.add(self.market, text="بازار")
        
    def setup_portfolio_tab(self):
        """راه‌اندازی تب پورتفوی"""
        self.portfolio = PortfolioManager(self.main_tabs)
        self.main_tabs.add(self.portfolio, text="مدیریت پورتفوی")
        
    def setup_watchlist_tab(self):
        """راه‌اندازی تب دیده‌بان"""
        self.watchlist = WatchlistPage(self.main_tabs)
        self.main_tabs.add(self.watchlist, text="دیده‌بان")
        
    def setup_alerts_tab(self):
        """راه‌اندازی تب هشدارها"""
        self.alerts = AlertsPage(self.main_tabs)
        self.main_tabs.add(self.alerts, text="هشدارها")
        
    def setup_reports_tab(self):
        """راه‌اندازی تب گزارشات"""
        self.reports = ReportsPage(self.main_tabs)
        self.main_tabs.add(self.reports, text="گزارشات")
        
    def setup_settings_tab(self):
        """راه‌اندازی تب تنظیمات"""
        settings_frame = ttk.Frame(self.main_tabs)
        self.main_tabs.add(settings_frame, text="تنظیمات")
        
        # ایجاد نمونه از صفحه تنظیمات
        self.settings_page = SettingsPage(settings_frame)
        self.settings_page.pack(fill=tk.BOTH, expand=True)
        
        # تنظیم رویداد ذخیره تنظیمات
        self.settings_page.save_btn.config(command=self.on_settings_save)
        
    def on_settings_save(self):
        """رویداد ذخیره تنظیمات"""
        try:
            # ذخیره تنظیمات
            self.settings_page.save_settings()
            
            # به‌روزرسانی API با تنظیمات جدید
            self.api.load_settings()
            
            messagebox.showinfo("موفق", "تنظیمات با موفقیت ذخیره شد")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره تنظیمات: {str(e)}")
        
    def setup_status_bar(self):
        """راه‌اندازی نوار وضعیت"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        # نمایش تعداد سهام
        self.stock_count_label = ttk.Label(status_frame, text="تعداد سهام: 0")
        self.stock_count_label.pack(side=tk.LEFT, padx=5)
        
        # نمایش زمان آخرین به‌روزرسانی
        self.last_update_label = ttk.Label(status_frame, text="آخرین به‌روزرسانی: -")
        self.last_update_label.pack(side=tk.LEFT, padx=5)
        
        # نمایش وضعیت اتصال
        self.connection_label = ttk.Label(status_frame, text="وضعیت اتصال: متصل")
        self.connection_label.pack(side=tk.RIGHT, padx=5)
        
        # نمایش ساعت
        self.clock_label = ttk.Label(status_frame, text="")
        self.clock_label.pack(side=tk.RIGHT, padx=5)
        
    def update_clock(self):
        """به‌روزرسانی ساعت"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)
        self.root.after(1000, self.update_clock)

    def setup_download_tab(self):
        """راه‌اندازی تب دانلود"""
        download_frame = ttk.Frame(self.main_tabs)
        self.main_tabs.add(download_frame, text="دانلود اطلاعات")
        
        # ایجاد صفحه دانلود
        self.download_page = DownloadPage(download_frame)
        self.download_page.pack(fill="both", expand=True) 