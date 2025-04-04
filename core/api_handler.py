"""
این ماژول ارتباط با API بازار بورس را مدیریت می‌کند.
"""

import requests
from datetime import datetime
import json
import time
from core.config import Config

class StockAPI:
    """کلاس مدیریت ارتباط با API بازار بورس"""
    
    def __init__(self):
        """سازنده کلاس StockAPI"""
        self.config = Config()
        self.base_url = self.config.get("api", "base_url")
        self.timeout = self.config.get("api", "timeout")
        self.retry_count = self.config.get("api", "retry_count")
        self.session = requests.Session()
        
    def get_stock_info(self, symbol):
        """
        دریافت اطلاعات سهم
        symbol: نماد سهم
        return: دیکشنری اطلاعات سهم
        """
        try:
            # ارسال درخواست به API
            params = {
                "i": symbol,
                "t": "stock"
            }
            response = self.send_request("GET", params=params)
            
            if response.status_code == 200:
                # پردازش پاسخ
                data = response.text.split(";")
                if len(data) >= 5:
                    return {
                        "symbol": symbol,
                        "name": data[0],
                        "last_price": float(data[1]),
                        "change": float(data[2]),
                        "volume": int(data[3]),
                        "value": float(data[4])
                    }
            return None
            
        except Exception as e:
            print(f"Error getting stock info: {str(e)}")
            return None
            
    def get_stock_history(self, symbol, start_date=None, end_date=None):
        """
        دریافت تاریخچه قیمت سهم
        symbol: نماد سهم
        start_date: تاریخ شروع (اختیاری)
        end_date: تاریخ پایان (اختیاری)
        return: لیست تاریخچه قیمت
        """
        try:
            # ارسال درخواست به API
            params = {
                "i": symbol,
                "t": "history"
            }
            if start_date:
                params["start"] = start_date
            if end_date:
                params["end"] = end_date
                
            response = self.send_request("GET", params=params)
            
            if response.status_code == 200:
                # پردازش پاسخ
                data = response.text.split(";")
                history = []
                for row in data:
                    if row:
                        items = row.split(",")
                        if len(items) >= 7:
                            history.append({
                                "date": items[0],
                                "open": float(items[1]),
                                "high": float(items[2]),
                                "low": float(items[3]),
                                "close": float(items[4]),
                                "volume": int(items[5]),
                                "value": float(items[6])
                            })
                return history
            return None
            
        except Exception as e:
            print(f"Error getting stock history: {str(e)}")
            return None
            
    def get_market_watch(self):
        """
        دریافت دیده‌بان بازار
        return: لیست اطلاعات سهام
        """
        try:
            # ارسال درخواست به API
            params = {
                "t": "market"
            }
            response = self.send_request("GET", params=params)
            
            if response.status_code == 200:
                # پردازش پاسخ
                data = response.text.split(";")
                stocks = []
                for row in data:
                    if row:
                        items = row.split(",")
                        if len(items) >= 5:
                            stocks.append({
                                "symbol": items[0],
                                "name": items[1],
                                "last_price": float(items[2]),
                                "change": float(items[3]),
                                "volume": int(items[4])
                            })
                return stocks
            return None
            
        except Exception as e:
            print(f"Error getting market watch: {str(e)}")
            return None
            
    def get_index_info(self):
        """
        دریافت اطلاعات شاخص‌ها
        return: دیکشنری اطلاعات شاخص‌ها
        """
        try:
            # ارسال درخواست به API
            params = {
                "t": "index"
            }
            response = self.send_request("GET", params=params)
            
            if response.status_code == 200:
                # پردازش پاسخ
                data = response.text.split(";")
                if len(data) >= 4:
                    return {
                        "total_index": float(data[0]),
                        "total_index_change": float(data[1]),
                        "market_value": float(data[2]),
                        "trade_value": float(data[3])
                    }
            return None
            
        except Exception as e:
            print(f"Error getting index info: {str(e)}")
            return None
            
    def get_stocks_list(self):
        """
        دریافت لیست کامل سهام
        return: لیست دیکشنری‌های اطلاعات سهام
        """
        try:
            # ارسال درخواست به API
            params = {
                "t": "list"
            }
            response = self.send_request("GET", params=params)
            
            if response.status_code == 200:
                # پردازش پاسخ
                data = response.text.split(";")
                stocks = []
                for row in data:
                    if row:
                        items = row.split(",")
                        if len(items) >= 4:
                            stocks.append({
                                "symbol": items[0],
                                "name": items[1],
                                "code": items[2],
                                "category": items[3]
                            })
                return stocks
            return None
            
        except Exception as e:
            print(f"Error getting stocks list: {str(e)}")
            return None
            
    def get_important_news(self):
        """
        دریافت اخبار مهم
        return: لیست دیکشنری‌های اخبار
        """
        try:
            # ارسال درخواست به API
            params = {
                "t": "news"
            }
            response = self.send_request("GET", params=params)
            
            if response.status_code == 200:
                # پردازش پاسخ
                data = response.text.split(";")
                news = []
                for row in data:
                    if row:
                        items = row.split(",")
                        if len(items) >= 3:
                            news.append({
                                "time": items[0],
                                "title": items[1],
                                "link": items[2]
                            })
                return news
            return None
            
        except Exception as e:
            print(f"Error getting important news: {str(e)}")
            return None
            
    def send_request(self, method, params=None):
        """
        ارسال درخواست به API
        method: متد درخواست (GET/POST)
        params: پارامترهای درخواست
        return: پاسخ درخواست
        """
        for i in range(self.retry_count):
            try:
                response = self.session.request(
                    method,
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                return response
                
            except requests.exceptions.RequestException as e:
                print(f"Request failed (attempt {i+1}/{self.retry_count}): {str(e)}")
                if i < self.retry_count - 1:
                    time.sleep(1)  # تاخیر قبل از تلاش مجدد
                    
        return None