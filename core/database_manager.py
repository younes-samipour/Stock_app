"""
ماژول مدیریت پایگاه داده
قابلیت‌های اصلی:
- ذخیره و بازیابی داده‌های سهام
- مدیریت جداول پایگاه داده
- پشتیبان‌گیری خودکار
- بهینه‌سازی عملکرد
"""

import sqlite3
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
from .exceptions import DatabaseError

class DatabaseManager:
    def __init__(self, db_path: str = 'data/market.db'):
        """
        سازنده کلاس DatabaseManager
        db_path: مسیر فایل پایگاه داده
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self._connect()
        self._create_tables()
        
    def _connect(self):
        """
        برقراری اتصال به پایگاه داده
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
        except Exception as e:
            raise DatabaseError(f"خطا در اتصال به پایگاه داده: {str(e)}")
            
    def _create_tables(self):
        """
        ایجاد جداول مورد نیاز
        """
        try:
            # جدول قیمت‌های روزانه
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_prices (
                    symbol TEXT,
                    date DATE,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    PRIMARY KEY (symbol, date)
                )
            ''')
            
            # جدول اطلاعات پایه سهام
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_info (
                    symbol TEXT PRIMARY KEY,
                    name TEXT,
                    market TEXT,
                    industry TEXT,
                    last_update DATETIME
                )
            ''')
            
            self.connection.commit()
            
        except Exception as e:
            raise DatabaseError(f"خطا در ایجاد جداول: {str(e)}")
    
    def save_stock_data(self, symbol, data):
        """
        ذخیره اطلاعات یک سهم در پایگاه داده
        symbol: نماد سهم
        data: دیتافریم اطلاعات سهم
        """
        self._connect()
        try:
            # بروزرسانی جدول سهام
            self.cursor.execute("""
                INSERT OR REPLACE INTO stocks 
                (symbol, last_update) VALUES (?, ?)
            """, (symbol, datetime.now()))
            
            # تبدیل دیتافریم به رکوردهای قابل درج
            records = data.to_dict('records')
            for record in records:
                self.cursor.execute("""
                    INSERT OR REPLACE INTO daily_prices 
                    (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (symbol, record['date'], record['open'],
                     record['high'], record['low'], record['close'],
                     record['volume']))
                     
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(f"خطا در ذخیره اطلاعات سهم: {str(e)}")
        finally:
            self._disconnect()
    
    def get_stock_data(self, symbol, start_date=None, end_date=None):
        """
        بازیابی اطلاعات یک سهم از پایگاه داده
        symbol: نماد سهم
        start_date: تاریخ شروع
        end_date: تاریخ پایان
        return: دیتافریم اطلاعات سهم
        """
        self._connect()
        try:
            query = """
                SELECT date, open, high, low, close, volume
                FROM daily_prices
                WHERE symbol = ?
            """
            params = [symbol]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
                
            query += " ORDER BY date"
            
            df = pd.read_sql_query(query, self.connection, params=params)
            return df
            
        except Exception as e:
            raise DatabaseError(f"خطا در بازیابی اطلاعات سهم: {str(e)}")
        finally:
            self._disconnect()
    
    def add_to_watchlist(self, symbol, notes=''):
        """
        افزودن سهم به لیست علاقه‌مندی‌ها
        symbol: نماد سهم
        notes: یادداشت‌های مربوط به سهم
        """
        self._connect()
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO watchlist 
                (symbol, added_date, notes) VALUES (?, ?, ?)
            """, (symbol, datetime.now(), notes))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(f"خطا در افزودن به لیست علاقه‌مندی‌ها: {str(e)}")
        finally:
            self._disconnect()
    
    def _disconnect(self):
        """
        قطع اتصال از پایگاه داده
        """
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def get_watchlist(self):
        """
        دریافت لیست علاقه‌مندی‌ها
        return: دیتافریم سهام موجود در لیست
        """
        self._connect()
        try:
            query = """
                SELECT w.symbol, w.added_date, w.notes,
                       s.name, s.market, s.industry
                FROM watchlist w
                LEFT JOIN stock_info s ON w.symbol = s.symbol
                ORDER BY w.added_date DESC
            """
            return pd.read_sql_query(query, self.connection)
        except Exception as e:
            raise DatabaseError(f"خطا در دریافت لیست علاقه‌مندی‌ها: {str(e)}")
        finally:
            self._disconnect()

    def update_stock_info(self, symbol: str, info: Dict):
        """
        بروزرسانی اطلاعات پایه سهم
        symbol: نماد سهم
        info: دیکشنری اطلاعات جدید
        """
        self._connect()
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO stock_info
                (symbol, name, market, industry, last_update)
                VALUES (?, ?, ?, ?, ?)
            """, (
                symbol,
                info.get('name'),
                info.get('market'),
                info.get('industry'),
                datetime.now()
            ))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(f"خطا در بروزرسانی اطلاعات سهم: {str(e)}")
        finally:
            self._disconnect()

    def get_last_price(self, symbol: str) -> Optional[float]:
        """
        دریافت آخرین قیمت سهم
        symbol: نماد سهم
        return: آخرین قیمت یا None
        """
        self._connect()
        try:
            self.cursor.execute("""
                SELECT close
                FROM daily_prices
                WHERE symbol = ?
                ORDER BY date DESC
                LIMIT 1
            """, (symbol,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            raise DatabaseError(f"خطا در دریافت آخرین قیمت: {str(e)}")
        finally:
            self._disconnect()

    def backup_database(self, backup_path: str = None):
        """
        پشتیبان‌گیری از پایگاه داده
        backup_path: مسیر فایل پشتیبان
        return: مسیر فایل پشتیبان
        """
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'data/backups/market_db_{timestamp}.sqlite'
        
        try:
            # ایجاد نسخه پشتیبان
            backup_conn = sqlite3.connect(backup_path)
            self.connection.backup(backup_conn)
            backup_conn.close()
            return backup_path
        except Exception as e:
            raise DatabaseError(f"خطا در پشتیبان‌گیری از پایگاه داده: {str(e)}")

    def optimize_database(self):
        """
        بهینه‌سازی پایگاه داده
        """
        self._connect()
        try:
            # حذف داده‌های اضافی و بازسازی ایندکس‌ها
            self.cursor.execute("VACUUM")
            self.cursor.execute("ANALYZE")
            self.connection.commit()
        except Exception as e:
            raise DatabaseError(f"خطا در بهینه‌سازی پایگاه داده: {str(e)}")
        finally:
            self._disconnect()

    def get_database_stats(self) -> Dict:
        """
        دریافت آمار پایگاه داده
        return: دیکشنری آمار پایگاه داده
        """
        self._connect()
        try:
            stats = {}
            
            # تعداد سهام
            self.cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_info")
            stats['total_stocks'] = self.cursor.fetchone()[0]
            
            # تعداد رکوردهای قیمت
            self.cursor.execute("SELECT COUNT(*) FROM daily_prices")
            stats['total_price_records'] = self.cursor.fetchone()[0]
            
            # آخرین بروزرسانی
            self.cursor.execute("""
                SELECT MAX(last_update) FROM stock_info
            """)
            stats['last_update'] = self.cursor.fetchone()[0]
            
            return stats
        except Exception as e:
            raise DatabaseError(f"خطا در دریافت آمار پایگاه داده: {str(e)}")
        finally:
            self._disconnect()

    def remove_from_watchlist(self, symbol: str):
        """
        حذف سهم از لیست علاقه‌مندی‌ها
        symbol: نماد سهم
        """
        self._connect()
        try:
            self.cursor.execute("""
                DELETE FROM watchlist
                WHERE symbol = ?
            """, (symbol,))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(f"خطا در حذف از لیست علاقه‌مندی‌ها: {str(e)}")
        finally:
            self._disconnect()

    def cleanup_old_data(self, days: int = 365):
        """
        پاکسازی داده‌های قدیمی
        days: تعداد روزهای نگهداری داده
        """
        self._connect()
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).date()
            
            # حذف قیمت‌های قدیمی
            self.cursor.execute("""
                DELETE FROM daily_prices
                WHERE date < ?
            """, (cutoff_date,))
            
            # بروزرسانی آمار جداول
            self.optimize_database()
            
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(f"خطا در پاکسازی داده‌های قدیمی: {str(e)}")
        finally:
            self._disconnect()

    def get_symbols_list(self) -> List[str]:
        """
        دریافت لیست تمام نمادهای موجود
        return: لیست نمادها
        """
        self._connect()
        try:
            self.cursor.execute("SELECT DISTINCT symbol FROM stock_info")
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            raise DatabaseError(f"خطا در دریافت لیست نمادها: {str(e)}")
        finally:
            self._disconnect() 