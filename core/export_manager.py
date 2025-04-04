"""
این ماژول مدیریت صدور و ذخیره داده‌ها را بر عهده دارد.
این ماژول امکانات زیر را فراهم می‌کند:
- صدور داده‌ها در فرمت‌های مختلف
- ذخیره نمودارها و گزارش‌ها
- تبدیل فرمت داده‌ها
- فشرده‌سازی فایل‌های خروجی
"""

import pandas as pd
import json
import csv
import xlsxwriter
from datetime import datetime
import os
import zipfile
from .exceptions import FileError
from .constants import FILE_PATHS

class ExportManager:
    def __init__(self):
        """
        سازنده کلاس ExportManager
        راه‌اندازی مدیریت صدور با تنظیمات پایه
        """
        self.export_dir = FILE_PATHS['export']
        
        # ایجاد دایرکتوری صدور اگر وجود نداشته باشد
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_to_csv(self, data, filename, encoding='utf-8'):
        """
        صدور داده‌ها در فرمت CSV
        data: دیتافریم یا دیکشنری داده‌ها
        filename: نام فایل خروجی
        encoding: کدگذاری فایل
        return: مسیر فایل ایجاد شده
        """
        try:
            filepath = os.path.join(self.export_dir, filename)
            
            if isinstance(data, pd.DataFrame):
                data.to_csv(filepath, encoding=encoding, index=True)
            else:
                with open(filepath, 'w', encoding=encoding, newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                    
            return filepath
            
        except Exception as e:
            raise FileError(f"خطا در صدور CSV: {str(e)}", filename)
    
    def export_to_excel(self, data, filename):
        """
        صدور داده‌ها در فرمت Excel
        data: دیتافریم یا دیکشنری داده‌ها
        filename: نام فایل خروجی
        return: مسیر فایل ایجاد شده
        """
        try:
            filepath = os.path.join(self.export_dir, filename)
            
            if isinstance(data, pd.DataFrame):
                writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
                data.to_excel(writer, sheet_name='Sheet1', index=True)
                
                # تنظیم عرض ستون‌ها
                worksheet = writer.sheets['Sheet1']
                for i, col in enumerate(data.columns):
                    max_length = max(
                        data[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    worksheet.set_column(i+1, i+1, max_length + 2)
                
                writer.close()
            else:
                df = pd.DataFrame(data)
                df.to_excel(filepath, index=False)
                
            return filepath
            
        except Exception as e:
            raise FileError(f"خطا در صدور Excel: {str(e)}", filename)
    
    def export_to_json(self, data, filename, encoding='utf-8'):
        """
        صدور داده‌ها در فرمت JSON
        data: دیکشنری یا لیست داده‌ها
        filename: نام فایل خروجی
        encoding: کدگذاری فایل
        return: مسیر فایل ایجاد شده
        """
        try:
            filepath = os.path.join(self.export_dir, filename)
            
            with open(filepath, 'w', encoding=encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            return filepath
            
        except Exception as e:
            raise FileError(f"خطا در صدور JSON: {str(e)}", filename)
    
    def export_chart(self, fig, filename):
        """
        صدور نمودار در فرمت تصویری
        fig: شیء نمودار
        filename: نام فایل خروجی
        return: مسیر فایل ایجاد شده
        """
        try:
            filepath = os.path.join(self.export_dir, filename)
            
            fig.savefig(
                filepath,
                dpi=300,
                bbox_inches='tight',
                pad_inches=0.1
            )
            
            return filepath
            
        except Exception as e:
            raise FileError(f"خطا در صدور نمودار: {str(e)}", filename)
    
    def create_zip_archive(self, files, archive_name):
        """
        ایجاد آرشیو فشرده از فایل‌ها
        files: لیست مسیر فایل‌ها
        archive_name: نام فایل آرشیو
        return: مسیر فایل آرشیو
        """
        try:
            archive_path = os.path.join(self.export_dir, archive_name)
            
            with zipfile.ZipFile(archive_path, 'w') as zf:
                for file in files:
                    if os.path.exists(file):
                        zf.write(
                            file,
                            os.path.basename(file),
                            compress_type=zipfile.ZIP_DEFLATED
                        )
            
            return archive_path
            
        except Exception as e:
            raise FileError(f"خطا در ایجاد آرشیو: {str(e)}", archive_name)
    
    def cleanup_old_files(self, days=30):
        """
        پاکسازی فایل‌های قدیمی
        days: تعداد روزهای نگهداری فایل‌ها
        """
        try:
            current_time = datetime.now()
            
            for filename in os.listdir(self.export_dir):
                file_path = os.path.join(self.export_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if (current_time - file_time).days > days:
                    os.remove(file_path)
                    
        except Exception as e:
            print(f"Error cleaning up old files: {str(e)}") 