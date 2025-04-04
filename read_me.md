stock_app/
│
├── __init__.py
├── main.py                # نقطه ورود اصلی برنامه
├── config.py              # تنظیمات و ثابت‌های برنامه
│
├── core/                  # هسته اصلی برنامه
│   ├── __init__.py
│   ├── database.py        # مدیریت پایگاه داده
│   ├── api_handler.py     # ارتباط با APIهای خارجی
│   └── utils.py           # ابزارهای کمکی
│
├── models/                # مدل‌های داده
│   ├── __init__.py
│   ├── stock.py           # مدل سهام
│   ├── watchlist.py       # مدل دیده‌بان
│   └── portfolio.py       # مدل پرتفوی
│
├── ui/                    # بخش رابط کاربری
│   ├── __init__.py
│   ├── main_window.py     # پنجره اصلی
│   ├── tab_manager.py     # مدیریت تب‌ها
│   ├── widgets/           # ویجت‌های سفارشی
│   │   ├── stock_table.py
│   │   ├── search_bar.py
│   │   └── ...
│   └── dialogs/           # دیالوگ‌ها
│       ├── edit_dialog.py
│       └── ...
│
└── assets/                # منابع برنامه
    ├── icons/
    └── styles/