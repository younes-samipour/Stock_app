"""
ماژول تحلیل داده‌های بازار سهام
قابلیت‌های اصلی:
- محاسبه شاخص‌های تکنیکال
- تحلیل آماری داده‌ها
- شناسایی الگوهای قیمتی
- محاسبه سیگنال‌های معاملاتی
"""

import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .exceptions import ValidationError

class DataAnalyzer:
    def __init__(self):
        """
        سازنده کلاس DataAnalyzer
        تنظیم پارامترهای پایه تحلیل
        """
        self.data = None
        self.symbol = None
        self.indicators = {}
        
    def validate_data(self, data):
        """
        اعتبارسنجی داده‌های ورودی
        data: دیتافریم داده‌های قیمت
        raises: ValidationError اگر داده‌ها معتبر نباشند
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValidationError(f"Missing required columns: {missing_columns}")
            
        if len(data) < 30:  # حداقل داده مورد نیاز
            raise ValidationError("Insufficient data points (minimum 30 required)")
            
    def calculate_sma(self, data, window=None):
        """
        محاسبه میانگین متحرک ساده
        data: دیتافریم قیمت‌ها
        window: دوره زمانی (پیش‌فرض از تنظیمات)
        return: سری میانگین متحرک
        """
        window = window or self.default_params['sma']['window']
        sma = SMAIndicator(close=data['close'], window=window)
        return sma.sma_indicator()
        
    def calculate_ema(self, data, window=None):
        """
        محاسبه میانگین متحرک نمایی
        data: دیتافریم قیمت‌ها
        window: دوره زمانی (پیش‌فرض از تنظیمات)
        return: سری میانگین متحرک نمایی
        """
        window = window or self.default_params['ema']['window']
        ema = EMAIndicator(close=data['close'], window=window)
        return ema.ema_indicator()
        
    def calculate_macd(self, data):
        """
        محاسبه شاخص MACD
        data: دیتافریم قیمت‌ها
        return: دیکشنری شامل MACD و سیگنال
        """
        params = self.default_params['macd']
        macd = MACD(
            close=data['close'],
            window_slow=params['window_slow'],
            window_fast=params['window_fast'],
            window_sign=params['window_sign']
        )
        return {
            'macd': macd.macd(),
            'signal': macd.macd_signal(),
            'histogram': macd.macd_diff()
        }
        
    def calculate_rsi(self, data, window=None):
        """
        محاسبه شاخص RSI
        data: دیتافریم قیمت‌ها
        window: دوره زمانی (پیش‌فرض از تنظیمات)
        return: سری RSI
        """
        window = window or self.default_params['rsi']['window']
        rsi = RSIIndicator(close=data['close'], window=window)
        return rsi.rsi()
        
    def calculate_bollinger_bands(self, data):
        """
        محاسبه باندهای بولینگر
        data: دیتافریم قیمت‌ها
        return: دیکشنری شامل باندهای بالا، پایین و میانی
        """
        params = self.default_params['bollinger']
        bollinger = BollingerBands(
            close=data['close'],
            window=params['window'],
            window_dev=params['window_dev']
        )
        return {
            'upper': bollinger.bollinger_hband(),
            'lower': bollinger.bollinger_lband(),
            'middle': bollinger.bollinger_mavg()
        }
        
    def analyze_trend(self, data: pd.DataFrame, window: int = 20) -> Dict:
        """
        تحلیل روند قیمت
        data: دیتافریم قیمت‌ها
        window: دوره زمانی تحلیل
        return: دیکشنری نتایج تحلیل
        """
        try:
            # محاسبه میانگین متحرک
            ma = data['close'].rolling(window=window).mean()
            
            # تعیین روند بر اساس شیب میانگین متحرک
            slope = (ma.iloc[-1] - ma.iloc[-window]) / window
            
            # محاسبه قدرت روند
            momentum = (data['close'].iloc[-1] - data['close'].iloc[-window]) / data['close'].iloc[-window] * 100
            
            return {
                'trend': 'صعودی' if slope > 0 else 'نزولی',
                'strength': abs(slope),
                'momentum': momentum,
                'ma': ma.iloc[-1]
            }
            
        except Exception as e:
            raise ValidationError(f"خطا در تحلیل روند: {str(e)}")
            
    def calculate_technical_indicators(self, data: pd.DataFrame) -> Dict:
        """
        محاسبه شاخص‌های تکنیکال
        data: دیتافریم قیمت‌ها
        return: دیکشنری شاخص‌های محاسبه شده
        """
        try:
            results = {}
            
            # محاسبه RSI
            results['rsi'] = self._calculate_rsi(
                data['close'],
                self.default_params['rsi_period']
            )
            
            # محاسبه MACD
            results['macd'] = self._calculate_macd(
                data['close'],
                self.default_params['macd_fast'],
                self.default_params['macd_slow'],
                self.default_params['macd_signal']
            )
            
            # محاسبه باندهای بولینگر
            results['bollinger'] = self._calculate_bollinger_bands(
                data['close'],
                self.default_params['bb_period'],
                self.default_params['bb_std']
            )
            
            return results
            
        except Exception as e:
            raise ValidationError(f"خطا در محاسبه شاخص‌های تکنیکال: {str(e)}")
        
    def generate_signals(self, data):
        """
        تولید سیگنال‌های معاملاتی
        data: دیتافریم قیمت‌ها
        return: دیکشنری سیگنال‌های تولید شده
        """
        signals = {
            'trend': self.analyze_trend(data)['trend'],
            'rsi': self.calculate_rsi(data).iloc[-1],
            'macd': self.calculate_macd(data)
        }
        
        # تحلیل سیگنال‌ها
        signals['recommendation'] = self._analyze_signals(signals)
        return signals
        
    def _analyze_signals(self, signals):
        """
        تحلیل سیگنال‌ها و ارائه توصیه
        signals: دیکشنری سیگنال‌ها
        return: توصیه نهایی ('خرید'، 'فروش'، 'نگهداری')
        """
        if signals['trend'] == 'صعودی' and signals['rsi'] < 70:
            return 'خرید'
        elif signals['trend'] == 'نزولی' and signals['rsi'] > 30:
            return 'فروش'
        else:
            return 'نگهداری'

    def load_data(self, data: pd.DataFrame, symbol: str):
        """
        بارگذاری داده‌های سهم برای تحلیل
        data: دیتافریم داده‌های قیمت
        symbol: نماد سهم
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            raise ValidationError("ستون‌های مورد نیاز در داده‌ها موجود نیست")
            
        self.data = data
        self.symbol = symbol
        self.indicators = {}  # پاک کردن شاخص‌های قبلی
    
    def calculate_moving_average(self, period, column='close'):
        """
        محاسبه میانگین متحرک
        period: دوره میانگین‌گیری
        column: نام ستون مورد نظر
        return: سری میانگین متحرک
        """
        if self.data is None:
            raise ValidationError("داده‌ای برای تحلیل بارگذاری نشده است")
            
        return self.data[column].rolling(window=period).mean()
    
    def calculate_volatility(self, window=20):
        """
        محاسبه نوسان‌پذیری قیمت
        window: پنجره زمانی محاسبه
        return: سری نوسان‌پذیری
        """
        if self.data is None:
            raise ValidationError("داده‌ای برای تحلیل بارگذاری نشده است")
            
        # محاسبه بازده روزانه
        returns = self.data['close'].pct_change()
        
        # محاسبه انحراف معیار متحرک و تبدیل به نوسان سالانه
        volatility = returns.rolling(window=window).std() * np.sqrt(252)
        
        return volatility
    
    def detect_price_patterns(self):
        """
        تشخیص الگوهای قیمتی
        return: لیست الگوهای شناسایی شده
        """
        if self.data is None:
            raise ValidationError("داده‌ای برای تحلیل بارگذاری نشده است")
            
        patterns = []
        
        # بررسی الگوی دوقله (Double Top)
        if self._check_double_top():
            patterns.append({
                'type': 'double_top',
                'signal': 'نزولی',
                'reliability': 'بالا'
            })
        
        # بررسی الگوی دودره (Double Bottom)
        if self._check_double_bottom():
            patterns.append({
                'type': 'double_bottom',
                'signal': 'صعودی',
                'reliability': 'بالا'
            })
        
        # بررسی الگوی سر و شانه (Head and Shoulders)
        if self._check_head_and_shoulders():
            patterns.append({
                'type': 'head_and_shoulders',
                'signal': 'نزولی',
                'reliability': 'متوسط'
            })
        
        return patterns
    
    def get_summary_stats(self):
        """
        محاسبه آمار خلاصه سهم
        return: دیکشنری آمار کلیدی
        """
        if self.data is None:
            raise ValidationError("داده‌ای برای تحلیل بارگذاری نشده است")
            
        return {
            'symbol': self.symbol,
            'start_date': self.data['date'].min(),
            'end_date': self.data['date'].max(),
            'trading_days': len(self.data),
            'avg_price': self.data['close'].mean(),
            'avg_volume': self.data['volume'].mean(),
            'price_change': (
                self.data['close'].iloc[-1] - self.data['close'].iloc[0]
            ) / self.data['close'].iloc[0] * 100,
            'volatility': self.calculate_volatility().iloc[-1],
            'rsi': self.calculate_rsi().iloc[-1]
        }

    def generate_report(self):
        """
        تولید گزارش جامع تحلیلی
        return: دیکشنری گزارش تحلیلی
        """
        if self.data is None:
            raise ValidationError("داده‌ای برای تحلیل بارگذاری نشده است")
            
        return {
            'summary': self.get_summary_stats(),
            'technical_indicators': self.calculate_technical_indicators(self.data),
            'trend_analysis': self.analyze_trend(self.data),
            'patterns': self.detect_price_patterns(),
            'signals': self.generate_signals(self.data)
        }

    def _check_double_top(self, threshold=0.02):
        """
        بررسی الگوی دوقله
        threshold: حد آستانه تفاوت قیمت (پیش‌فرض: 2%)
        return: True اگر الگو تشخیص داده شود
        """
        highs = self.data['high'].values
        peaks = []
        
        # یافتن قله‌های محلی
        for i in range(1, len(highs)-1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                peaks.append((i, highs[i]))
                
        # بررسی شرایط دوقله
        if len(peaks) >= 2:
            last_two_peaks = peaks[-2:]
            price_diff = abs(last_two_peaks[1][1] - last_two_peaks[0][1])
            avg_price = (last_two_peaks[1][1] + last_two_peaks[0][1]) / 2
            
            return price_diff / avg_price <= threshold
            
        return False

    def _check_double_bottom(self, threshold=0.02):
        """
        بررسی الگوی دودره
        threshold: حد آستانه تفاوت قیمت (پیش‌فرض: 2%)
        return: True اگر الگو تشخیص داده شود
        """
        lows = self.data['low'].values
        troughs = []
        
        # یافتن دره‌های محلی
        for i in range(1, len(lows)-1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                troughs.append((i, lows[i]))
                
        # بررسی شرایط دودره
        if len(troughs) >= 2:
            last_two_troughs = troughs[-2:]
            price_diff = abs(last_two_troughs[1][1] - last_two_troughs[0][1])
            avg_price = (last_two_troughs[1][1] + last_two_troughs[0][1]) / 2
            
            return price_diff / avg_price <= threshold
            
        return False

    def _check_head_and_shoulders(self, threshold=0.03):
        """
        بررسی الگوی سر و شانه
        threshold: حد آستانه تفاوت قیمت (پیش‌فرض: 3%)
        return: True اگر الگو تشخیص داده شود
        """
        highs = self.data['high'].values
        peaks = []
        
        # یافتن قله‌های محلی
        for i in range(1, len(highs)-1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                peaks.append((i, highs[i]))
                
        # بررسی شرایط سر و شانه
        if len(peaks) >= 3:
            last_three_peaks = peaks[-3:]
            left_shoulder = last_three_peaks[0][1]
            head = last_three_peaks[1][1]
            right_shoulder = last_three_peaks[2][1]
            
            # سر باید بالاتر از شانه‌ها باشد
            if head > left_shoulder and head > right_shoulder:
                # شانه‌ها باید تقریباً هم‌سطح باشند
                shoulder_diff = abs(right_shoulder - left_shoulder)
                avg_shoulder = (right_shoulder + left_shoulder) / 2
                
                return shoulder_diff / avg_shoulder <= threshold
                
        return False

    def analyze_volume(self, window=20):
        """
        تحلیل حجم معاملات
        window: دوره زمانی تحلیل
        return: دیکشنری نتایج تحلیل حجم
        """
        if self.data is None:
            raise ValidationError("داده‌ای برای تحلیل بارگذاری نشده است")
        
        # محاسبه میانگین متحرک حجم
        volume_ma = self.data['volume'].rolling(window=window).mean()
        
        # محاسبه نسبت حجم فعلی به میانگین
        current_ratio = self.data['volume'].iloc[-1] / volume_ma.iloc[-1]
        
        # تشخیص روند حجم
        volume_trend = 'افزایشی' if current_ratio > 1.5 else \
                      'کاهشی' if current_ratio < 0.5 else 'عادی'
                      
        return {
            'avg_volume': volume_ma.iloc[-1],
            'current_volume': self.data['volume'].iloc[-1],
            'volume_ratio': current_ratio,
            'volume_trend': volume_trend
        }

    def calculate_support_resistance(self, periods=20):
        """
        محاسبه سطوح حمایت و مقاومت
        periods: تعداد دوره‌های بررسی
        return: دیکشنری سطوح حمایت و مقاومت
        """
        if self.data is None:
            raise ValidationError("داده‌ای برای تحلیل بارگذاری نشده است")
        
        # یافتن نقاط اوج و حضیض
        highs = self.data['high'].rolling(window=periods, center=True).max()
        lows = self.data['low'].rolling(window=periods, center=True).min()
        
        # محاسبه سطوح حمایت و مقاومت
        resistance_levels = highs.unique()[-3:]  # سه سطح مقاومت آخر
        support_levels = lows.unique()[:3]  # سه سطح حمایت اول
        
        return {
            'resistance': resistance_levels.tolist(),
            'support': support_levels.tolist(),
            'current_price': self.data['close'].iloc[-1]
        }

    def calculate_fibonacci_levels(self, high_price=None, low_price=None):
        """
        محاسبه سطوح فیبوناچی
        high_price: قیمت بالا (اختیاری)
        low_price: قیمت پایین (اختیاری)
        return: دیکشنری سطوح فیبوناچی
        """
        if self.data is None:
            raise ValidationError("داده‌ای برای تحلیل بارگذاری نشده است")
        
        # استفاده از بالاترین و پایین‌ترین قیمت اخیر اگر ورودی نداشته باشیم
        if high_price is None:
            high_price = self.data['high'].max()
        if low_price is None:
            low_price = self.data['low'].min()
        
        # محاسبه سطوح فیبوناچی
        diff = high_price - low_price
        levels = {
            '0.0': low_price,
            '0.236': low_price + 0.236 * diff,
            '0.382': low_price + 0.382 * diff,
            '0.5': low_price + 0.5 * diff,
            '0.618': low_price + 0.618 * diff,
            '0.786': low_price + 0.786 * diff,
            '1.0': high_price
        }
        
        return levels