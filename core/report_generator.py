"""
این ماژول تولید گزارش‌های تحلیلی را بر عهده دارد.
این ماژول امکانات زیر را فراهم می‌کند:
- تولید گزارش‌های تحلیل تکنیکال
- تولید گزارش‌های آماری
- تولید گزارش‌های مقایسه‌ای
- صدور گزارش‌ها در فرمت‌های مختلف
"""

import pandas as pd
from datetime import datetime
from .data_analyzer import DataAnalyzer
from .chart_generator import ChartGenerator
from .export_manager import ExportManager
from .exceptions import ValidationError

class ReportGenerator:
    def __init__(self):
        """
        سازنده کلاس ReportGenerator
        راه‌اندازی تولیدکننده گزارش با تنظیمات پایه
        """
        self.analyzer = DataAnalyzer()
        self.chart_gen = ChartGenerator()
        self.exporter = ExportManager()
    
    def generate_technical_report(self, data, symbol):
        """
        تولید گزارش تحلیل تکنیکال
        data: داده‌های سهم
        symbol: نماد سهم
        return: دیکشنری گزارش
        """
        # بارگذاری داده‌ها
        self.analyzer.load_data(data, symbol)
        self.chart_gen.load_data(data, symbol)
        
        # محاسبه شاخص‌های تکنیکال
        rsi = self.analyzer.calculate_rsi()
        macd, signal, hist = self.analyzer.calculate_macd()
        ma20 = self.analyzer.calculate_moving_average(20)
        ma50 = self.analyzer.calculate_moving_average(50)
        
        # رسم نمودارها
        price_chart = self.chart_gen.plot_candlestick(ma_periods=[20, 50])
        indicators_chart = self.chart_gen.plot_technical_indicators({
            'RSI': {'period': 14},
            'MACD': {'fast': 12, 'slow': 26, 'signal': 9}
        })
        
        # تولید گزارش
        report = {
            'symbol': symbol,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'technical_analysis': {
                'current_price': data['close'].iloc[-1],
                'rsi': rsi.iloc[-1],
                'macd': macd.iloc[-1],
                'ma20': ma20.iloc[-1],
                'ma50': ma50.iloc[-1],
                'signals': self._generate_signals(data)
            },
            'charts': {
                'price': price_chart,
                'indicators': indicators_chart
            }
        }
        
        return report
    
    def generate_statistical_report(self, data, symbol):
        """
        تولید گزارش آماری
        data: داده‌های سهم
        symbol: نماد سهم
        return: دیکشنری گزارش
        """
        # بارگذاری داده‌ها
        self.analyzer.load_data(data, symbol)
        
        # محاسبه آمار
        stats = self.analyzer.get_summary_stats()
        volatility = self.analyzer.calculate_volatility()
        
        # تولید گزارش
        report = {
            'symbol': symbol,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': {
                **stats,
                'volatility_30d': volatility.iloc[-30:].mean(),
                'price_range': {
                    'min': data['low'].min(),
                    'max': data['high'].max(),
                    'avg': data['close'].mean()
                },
                'volume_stats': {
                    'avg_volume': data['volume'].mean(),
                    'max_volume': data['volume'].max(),
                    'volume_trend': self._calculate_volume_trend(data)
                }
            }
        }
        
        return report
    
    def generate_comparison_report(self, data_list, symbols):
        """
        تولید گزارش مقایسه‌ای چند سهم
        data_list: لیست داده‌های سهام
        symbols: لیست نمادها
        return: دیکشنری گزارش
        """
        if len(data_list) != len(symbols):
            raise ValidationError("تعداد داده‌ها و نمادها باید برابر باشد")
        
        comparison = []
        for data, symbol in zip(data_list, symbols):
            self.analyzer.load_data(data, symbol)
            stats = self.analyzer.get_summary_stats()
            comparison.append({
                'symbol': symbol,
                **stats
            })
        
        report = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'comparison': comparison,
            'rankings': self._generate_rankings(comparison)
        }
        
        return report
    
    def export_report(self, report, format='pdf'):
        """
        صدور گزارش در فرمت مورد نظر
        report: دیکشنری گزارش
        format: فرمت خروجی ('pdf', 'excel', 'html')
        return: مسیر فایل ایجاد شده
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{report['symbol']}_{timestamp}.{format}"
        
        if format == 'pdf':
            return self._export_pdf(report, filename)
        elif format == 'excel':
            return self._export_excel(report, filename)
        elif format == 'html':
            return self._export_html(report, filename)
        else:
            raise ValueError(f"فرمت {format} پشتیبانی نمی‌شود")
    
    def _generate_signals(self, data):
        """
        تولید سیگنال‌های معاملاتی
        data: داده‌های سهم
        return: لیست سیگنال‌ها
        """
        signals = []
        # پیاده‌سازی منطق تولید سیگنال
        return signals
    
    def _calculate_volume_trend(self, data):
        """
        محاسبه روند حجم معاملات
        data: داده‌های سهم
        return: توضیح روند
        """
        # پیاده‌سازی محاسبه روند حجم
        pass
    
    def _generate_rankings(self, comparison):
        """
        تولید رتبه‌بندی سهام
        comparison: لیست مقایسه سهام
        return: دیکشنری رتبه‌بندی‌ها
        """
        # پیاده‌سازی رتبه‌بندی
        pass 