"""
ماژول ارتباط با API بازار سهام
قابلیت‌های اصلی:
- دریافت اطلاعات لحظه‌ای
- دریافت داده‌های تاریخی
- مدیریت درخواست‌ها
- کنترل خطاها و محدودیت‌ها
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .exceptions import APIError
from .config import API_CONFIG
import pandas as pd

class APIClient:
    def __init__(self, api_key: str = None):
        """
        سازنده کلاس APIClient
        api_key: کلید API (اختیاری)
        """
        self.api_key = api_key or API_CONFIG['api_key']
        self.base_url = API_CONFIG['base_url']
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
    def _make_request(self, endpoint: str, method: str = 'GET', params: Dict = None) -> Dict:
        """
        ارسال درخواست به API
        endpoint: نقطه پایانی API
        method: متد درخواست
        params: پارامترهای درخواست
        return: پاسخ API
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"خطا در ارتباط با API: {str(e)}")
    
    def get_market_status(self):
        """
        دریافت وضعیت بازار
        return: دیکشنری وضعیت بازار
        """
        try:
            response = self._make_request('market/status')
            return response['data']
        except Exception as e:
            raise APIError(f"خطا در دریافت وضعیت بازار: {str(e)}")
    
    def get_stock_price(self, symbol):
        """
        دریافت قیمت لحظه‌ای سهم
        symbol: نماد سهم
        return: دیکشنری اطلاعات قیمت
        """
        try:
            response = self._make_request(f'stock/{symbol}/price')
            return response['data']
        except Exception as e:
            raise APIError(f"خطا در دریافت قیمت سهم: {str(e)}")
    
    def get_price_history(self, symbol, start_date=None, end_date=None):
        """
        دریافت تاریخچه قیمت سهم
        symbol: نماد سهم
        start_date: تاریخ شروع
        end_date: تاریخ پایان
        return: دیتافریم تاریخچه قیمت
        """
        params = {'symbol': symbol}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        try:
            response = self._make_request('stock/history', params)
            return pd.DataFrame(response['data'])
        except Exception as e:
            raise APIError(f"خطا در دریافت تاریخچه قیمت: {str(e)}")
    
    def get_company_info(self, symbol):
        """
        دریافت اطلاعات بنیادی شرکت
        symbol: نماد سهم
        return: دیکشنری اطلاعات شرکت
        """
        try:
            response = self._make_request(f'company/{symbol}/info')
            return response['data']
        except Exception as e:
            raise APIError(f"خطا در دریافت اطلاعات شرکت: {str(e)}")

    def get_market_indices(self) -> Dict:
        """
        دریافت شاخص‌های بازار
        return: دیکشنری شاخص‌های بازار
        """
        try:
            response = self._make_request('market/indices')
            return {
                'total_index': response['data']['total'],
                'equal_weight': response['data']['equal_weight'],
                'industries': response['data']['industries'],
                'timestamp': datetime.fromtimestamp(response['timestamp'])
            }
        except Exception as e:
            raise APIError(f"خطا در دریافت شاخص‌های بازار: {str(e)}")

    def get_market_watch(self) -> Dict:
        """
        دریافت دیده‌بان بازار
        return: دیکشنری وضعیت کلی نمادها
        """
        try:
            response = self._make_request('market/watch')
            return {
                'symbols': response['data']['symbols'],
                'total_trades': response['data']['total_trades'],
                'total_volume': response['data']['total_volume'],
                'timestamp': datetime.fromtimestamp(response['timestamp'])
            }
        except Exception as e:
            raise APIError(f"خطا در دریافت دیده‌بان بازار: {str(e)}")

    def get_market_depth(self, symbol: str) -> Dict:
        """
        دریافت عمق بازار یک نماد
        symbol: نماد سهم
        return: دیکشنری سفارشات خرید و فروش
        """
        try:
            response = self._make_request(f'market/depth/{symbol}')
            return {
                'buy_orders': response['data']['buy'],
                'sell_orders': response['data']['sell'],
                'last_trade': response['data']['last_trade'],
                'timestamp': datetime.fromtimestamp(response['timestamp'])
            }
        except Exception as e:
            raise APIError(f"خطا در دریافت عمق بازار: {str(e)}")

    def get_historical_trades(self, symbol: str, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """
        دریافت معاملات تاریخی یک نماد
        symbol: نماد سهم
        start_date: تاریخ شروع
        end_date: تاریخ پایان
        return: دیکشنری معاملات تاریخی
        """
        params = {}
        if start_date:
            params['start_date'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['end_date'] = end_date.strftime('%Y-%m-%d')
        
        try:
            response = self._make_request(f'trades/{symbol}/history', params=params)
            return {
                'trades': response['data']['trades'],
                'total_volume': response['data']['total_volume'],
                'average_price': response['data']['average_price']
            }
        except Exception as e:
            raise APIError(f"خطا در دریافت معاملات تاریخی: {str(e)}")

    def get_fundamental_data(self, symbol: str) -> Dict:
        """
        دریافت اطلاعات بنیادی سهم
        symbol: نماد سهم
        return: دیکشنری اطلاعات بنیادی
        """
        try:
            response = self._make_request(f'fundamental/{symbol}')
            return {
                'eps': response['data']['eps'],
                'p_e': response['data']['p_e'],
                'book_value': response['data']['book_value'],
                'market_cap': response['data']['market_cap'],
                'shares_count': response['data']['shares_count'],
                'float_shares': response['data']['float_shares'],
                'industry': response['data']['industry'],
                'last_update': datetime.fromtimestamp(response['timestamp'])
            }
        except Exception as e:
            raise APIError(f"خطا در دریافت اطلاعات بنیادی: {str(e)}")

    def get_client_types(self, symbol: str) -> Dict:
        """
        دریافت اطلاعات حقیقی/حقوقی
        symbol: نماد سهم
        return: دیکشنری اطلاعات خرید و فروش به تفکیک نوع مشتری
        """
        try:
            response = self._make_request(f'client-types/{symbol}')
            return {
                'individual_buy': response['data']['individual_buy'],
                'individual_sell': response['data']['individual_sell'],
                'institutional_buy': response['data']['institutional_buy'],
                'institutional_sell': response['data']['institutional_sell'],
                'date': datetime.fromtimestamp(response['timestamp'])
            }
        except Exception as e:
            raise APIError(f"خطا در دریافت اطلاعات حقیقی/حقوقی: {str(e)}") 