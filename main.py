"""
فایل اصلی برنامه برای اجرا
"""

import tkinter as tk
from ui.main_window import MainWindow

def main():
    """
    تابع اصلی برنامه
    """
    # ایجاد پنجره اصلی
    root = tk.Tk()
    
    # ایجاد نمونه از کلاس MainWindow
    app = MainWindow(root)
    
    # اجرای حلقه اصلی برنامه
    root.mainloop()

if __name__ == "__main__":
    main()