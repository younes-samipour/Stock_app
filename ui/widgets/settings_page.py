"""
این ماژول صفحه تنظیمات را مدیریت می‌کند و شامل موارد زیر است:
- تنظیمات عمومی برنامه
- تنظیمات API و اتصال
- تنظیمات نمایش و ظاهر
- تنظیمات امنیتی
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.database import DatabaseManager
from core.config import Config
from core.api_handler import StockAPI
import json
import os

class SettingsPage(ttk.Frame):
    def __init__(self, parent):
        """
        سازنده کلاس SettingsPage
        parent: والد ویجت (فریم اصلی)
        """
        super().__init__(parent)
        self.db = DatabaseManager()
        self.config = Config()
        self.api = StockAPI()
        
        # تنظیمات اولیه
        self.setup_ui()
        
        # بارگذاری تنظیمات
        self.load_settings()
        
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        # ایجاد فریم اصلی
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # فریم تنظیمات API
        api_frame = ttk.LabelFrame(main_frame, text="تنظیمات API")
        api_frame.pack(fill=tk.X, pady=5)
        
        # URL اطلاعات پایه
        ttk.Label(api_frame, text="URL اطلاعات پایه:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.basic_info_url = ttk.Entry(api_frame, width=50)
        self.basic_info_url.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # URL نسبت‌های مالی
        ttk.Label(api_frame, text="URL نسبت‌های مالی:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ratios_url = ttk.Entry(api_frame, width=50)
        self.ratios_url.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # URL صورت‌های مالی
        ttk.Label(api_frame, text="URL صورت‌های مالی:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.statements_url = ttk.Entry(api_frame, width=50)
        self.statements_url.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # URL تحلیل سودآوری
        ttk.Label(api_frame, text="URL تحلیل سودآوری:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.profitability_url = ttk.Entry(api_frame, width=50)
        self.profitability_url.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # دکمه ذخیره
        self.save_btn = ttk.Button(main_frame, text="ذخیره تنظیمات")
        self.save_btn.pack(pady=10)
        
        # برچسب وضعیت
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.pack(pady=5)
        
    def load_settings(self):
        """بارگذاری تنظیمات"""
        try:
            self.db.cursor.execute('SELECT * FROM settings WHERE id = 1')
            settings = self.db.cursor.fetchone()
            
            if settings:
                self.basic_info_url.insert(0, settings[1] or '')
                self.ratios_url.insert(0, settings[2] or '')
                self.statements_url.insert(0, settings[3] or '')
                self.profitability_url.insert(0, settings[4] or '')
                
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
            
    def save_settings(self):
        """ذخیره تنظیمات"""
        try:
            self.db.cursor.execute('''
                INSERT OR REPLACE INTO settings 
                (id, basic_info_url, ratios_url, statements_url, profitability_url)
                VALUES (1, ?, ?, ?, ?)
            ''', (
                self.basic_info_url.get(),
                self.ratios_url.get(),
                self.statements_url.get(),
                self.profitability_url.get()
            ))
            
            self.db.conn.commit()
            self.status_label.config(text="تنظیمات با موفقیت ذخیره شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره تنظیمات: {str(e)}")
            
    def reset_settings(self):
        """بازنشانی تنظیمات به مقادیر پیش‌فرض"""
        try:
            self.config.reset_settings()
            self.load_settings()
            messagebox.showinfo("موفق", "تنظیمات با موفقیت بازنشانی شد.")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بازنشانی تنظیمات: {str(e)}")
            
    def backup_settings(self):
        """پشتیبان‌گیری از تنظیمات"""
        try:
            # دریافت مسیر ذخیره فایل
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            
            if file_path:
                settings = self.config.get_settings()
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)
                    
                messagebox.showinfo("موفق", "پشتیبان‌گیری با موفقیت انجام شد.")
                
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در پشتیبان‌گیری: {str(e)}")
            
    def restore_settings(self):
        """بازیابی تنظیمات از فایل پشتیبان"""
        try:
            # دریافت مسیر فایل پشتیبان
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")]
            )
            
            if file_path:
                with open(file_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    
                self.config.save_settings(settings)
                self.load_settings()
                messagebox.showinfo("موفق", "بازیابی با موفقیت انجام شد.")
                
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بازیابی: {str(e)}") 