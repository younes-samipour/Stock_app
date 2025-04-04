"""
این ماژول مدیریت ارتباط با پایگاه داده SQLite را بر عهده دارد.
این ماژول امکانات زیر را فراهم می‌کند:
- ایجاد و مدیریت جداول پایگاه داده
- ذخیره و بازیابی اطلاعات سهام
- مدیریت لیست سهام منتخب
- ذخیره تنظیمات برنامه
"""

import sqlite3
import os
from datetime import datetime
from core.config import Config

class DatabaseManager:
    """کلاس مدیریت پایگاه داده"""
    
    def __init__(self):
        """سازنده کلاس DatabaseManager"""
        self.config = Config()
        self.db_path = self.config.get("database", "path")
        self.backup_path = self.config.get("database", "backup_path")
        
        # ایجاد پوشه‌های مورد نیاز
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.backup_path, exist_ok=True)
        
        # اتصال به پایگاه داده
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # ایجاد جداول
        self.create_tables()
        
        # Insert sample data if tables are empty
        self.insert_sample_data()
        
    def create_tables(self):
        """ایجاد جداول پایگاه داده"""
        try:
            # جدول لیست سهام
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_list (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT UNIQUE,
                    name TEXT,
                    code TEXT,
                    sector TEXT,
                    market TEXT,
                    last_update TIMESTAMP
                )
            """)
            
            # جدول قیمت‌ها
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    symbol TEXT,
                    date TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    PRIMARY KEY (symbol, date)
                )
            """)
            
            # جدول پرتفوی
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT,
                    quantity INTEGER,
                    avg_price REAL,
                    total_value REAL,
                    status TEXT DEFAULT 'open',
                    last_update TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES stock_list(symbol)
                )
            """)
            
            # جدول دیده‌بان
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT,
                    alert_price REAL,
                    alert_type TEXT,
                    last_update TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES stock_list(symbol)
                )
            """)
            
            # جدول هشدارها
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT,
                    alert_type TEXT,
                    price REAL,
                    status TEXT,
                    created_at TIMESTAMP,
                    triggered_at TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES stock_list(symbol)
                )
            """)
            
            # جدول تنظیمات
            self.cursor.execute("""
                DROP TABLE IF EXISTS settings
            """)
            self.cursor.execute("""
                CREATE TABLE settings (
                    id INTEGER PRIMARY KEY,
                    basic_info_url TEXT,
                    ratios_url TEXT,
                    statements_url TEXT,
                    profitability_url TEXT
                )
            """)
            
            # ذخیره تغییرات
            self.conn.commit()
            
            # مقداردهی اولیه داده‌های سهام
            self.initialize_stock_data()
            
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
            
    def initialize_stock_data(self):
        """مقداردهی اولیه داده‌های سهام"""
        try:
            # بررسی وجود داده در جدول
            self.cursor.execute("SELECT COUNT(*) FROM stock_list")
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                # داده‌های اولیه سهام
                initial_stocks = {
                    'خودرو': 'IRO1IKCO0001',
                    'فولاد': 'IRO1FOLD0001',
                    'شستا': 'IRO1SSIC0001',
                    'وبملت': 'IRO1BMLT0001',
                    'شپنا': 'IRO1NAFT0001',
                    'فملی': 'IRO1MSMI0001',
                    'وتجارت': 'IRO1TEJC0001',
                    'وبصادر': 'IRO1BSDR0001',
                    'وپارس': 'IRO1PARS0001',
                    'ومعادن': 'IRO1MIND0001'
                }
                
                # درج داده‌ها در جدول
                for symbol, code in initial_stocks.items():
                    self.cursor.execute('''
                        INSERT INTO stock_list (symbol, name, code, sector, market, last_update) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (symbol, symbol, code, 'default', 'default', datetime.now()))
                
                self.conn.commit()
                print("Stock data initialized successfully")
                
        except Exception as e:
            print(f"Error initializing stock data: {str(e)}")
            
    def get_stock_list(self):
        """
        دریافت لیست سهام
        return: لیست دیکشنری‌های اطلاعات سهام
        """
        try:
            self.cursor.execute("SELECT * FROM stock_list")
            rows = self.cursor.fetchall()
            
            return [{
                "symbol": row[1],
                "name": row[2],
                "code": row[3],
                "sector": row[4],
                "market": row[5]
            } for row in rows]
            
        except Exception as e:
            print(f"Error getting stock list: {str(e)}")
            return []
            
    def get_stock(self, symbol):
        """
        دریافت اطلاعات یک سهم
        symbol: نماد سهم
        return: دیکشنری اطلاعات سهم
        """
        try:
            self.cursor.execute("SELECT * FROM stock_list WHERE symbol=?", (symbol,))
            row = self.cursor.fetchone()
            
            if row:
                return {
                    "symbol": row[1],
                    "name": row[2],
                    "code": row[3],
                    "sector": row[4],
                    "market": row[5]
                }
            return None
            
        except Exception as e:
            print(f"Error getting stock: {str(e)}")
            return None
            
    def add_stock(self, stock):
        """
        اضافه کردن سهم جدید
        stock: دیکشنری اطلاعات سهم
        return: True در صورت موفقیت
        """
        try:
            self.cursor.execute("""
                INSERT INTO stock_list (symbol, name, code, sector, market, last_update)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                stock["symbol"],
                stock["name"],
                stock["code"],
                stock["sector"],
                stock["market"],
                datetime.now()
            ))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error adding stock: {str(e)}")
            return False
            
    def update_stock(self, symbol, data):
        """
        به‌روزرسانی اطلاعات سهم
        symbol: نماد سهم
        data: دیکشنری اطلاعات جدید
        return: True در صورت موفقیت
        """
        try:
            self.cursor.execute("""
                UPDATE stock_list
                SET name=?, code=?, sector=?, market=?
                WHERE symbol=?
            """, (
                data["name"],
                data["code"],
                data["sector"],
                data["market"],
                symbol
            ))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating stock: {str(e)}")
            return False
            
    def remove_stock(self, symbol):
        """
        حذف سهم
        symbol: نماد سهم
        return: True در صورت موفقیت
        """
        try:
            self.cursor.execute("DELETE FROM stock_list WHERE symbol=?", (symbol,))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error removing stock: {str(e)}")
            return False
            
    def get_portfolio(self):
        """
        دریافت لیست پرتفوی
        return: لیست دیکشنری‌های اطلاعات پرتفوی
        """
        try:
            self.cursor.execute("SELECT * FROM portfolio")
            rows = self.cursor.fetchall()
            
            return [{
                "id": row[0],
                "symbol": row[1],
                "quantity": row[2],
                "buy_price": row[3],
                "buy_date": row[4],
                "sell_price": row[5],
                "sell_date": row[6],
                "status": row[7]
            } for row in rows]
            
        except Exception as e:
            print(f"Error getting portfolio: {str(e)}")
            return []
            
    def add_to_portfolio(self, item):
        """
        اضافه کردن سهم به پرتفوی
        item: دیکشنری اطلاعات سهم
        return: True در صورت موفقیت
        """
        try:
            self.cursor.execute("""
                INSERT INTO portfolio (symbol, quantity, avg_price, total_value, last_update)
                VALUES (?, ?, ?, ?, ?)
            """, (
                item["symbol"],
                item["quantity"],
                item["buy_price"],
                item["buy_price"] * item["quantity"],
                datetime.now()
            ))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error adding to portfolio: {str(e)}")
            return False
            
    def update_portfolio(self, id, data):
        """
        به‌روزرسانی اطلاعات پرتفوی
        id: شناسه سهم
        data: دیکشنری اطلاعات جدید
        return: True در صورت موفقیت
        """
        try:
            self.cursor.execute("""
                UPDATE portfolio
                SET quantity=?, avg_price=?, total_value=?, last_update=?
                WHERE id=?
            """, (
                data["quantity"],
                data["buy_price"],
                data["buy_price"] * data["quantity"],
                datetime.now(),
                id
            ))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating portfolio: {str(e)}")
            return False
            
    def remove_from_portfolio(self, id):
        """
        حذف سهم از پرتفوی
        id: شناسه سهم
        return: True در صورت موفقیت
        """
        try:
            self.cursor.execute("DELETE FROM portfolio WHERE id=?", (id,))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error removing from portfolio: {str(e)}")
            return False
            
    def get_watchlist(self):
        """
        دریافت لیست دیده‌بان
        return: لیست دیکشنری‌های اطلاعات دیده‌بان
        """
        try:
            self.cursor.execute("SELECT * FROM watchlist")
            rows = self.cursor.fetchall()
            
            return [{
                "symbol": row[2],
                "alert_price": row[3],
                "alert_type": row[4],
                "status": row[5]
            } for row in rows]
            
        except Exception as e:
            print(f"Error getting watchlist: {str(e)}")
            return []
            
    def add_to_watchlist(self, item):
        """
        اضافه کردن سهم به دیده‌بان
        item: دیکشنری اطلاعات سهم
        return: True در صورت موفقیت
        """
        try:
            self.cursor.execute("""
                INSERT INTO watchlist (symbol, alert_price, alert_type, status)
                VALUES (?, ?, ?, ?)
            """, (
                item["symbol"],
                item["alert_price"],
                item["alert_type"],
                "active"
            ))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error adding to watchlist: {str(e)}")
            return False
            
    def update_watchlist(self, symbol, data):
        """
        به‌روزرسانی اطلاعات دیده‌بان
        symbol: نماد سهم
        data: دیکشنری اطلاعات جدید
        return: True در صورت موفقیت
        """
        try:
            self.cursor.execute("""
                UPDATE watchlist
                SET alert_price=?, alert_type=?, status=?
                WHERE symbol=?
            """, (
                data["alert_price"],
                data["alert_type"],
                data["status"],
                symbol
            ))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating watchlist: {str(e)}")
            return False
            
    def remove_from_watchlist(self, symbol):
        """
        حذف سهم از دیده‌بان
        symbol: نماد سهم
        return: True در صورت موفقیت
        """
        try:
            self.cursor.execute("DELETE FROM watchlist WHERE symbol=?", (symbol,))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error removing from watchlist: {str(e)}")
            return False
            
    def get_alerts(self):
        """
        دریافت لیست هشدارها
        return: لیست دیکشنری‌های اطلاعات هشدارها
        """
        try:
            self.cursor.execute("SELECT * FROM alerts")
            rows = self.cursor.fetchall()
            
            return [{
                "id": row[0],
                "symbol": row[1],
                "type": row[2],
                "price": row[3],
                "status": row[4],
                "time": row[5]
            } for row in rows]
            
        except Exception as e:
            print(f"Error getting alerts: {str(e)}")
            return []
            
    def add_alert(self, alert):
        """
        اضافه کردن هشدار جدید
        alert: دیکشنری اطلاعات هشدار
        return: True در صورت موفقیت
        """
        try:
            self.cursor.execute("""
                INSERT INTO alerts (symbol, type, price, status, time)
                VALUES (?, ?, ?, ?, ?)
            """, (
                alert["symbol"],
                alert["type"],
                alert["price"],
                alert["status"],
                alert["time"]
            ))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error adding alert: {str(e)}")
            return False
            
    def update_alert(self, id, data):
        """
        به‌روزرسانی اطلاعات هشدار
        id: شناسه هشدار
        data: دیکشنری اطلاعات جدید
        return: True در صورت موفقیت
        """
        try:
            self.cursor.execute("""
                UPDATE alerts
                SET symbol=?, type=?, price=?, status=?, time=?
                WHERE id=?
            """, (
                data["symbol"],
                data["type"],
                data["price"],
                data["status"],
                data["time"],
                id
            ))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating alert: {str(e)}")
            return False
            
    def remove_alert(self, id):
        """
        حذف هشدار
        id: شناسه هشدار
        return: True در صورت موفقیت
        """
        try:
            # انتقال به تاریخچه
            self.cursor.execute("SELECT * FROM alerts WHERE id=?", (id,))
            row = self.cursor.fetchone()
            if row:
                self.cursor.execute("""
                    INSERT INTO alert_history (symbol, type, price, status, time)
                    VALUES (?, ?, ?, ?, ?)
                """, (row[1], row[2], row[3], row[4], row[5]))
                
            # حذف از جدول هشدارها
            self.cursor.execute("DELETE FROM alerts WHERE id=?", (id,))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error removing alert: {str(e)}")
            return False
            
    def clear_alerts(self):
        """
        پاک کردن همه هشدارها
        return: True در صورت موفقیت
        """
        try:
            # انتقال به تاریخچه
            self.cursor.execute("""
                INSERT INTO alert_history (symbol, type, price, status, time)
                SELECT symbol, type, price, status, time FROM alerts
            """)
            
            # پاک کردن جدول هشدارها
            self.cursor.execute("DELETE FROM alerts")
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error clearing alerts: {str(e)}")
            return False
            
    def backup_database(self):
        """
        تهیه نسخه پشتیبان از پایگاه داده
        return: True در صورت موفقیت
        """
        try:
            # ایجاد نام فایل پشتیبان
            backup_file = os.path.join(
                self.backup_path,
                f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            
            # کپی فایل پایگاه داده
            import shutil
            shutil.copy2(self.db_path, backup_file)
            return True
            
        except Exception as e:
            print(f"Error backing up database: {str(e)}")
            return False
            
    def get_portfolio_summary(self):
        """
        دریافت خلاصه اطلاعات پرتفوی
        return: دیکشنری شامل اطلاعات خلاصه پرتفوی
        """
        try:
            # دریافت اطلاعات پرتفوی
            self.cursor.execute("""
                SELECT 
                    symbol,
                    SUM(quantity) as total_quantity,
                    AVG(avg_price) as avg_buy_price,
                    SUM(quantity * avg_price) as total_investment
                FROM portfolio
                WHERE status = 'open'
                GROUP BY symbol
            """)
            
            portfolio = self.cursor.fetchall()
            
            # محاسبه ارزش فعلی
            total_value = 0
            total_investment = 0
            total_profit = 0
            
            for item in portfolio:
                symbol, quantity, avg_price, investment = item
                
                # دریافت آخرین قیمت
                self.cursor.execute("""
                    SELECT close
                    FROM prices
                    WHERE symbol = ?
                    ORDER BY date DESC
                    LIMIT 1
                """, (symbol,))
                
                last_price = self.cursor.fetchone()
                if last_price:
                    current_value = quantity * last_price[0]
                    total_value += current_value
                    total_investment += investment
                    total_profit += current_value - investment
            
            return {
                "total_value": total_value,
                "total_investment": total_investment,
                "total_profit": total_profit,
                "profit_percentage": (total_profit / total_investment * 100) if total_investment > 0 else 0
            }
            
        except Exception as e:
            print(f"Error getting portfolio summary: {str(e)}")
            return None
            
    def get_trades_report(self):
        """
        دریافت گزارش معاملات
        return: لیست دیکشنری‌های اطلاعات معاملات
        """
        try:
            self.cursor.execute("""
                SELECT 
                    p.id,
                    p.symbol,
                    p.quantity,
                    p.avg_price as buy_price,
                    p.last_update as buy_date,
                    CASE 
                        WHEN p.quantity IS NOT NULL 
                        THEN (p.quantity * p.avg_price) 
                        ELSE NULL 
                    END as sell_price,
                    CASE 
                        WHEN p.quantity IS NOT NULL 
                        THEN p.last_update 
                        ELSE NULL 
                    END as sell_date,
                    CASE 
                        WHEN p.quantity IS NOT NULL 
                        THEN p.status 
                        ELSE NULL 
                    END as status,
                    CASE 
                        WHEN p.quantity IS NOT NULL 
                        THEN (p.quantity * p.avg_price) - (p.quantity * p.avg_price) 
                        ELSE NULL 
                    END as profit
                FROM portfolio p
                WHERE p.status = 'open'
                ORDER BY p.last_update DESC
            """)
            
            rows = self.cursor.fetchall()
            return [{
                "id": row[0],
                "symbol": row[1],
                "quantity": row[2],
                "buy_price": row[3],
                "buy_date": row[4],
                "sell_price": row[5],
                "sell_date": row[6],
                "status": row[7],
                "profit": row[8]
            } for row in rows]
            
        except Exception as e:
            print(f"Error getting trades report: {str(e)}")
            return []
            
    def get_portfolio_stocks(self):
        """
        دریافت لیست سهام پرتفوی
        return: لیست دیکشنری‌های اطلاعات سهام
        """
        try:
            self.cursor.execute("""
                SELECT 
                    p.symbol,
                    SUM(p.quantity) as total_quantity,
                    AVG(p.avg_price) as avg_buy_price,
                    MAX(pr.close) as current_price,
                    SUM(p.quantity * p.avg_price) as total_cost,
                    SUM(p.quantity * COALESCE(pr.close, p.avg_price)) as current_value
                FROM portfolio p
                LEFT JOIN prices pr ON p.symbol = pr.symbol
                WHERE p.status = 'open'
                GROUP BY p.symbol
            """)
            
            rows = self.cursor.fetchall()
            return [{
                "symbol": row[0],
                "quantity": row[1],
                "buy_price": row[2],
                "current_price": row[3] or row[2],
                "value": row[5],
                "profit": row[5] - row[4],
                "return": ((row[5] - row[4]) / row[4] * 100) if row[4] > 0 else 0
            } for row in rows]
            
        except Exception as e:
            print(f"Error getting portfolio stocks: {str(e)}")
            return []
            
    def get_portfolio_allocation(self):
        """
        دریافت تخصیص دارایی پرتفوی
        return: لیست دیکشنری‌های اطلاعات تخصیص دارایی
        """
        try:
            stocks = self.get_portfolio_stocks()
            total_value = sum(stock["value"] for stock in stocks)
            
            return [{
                "symbol": stock["symbol"],
                "value": stock["value"],
                "percentage": (stock["value"] / total_value * 100) if total_value > 0 else 0
            } for stock in stocks]
            
        except Exception as e:
            print(f"Error getting portfolio allocation: {str(e)}")
            return []
            
    def get_portfolio_history(self):
        """
        دریافت تاریخچه ارزش پرتفوی
        return: لیست دیکشنری‌های اطلاعات تاریخچه
        """
        try:
            self.cursor.execute("""
                SELECT 
                    pr.date,
                    SUM(p.quantity * pr.close) as total_value
                FROM portfolio p
                JOIN prices pr ON p.symbol = pr.symbol
                WHERE p.status = 'open'
                GROUP BY pr.date
                ORDER BY pr.date
            """)
            
            rows = self.cursor.fetchall()
            return [{
                "date": row[0],
                "value": row[1]
            } for row in rows]
            
        except Exception as e:
            print(f"Error getting portfolio history: {str(e)}")
            return []
            
    def get_top_stocks(self):
        """
        دریافت سهام برتر پرتفوی
        return: لیست دیکشنری‌های اطلاعات سهام برتر
        """
        try:
            stocks = self.get_portfolio_stocks()
            return sorted(stocks, key=lambda x: x["value"], reverse=True)[:5]
            
        except Exception as e:
            print(f"Error getting top stocks: {str(e)}")
            return []
            
    def insert_sample_data(self):
        """Insert sample data into tables"""
        # Check if stock_list is empty
        self.cursor.execute('SELECT COUNT(*) FROM stock_list')
        if self.cursor.fetchone()[0] == 0:
            # Insert sample stocks
            sample_stocks = [
                ('خودرو', 'ایران خودرو', 'IRAN1', 'خودرو', 'بورس', datetime.now()),
                ('فولاد', 'فولاد مبارکه', 'FOLD1', 'فلزات', 'بورس', datetime.now()),
                ('وبملت', 'بانک ملت', 'BMLT1', 'بانک', 'بورس', datetime.now()),
                ('فملی', 'معدنی و فلزی', 'FMLI1', 'فلزات', 'بورس', datetime.now()),
                ('شپنا', 'پالایش نفت', 'SHGN1', 'نفت', 'بورس', datetime.now())
            ]
            
            self.cursor.executemany('''
                INSERT INTO stock_list (symbol, name, code, sector, market, last_update)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', sample_stocks)
            
        # Check if settings is empty
        self.cursor.execute('SELECT COUNT(*) FROM settings')
        if self.cursor.fetchone()[0] == 0:
            # Insert default settings
            self.cursor.execute('''
                INSERT INTO settings (id, basic_info_url, ratios_url, statements_url, profitability_url)
                VALUES (1, '', '', '', '')
            ''')
            
        self.conn.commit()
            
    def __del__(self):
        """تخریب‌گر کلاس"""
        try:
            self.conn.close()
        except:
            pass