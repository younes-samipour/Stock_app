"""
این ماژول مسئول دریافت و مدیریت داده‌های بازار است.
قابلیت‌های اصلی این ماژول عبارتند از:
- دریافت قیمت‌های لحظه‌ای
- دریافت تاریخچه قیمت
- مدیریت نمادها و اطلاعات پایه
- ذخیره و بازیابی داده‌ها
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .exceptions import ValidationError
from .cache_manager import CacheManager
import requests

class MarketDataProvider:
    def __init__(self):
        """
        سازنده کلاس MarketDataProvider
        راه‌اندازی کش و تنظیمات اولیه
        """
        self.cache = CacheManager()
        self.symbols = {}  # دیکشنری اطلاعات نمادها
        self.load_symbols()
        
    def load_symbols(self):
        """
        بارگذاری اطلاعات پایه نمادها
        """
        try:
            # بارگذاری از کش یا فایل
            cached_symbols = self.cache.get('symbols')
            if cached_symbols:
                self.symbols = cached_symbols
            else:
                # بارگذاری از فایل یا API
                self._load_symbols_from_source()
                # ذخیره در کش
                self.cache.set('symbols', self.symbols, ttl=86400)  # 24 ساعت
        except Exception as e:
            raise ValidationError(f"خطا در بارگذاری نمادها: {str(e)}")
            
    def get_real_time_price(self, symbol: str) -> Dict:
        """
        دریافت قیمت لحظه‌ای
        symbol: نماد سهم
        return: دیکشنری اطلاعات قیمت
        """
        if symbol not in self.symbols:
            raise ValidationError(f"نماد {symbol} معتبر نیست")
            
        # بررسی کش
        cached_price = self.cache.get(f'price_{symbol}')
        if cached_price:
            return cached_price
            
        try:
            # دریافت از API
            price_data = self._fetch_real_time_price(symbol)
            # ذخیره در کش با TTL کوتاه
            self.cache.set(f'price_{symbol}', price_data, ttl=60)
            return price_data
        except Exception as e:
            raise ValidationError(f"خطا در دریافت قیمت: {str(e)}")
            
    def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        دریافت تاریخچه قیمت
        symbol: نماد سهم
        start_date: تاریخ شروع
        end_date: تاریخ پایان
        return: دیتافریم تاریخچه قیمت
        """
        if symbol not in self.symbols:
            raise ValidationError(f"نماد {symbol} معتبر نیست")
            
        cache_key = f'history_{symbol}_{start_date.date()}_{end_date.date()}'
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            return pd.DataFrame(cached_data)
            
        try:
            # دریافت از API
            historical_data = self._fetch_historical_data(symbol, start_date, end_date)
            # ذخیره در کش
            self.cache.set(cache_key, historical_data.to_dict(), ttl=3600)
            return historical_data
        except Exception as e:
            raise ValidationError(f"خطا در دریافت تاریخچه: {str(e)}")

    def _load_symbols_from_source(self):
        """
        بارگذاری اطلاعات نمادها از منبع اصلی (API یا فایل)
        """
        try:
            # اتصال به API بورس
            response = self._make_api_request('symbols')
            
            # پردازش و ذخیره اطلاعات نمادها
            for symbol_data in response:
                symbol = symbol_data['symbol']
                self.symbols[symbol] = {
                    'name': symbol_data['name'],
                    'market': symbol_data['market'],
                    'industry': symbol_data['industry'],
                    'last_update': datetime.now()
                }
        except Exception as e:
            raise ValidationError(f"خطا در بارگذاری نمادها از منبع: {str(e)}")

    def _fetch_real_time_price(self, symbol: str) -> Dict:
        """
        دریافت قیمت لحظه‌ای از API
        symbol: نماد سهم
        return: دیکشنری اطلاعات قیمت
        """
        try:
            # دریافت اطلاعات از API
            response = self._make_api_request(f'price/{symbol}')
            
            return {
                'symbol': symbol,
                'price': float(response['price']),
                'change': float(response['change']),
                'volume': int(response['volume']),
                'timestamp': datetime.fromtimestamp(response['timestamp']),
                'bid': float(response.get('bid', 0)),
                'ask': float(response.get('ask', 0))
            }
        except Exception as e:
            raise ValidationError(f"خطا در دریافت قیمت از API: {str(e)}")

    def _fetch_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        دریافت داده‌های تاریخی از API
        symbol: نماد سهم
        start_date: تاریخ شروع
        end_date: تاریخ پایان
        return: دیتافریم داده‌های تاریخی
        """
        try:
            # تبدیل تاریخ‌ها به فرمت مورد نیاز API
            params = {
                'symbol': symbol,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d')
            }
            
            # دریافت داده‌ها از API
            response = self._make_api_request('history', params)
            
            # تبدیل به دیتافریم
            df = pd.DataFrame(response['data'])
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            raise ValidationError(f"خطا در دریافت داده‌های تاریخی از API: {str(e)}")

    def _make_api_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        ارسال درخواست به API
        endpoint: نقطه پایانی API
        params: پارامترهای درخواست
        return: پاسخ API
        """
        try:
            # تنظیمات درخواست
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # ارسال درخواست
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            
            # بررسی خطاها
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"خطا در ارتباط با API: {str(e)}")

    def get_market_status(self) -> Dict:
        """
        دریافت وضعیت کلی بازار
        return: دیکشنری وضعیت بازار
        """
        try:
            # بررسی کش
            cached_status = self.cache.get('market_status')
            if cached_status:
                return cached_status
            
            # دریافت از API
            response = self._make_api_request('market/status')
            status_data = {
                'is_open': response['is_open'],
                'timestamp': datetime.fromtimestamp(response['timestamp']),
                'index_value': float(response['index_value']),
                'index_change': float(response['index_change']),
                'total_volume': int(response['total_volume']),
                'total_trades': int(response['total_trades'])
            }
            
            # ذخیره در کش
            self.cache.set('market_status', status_data, ttl=300)  # 5 دقیقه
            return status_data
        
        except Exception as e:
            raise ValidationError(f"خطا در دریافت وضعیت بازار: {str(e)}")

    def get_market_depth(self, symbol: str) -> Dict:
        """
        دریافت عمق بازار برای یک نماد
        symbol: نماد سهم
        return: دیکشنری عمق بازار
        """
        if symbol not in self.symbols:
            raise ValidationError(f"نماد {symbol} معتبر نیست")
        
        try:
            # دریافت از API
            response = self._make_api_request(f'depth/{symbol}')
            
            return {
                'bids': [
                    {'price': float(bid['price']), 'volume': int(bid['volume'])}
                    for bid in response['bids']
                ],
                'asks': [
                    {'price': float(ask['price']), 'volume': int(ask['volume'])}
                    for ask in response['asks']
                ],
                'timestamp': datetime.fromtimestamp(response['timestamp'])
            }
        
        except Exception as e:
            raise ValidationError(f"خطا در دریافت عمق بازار: {str(e)}")

    def get_intraday_data(self, symbol: str) -> pd.DataFrame:
        """
        دریافت داده‌های درون روزی
        symbol: نماد سهم
        return: دیتافریم داده‌های درون روزی
        """
        if symbol not in self.symbols:
            raise ValidationError(f"نماد {symbol} معتبر نیست")
        
        try:
            # دریافت از API
            response = self._make_api_request(f'intraday/{symbol}')
            
            # تبدیل به دیتافریم
            df = pd.DataFrame(response['data'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp', inplace=True)
            
            return df
        
        except Exception as e:
            raise ValidationError(f"خطا در دریافت داده‌های درون روزی: {str(e)}")

    def get_market_indices(self) -> Dict:
        """
        دریافت شاخص‌های اصلی بازار
        return: دیکشنری شاخص‌های بازار
        """
        try:
            # بررسی کش
            cached_indices = self.cache.get('market_indices')
            if cached_indices:
                return cached_indices
            
            # دریافت از API
            response = self._make_api_request('indices')
            indices_data = {
                'total_index': {
                    'value': float(response['total']['value']),
                    'change': float(response['total']['change'])
                },
                'equal_weight': {
                    'value': float(response['equal_weight']['value']),
                    'change': float(response['equal_weight']['change'])
                },
                'industry_indices': {
                    name: {
                        'value': float(data['value']),
                        'change': float(data['change'])
                    }
                    for name, data in response['industries'].items()
                }
            }
            
            # ذخیره در کش
            self.cache.set('market_indices', indices_data, ttl=300)  # 5 دقیقه
            return indices_data
        
        except Exception as e:
            raise ValidationError(f"خطا در دریافت شاخص‌های بازار: {str(e)}")

    def get_symbol_info(self, symbol: str) -> Dict:
        """
        دریافت اطلاعات کامل یک نماد
        symbol: نماد سهم
        return: دیکشنری اطلاعات نماد
        """
        if symbol not in self.symbols:
            raise ValidationError(f"نماد {symbol} معتبر نیست")
        
        try:
            # دریافت از API
            response = self._make_api_request(f'symbol/{symbol}/info')
            
            return {
                'symbol': symbol,
                'name': response['name'],
                'market': response['market'],
                'industry': response['industry'],
                'eps': float(response.get('eps', 0)),
                'p_e': float(response.get('p_e', 0)),
                'market_cap': float(response.get('market_cap', 0)),
                'shares_count': int(response.get('shares_count', 0)),
                'float_shares': int(response.get('float_shares', 0)),
                'trading_status': response.get('trading_status', 'unknown')
            }
        
        except Exception as e:
            raise ValidationError(f"خطا در دریافت اطلاعات نماد: {str(e)}")

    def get_market_calendar(self, year: int, month: int) -> List[Dict]:
        """
        دریافت تقویم بازار
        year: سال
        month: ماه
        return: لیست روزهای معاملاتی
        """
        try:
            cache_key = f'calendar_{year}_{month}'
            cached_calendar = self.cache.get(cache_key)
            if cached_calendar:
                return cached_calendar
            
            # دریافت از API
            response = self._make_api_request('calendar', {
                'year': year,
                'month': month
            })
            
            calendar_data = [
                {
                    'date': datetime.strptime(day['date'], '%Y-%m-%d'),
                    'is_trading_day': day['is_trading_day'],
                    'description': day.get('description', '')
                }
                for day in response['days']
            ]
            
            # ذخیره در کش
            self.cache.set(cache_key, calendar_data, ttl=86400)  # 24 ساعت
            return calendar_data
        
        except Exception as e:
            raise ValidationError(f"خطا در دریافت تقویم بازار: {str(e)}")

    def get_market_watch(self) -> pd.DataFrame:
        """
        دریافت دیده‌بان بازار (مارکت واچ)
        return: دیتافریم اطلاعات کلی نمادها
        """
        try:
            # بررسی کش
            cached_watch = self.cache.get('market_watch')
            if cached_watch is not None:
                return pd.DataFrame(cached_watch)
            
            # دریافت از API
            response = self._make_api_request('market/watch')
            
            # تبدیل به دیتافریم
            df = pd.DataFrame(response['data'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            
            # محاسبات اضافی
            df['value'] = df['price'] * df['volume']
            df['price_change_percent'] = (df['price_change'] / (df['price'] - df['price_change'])) * 100
            
            # ذخیره در کش
            self.cache.set('market_watch', df.to_dict(), ttl=60)  # 1 دقیقه
            return df
        
        except Exception as e:
            raise ValidationError(f"خطا در دریافت دیده‌بان بازار: {str(e)}")

    def get_trades_history(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """
        دریافت تاریخچه معاملات یک نماد
        symbol: نماد سهم
        limit: تعداد معاملات درخواستی
        return: دیتافریم معاملات
        """
        if symbol not in self.symbols:
            raise ValidationError(f"نماد {symbol} معتبر نیست")
        
        try:
            # دریافت از API
            response = self._make_api_request(f'trades/{symbol}', {'limit': limit})
            
            # تبدیل به دیتافریم
            df = pd.DataFrame(response['trades'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df['value'] = df['price'] * df['volume']
            
            return df.sort_values('timestamp', ascending=False)
        
        except Exception as e:
            raise ValidationError(f"خطا در دریافت تاریخچه معاملات: {str(e)}")

    def get_client_types(self, symbol: str) -> Dict:
        """
        دریافت اطلاعات معاملات به تفکیک نوع مشتری
        symbol: نماد سهم
        return: دیکشنری اطلاعات معاملات حقیقی/حقوقی
        """
        if symbol not in self.symbols:
            raise ValidationError(f"نماد {symbol} معتبر نیست")
        
        try:
            # دریافت از API
            response = self._make_api_request(f'client-types/{symbol}')
            
            return {
                'individual': {
                    'buy_count': int(response['individual']['buy_count']),
                    'buy_volume': int(response['individual']['buy_volume']),
                    'sell_count': int(response['individual']['sell_count']),
                    'sell_volume': int(response['individual']['sell_volume'])
                },
                'institutional': {
                    'buy_count': int(response['institutional']['buy_count']),
                    'buy_volume': int(response['institutional']['buy_volume']),
                    'sell_count': int(response['institutional']['sell_count']),
                    'sell_volume': int(response['institutional']['sell_volume'])
                },
                'date': datetime.fromtimestamp(response['timestamp'])
            }
        
        except Exception as e:
            raise ValidationError(f"خطا در دریافت اطلاعات نوع مشتری: {str(e)}")

    def get_order_book(self, symbol: str) -> Dict:
        """
        دریافت دفتر سفارشات یک نماد
        symbol: نماد سهم
        return: دیکشنری اطلاعات سفارشات خرید و فروش
        """
        if symbol not in self.symbols:
            raise ValidationError(f"نماد {symbol} معتبر نیست")
        
        try:
            # دریافت از API
            response = self._make_api_request(f'orders/{symbol}')
            
            return {
                'buy_orders': [
                    {
                        'price': float(order['price']),
                        'volume': int(order['volume']),
                        'count': int(order['count'])
                    }
                    for order in response['buy_orders']
                ],
                'sell_orders': [
                    {
                        'price': float(order['price']),
                        'volume': int(order['volume']),
                        'count': int(order['count'])
                    }
                    for order in response['sell_orders']
                ],
                'timestamp': datetime.fromtimestamp(response['timestamp'])
            }
            
        except Exception as e:
            raise ValidationError(f"خطا در دریافت دفتر سفارشات: {str(e)}")

    def get_trade_details(self, symbol: str, trade_id: str) -> Dict:
        """
        دریافت جزئیات یک معامله خاص
        symbol: نماد سهم
        trade_id: شناسه معامله
        return: دیکشنری جزئیات معامله
        """
        if symbol not in self.symbols:
            raise ValidationError(f"نماد {symbol} معتبر نیست")
        
        try:
            # دریافت از API
            response = self._make_api_request(f'trades/{symbol}/{trade_id}')
            
            return {
                'trade_id': trade_id,
                'symbol': symbol,
                'price': float(response['price']),
                'volume': int(response['volume']),
                'timestamp': datetime.fromtimestamp(response['timestamp']),
                'buyer_type': response['buyer_type'],
                'seller_type': response['seller_type'],
                'trade_type': response.get('trade_type', 'regular')
            }
            
        except Exception as e:
            raise ValidationError(f"خطا در دریافت جزئیات معامله: {str(e)}") 