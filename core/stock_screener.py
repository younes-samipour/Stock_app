"""
ماژول غربالگری سهام
قابلیت‌های اصلی:
- فیلتر سهام بر اساس معیارهای بنیادی
- فیلتر سهام بر اساس معیارهای تکنیکال
- رتبه‌بندی سهام بر اساس معیارهای ترکیبی
- ذخیره و بازیابی فیلترهای پرکاربرد
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from .exceptions import ValidationError
from .data_analyzer import DataAnalyzer

class StockScreener:
    def __init__(self):
        """
        سازنده کلاس StockScreener
        راه‌اندازی آنالایزر داده و تنظیمات پایه
        """
        self.analyzer = DataAnalyzer()
        self.filters = {}
        self.market_data = None
        
    def load_market_data(self, data: pd.DataFrame):
        """
        بارگذاری داده‌های کل بازار
        data: دیتافریم داده‌های بازار
        """
        required_columns = ['symbol', 'price', 'volume', 'market_cap', 'p/e', 'eps']
        if not all(col in data.columns for col in required_columns):
            raise ValidationError("ستون‌های مورد نیاز در داده‌ها موجود نیست")
            
        self.market_data = data
        
    def add_filter(self, name: str, conditions: Dict):
        """
        اضافه کردن فیلتر جدید
        name: نام فیلتر
        conditions: شرایط فیلتر
        """
        if name in self.filters:
            raise ValidationError(f"فیلتر {name} قبلاً تعریف شده است")
            
        self.filters[name] = conditions
        
    def apply_price_filter(self, stocks: pd.DataFrame, min_price=None, max_price=None) -> pd.DataFrame:
        """
        اعمال فیلتر قیمت
        stocks: دیتافریم سهام
        min_price: حداقل قیمت
        max_price: حداکثر قیمت
        return: دیتافریم فیلتر شده
        """
        min_price = min_price or self.default_filters['min_price']
        max_price = max_price or self.default_filters['max_price']
        
        mask = (stocks['close'] >= min_price) & (stocks['close'] <= max_price)
        return stocks[mask]
        
    def apply_volume_filter(self, stocks: pd.DataFrame, min_volume=None, max_volume=None) -> pd.DataFrame:
        """
        اعمال فیلتر حجم معاملات
        stocks: دیتافریم سهام
        min_volume: حداقل حجم
        max_volume: حداکثر حجم
        return: دیتافریم فیلتر شده
        """
        min_volume = min_volume or self.default_filters['min_volume']
        max_volume = max_volume or self.default_filters['max_volume']
        
        mask = (stocks['volume'] >= min_volume) & (stocks['volume'] <= max_volume)
        return stocks[mask]
        
    def apply_technical_filter(self, stocks: pd.DataFrame, conditions: Dict) -> pd.DataFrame:
        """
        اعمال فیلتر تکنیکال
        stocks: دیتافریم سهام
        conditions: شرایط تکنیکال
        return: دیتافریم فیلتر شده
        """
        filtered_stocks = stocks.copy()
        
        for symbol in stocks.index:
            stock_data = stocks.loc[symbol]
            
            # محاسبه شاخص‌های تکنیکال
            indicators = self.analyzer.calculate_technical_indicators(stock_data)
            
            # بررسی شرایط RSI
            if 'rsi' in conditions:
                rsi = indicators['rsi'].iloc[-1]
                if not (conditions['rsi']['min'] <= rsi <= conditions['rsi']['max']):
                    filtered_stocks.drop(symbol, inplace=True)
                    continue
                    
            # بررسی شرایط MACD
            if 'macd' in conditions:
                macd = indicators['macd']['macd'].iloc[-1]
                signal = indicators['macd']['signal'].iloc[-1]
                if conditions['macd'] == 'bullish' and macd <= signal:
                    filtered_stocks.drop(symbol, inplace=True)
                    continue
                elif conditions['macd'] == 'bearish' and macd >= signal:
                    filtered_stocks.drop(symbol, inplace=True)
                    continue
                    
        return filtered_stocks 

    def apply_fundamental_filter(self, stocks: pd.DataFrame, conditions: Dict) -> pd.DataFrame:
        """
        اعمال فیلتر بنیادی
        stocks: دیتافریم سهام
        conditions: شرایط بنیادی (P/E، EPS و...)
        return: دیتافریم فیلتر شده
        """
        filtered_stocks = stocks.copy()
        
        # فیلتر P/E
        if 'pe_ratio' in conditions:
            pe_min = conditions['pe_ratio'].get('min', 0)
            pe_max = conditions['pe_ratio'].get('max', float('inf'))
            mask = (filtered_stocks['pe_ratio'] >= pe_min) & \
                   (filtered_stocks['pe_ratio'] <= pe_max)
            filtered_stocks = filtered_stocks[mask]
        
        # فیلتر EPS
        if 'eps' in conditions:
            eps_min = conditions['eps'].get('min', self.default_filters['min_eps'])
            mask = filtered_stocks['eps'] >= eps_min
            filtered_stocks = filtered_stocks[mask]
        
        return filtered_stocks

    def rank_stocks(self, stocks: pd.DataFrame, criteria: Dict) -> pd.DataFrame:
        """
        رتبه‌بندی سهام بر اساس معیارهای مختلف
        stocks: دیتافریم سهام
        criteria: معیارهای رتبه‌بندی و وزن آنها
        return: دیتافریم رتبه‌بندی شده
        """
        ranked_stocks = stocks.copy()
        total_score = pd.Series(0, index=stocks.index)
        
        for criterion, weight in criteria.items():
            if criterion == 'volume':
                # رتبه‌بندی بر اساس حجم معاملات
                score = ranked_stocks['volume'].rank(pct=True)
            elif criterion == 'price_change':
                # رتبه‌بندی بر اساس تغییرات قیمت
                score = ranked_stocks['close'].pct_change().rank(pct=True)
            elif criterion == 'rsi':
                # رتبه‌بندی بر اساس RSI
                score = ranked_stocks['rsi'].rank(pct=True)
            
            total_score += score * weight
        
        ranked_stocks['total_score'] = total_score
        return ranked_stocks.sort_values('total_score', ascending=False)

    def generate_screening_report(self, stocks: pd.DataFrame, filters: Dict) -> Dict:
        """
        تولید گزارش غربالگری
        stocks: دیتافریم سهام
        filters: فیلترهای اعمال شده
        return: دیکشنری گزارش غربالگری
        """
        initial_count = len(stocks)
        
        # اعمال فیلترها به ترتیب
        filtered_stocks = self.apply_price_filter(
            stocks,
            filters.get('min_price'),
            filters.get('max_price')
        )
        
        filtered_stocks = self.apply_volume_filter(
            filtered_stocks,
            filters.get('min_volume'),
            filters.get('max_volume')
        )
        
        if 'technical' in filters:
            filtered_stocks = self.apply_technical_filter(
                filtered_stocks,
                filters['technical']
            )
        
        if 'fundamental' in filters:
            filtered_stocks = self.apply_fundamental_filter(
                filtered_stocks,
                filters['fundamental']
            )
        
        return {
            'initial_count': initial_count,
            'filtered_count': len(filtered_stocks),
            'filtered_stocks': filtered_stocks,
            'filters_applied': filters,
            'timestamp': pd.Timestamp.now()
        }

    def search_by_pattern(self, stocks: pd.DataFrame, pattern_type: str) -> pd.DataFrame:
        """
        جستجوی سهام بر اساس الگوهای تکنیکال
        stocks: دیتافریم سهام
        pattern_type: نوع الگو ('double_top', 'double_bottom', 'head_shoulders')
        return: دیتافریم سهام با الگوی مورد نظر
        """
        matched_stocks = pd.DataFrame()
        
        for symbol in stocks.index:
            stock_data = stocks.loc[symbol]
            
            # بررسی الگو با استفاده از تحلیلگر
            if pattern_type == 'double_top' and self.analyzer._check_double_top(stock_data):
                matched_stocks = matched_stocks.append(stock_data)
            elif pattern_type == 'double_bottom' and self.analyzer._check_double_bottom(stock_data):
                matched_stocks = matched_stocks.append(stock_data)
            elif pattern_type == 'head_shoulders' and self.analyzer._check_head_and_shoulders(stock_data):
                matched_stocks = matched_stocks.append(stock_data)
            
        return matched_stocks

    def filter_by_industry(self, stocks: pd.DataFrame, industries: List[str]) -> pd.DataFrame:
        """
        فیلتر سهام بر اساس صنعت
        stocks: دیتافریم سهام
        industries: لیست صنایع مورد نظر
        return: دیتافریم فیلتر شده
        """
        if not industries:
            return stocks
        
        return stocks[stocks['industry'].isin(industries)]

    def filter_by_market_cap(self, stocks: pd.DataFrame, min_cap: float = None, max_cap: float = None) -> pd.DataFrame:
        """
        فیلتر سهام بر اساس ارزش بازار
        stocks: دیتافریم سهام
        min_cap: حداقل ارزش بازار
        max_cap: حداکثر ارزش بازار
        return: دیتافریم فیلتر شده
        """
        filtered_stocks = stocks.copy()
        
        if min_cap:
            filtered_stocks = filtered_stocks[filtered_stocks['market_cap'] >= min_cap]
        if max_cap:
            filtered_stocks = filtered_stocks[filtered_stocks['market_cap'] <= max_cap]
        
        return filtered_stocks

    def find_breakouts(self, stocks: pd.DataFrame, threshold: float = 0.02) -> pd.DataFrame:
        """
        یافتن سهام در حال شکست مقاومت یا حمایت
        stocks: دیتافریم سهام
        threshold: حد آستانه شکست (پیش‌فرض: 2%)
        return: دیتافریم سهام با شکست قیمتی
        """
        breakouts = pd.DataFrame()
        
        for symbol in stocks.index:
            stock_data = stocks.loc[symbol]
            
            # محاسبه سطوح حمایت و مقاومت
            levels = self.analyzer.calculate_support_resistance(stock_data)
            current_price = stock_data['close'].iloc[-1]
            
            # بررسی شکست مقاومت
            for resistance in levels['resistance']:
                if current_price > resistance * (1 + threshold):
                    stock_data['breakout_type'] = 'resistance'
                    breakouts = breakouts.append(stock_data)
                    break
                
            # بررسی شکست حمایت
            for support in levels['support']:
                if current_price < support * (1 - threshold):
                    stock_data['breakout_type'] = 'support'
                    breakouts = breakouts.append(stock_data)
                    break
                
        return breakouts 

    def find_momentum_stocks(self, stocks: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        یافتن سهام با مومنتوم قوی
        stocks: دیتافریم سهام
        period: دوره زمانی بررسی مومنتوم
        return: دیتافریم سهام با مومنتوم قوی
        """
        momentum_stocks = pd.DataFrame()
        
        for symbol in stocks.index:
            stock_data = stocks.loc[symbol]
            
            # محاسبه تغییرات قیمت در دوره مورد نظر
            price_change = (
                stock_data['close'].iloc[-1] - stock_data['close'].iloc[-period]
            ) / stock_data['close'].iloc[-period] * 100
            
            # محاسبه میانگین حجم معاملات
            volume_ratio = (
                stock_data['volume'].iloc[-5:].mean() / 
                stock_data['volume'].iloc[-period:].mean()
            )
            
            # انتخاب سهام با مومنتوم مثبت و افزایش حجم
            if price_change > 10 and volume_ratio > 1.5:
                stock_data['momentum_score'] = price_change * volume_ratio
                momentum_stocks = momentum_stocks.append(stock_data)
                
        return momentum_stocks.sort_values('momentum_score', ascending=False)

    def find_reversal_candidates(self, stocks: pd.DataFrame) -> pd.DataFrame:
        """
        یافتن سهام با پتانسیل برگشت روند
        stocks: دیتافریم سهام
        return: دیتافریم سهام کاندید برگشت
        """
        reversal_stocks = pd.DataFrame()
        
        for symbol in stocks.index:
            stock_data = stocks.loc[symbol]
            indicators = self.analyzer.calculate_technical_indicators(stock_data)
            
            # بررسی شرایط برگشت صعودی
            if (indicators['rsi'].iloc[-1] < 30 and  # RSI اشباع فروش
                stock_data['volume'].iloc[-1] > stock_data['volume'].mean() * 1.5):  # افزایش حجم
                stock_data['reversal_type'] = 'bullish'
                reversal_stocks = reversal_stocks.append(stock_data)
                
            # بررسی شرایط برگشت نزولی
            elif (indicators['rsi'].iloc[-1] > 70 and  # RSI اشباع خرید
                  stock_data['volume'].iloc[-1] > stock_data['volume'].mean() * 1.5):  # افزایش حجم
                stock_data['reversal_type'] = 'bearish'
                reversal_stocks = reversal_stocks.append(stock_data)
                
        return reversal_stocks

    def find_consolidating_stocks(self, stocks: pd.DataFrame, days: int = 20, threshold: float = 0.05) -> pd.DataFrame:
        """
        یافتن سهام در حال تثبیت
        stocks: دیتافریم سهام
        days: تعداد روزهای بررسی
        threshold: حد آستانه نوسان قیمت
        return: دیتافریم سهام در حال تثبیت
        """
        consolidating_stocks = pd.DataFrame()
        
        for symbol in stocks.index:
            stock_data = stocks.loc[symbol]
            
            # محاسبه حداکثر و حداقل قیمت در دوره
            price_range = stock_data['high'].iloc[-days:].max() - stock_data['low'].iloc[-days:].min()
            avg_price = stock_data['close'].iloc[-days:].mean()
            
            # بررسی محدوده نوسان
            if price_range / avg_price <= threshold:
                stock_data['consolidation_range'] = price_range
                stock_data['avg_price'] = avg_price
                consolidating_stocks = consolidating_stocks.append(stock_data)
                
        return consolidating_stocks.sort_values('consolidation_range')