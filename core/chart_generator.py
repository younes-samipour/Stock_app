"""
ماژول تولید نمودارهای تحلیلی و تکنیکال
قابلیت‌های اصلی:
- رسم نمودارهای قیمت
- رسم اندیکاتورهای تکنیکال
- رسم نمودارهای مقایسه‌ای
- ذخیره و مدیریت نمودارها
"""

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from .exceptions import ValidationError

class ChartGenerator:
    def __init__(self):
        """
        سازنده کلاس ChartGenerator
        تنظیم پارامترهای پایه نمودارها
        """
        self.style = 'yahoo'  # سبک پیش‌فرض نمودارها
        self.dpi = 100  # وضوح تصویر
        self.figsize = (12, 8)  # اندازه پیش‌فرض نمودار
        
    def create_price_chart(self, data: pd.DataFrame, symbol: str, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> str:
        """
        ایجاد نمودار قیمت
        data: دیتافریم داده‌های قیمت
        symbol: نماد سهم
        start_date: تاریخ شروع (اختیاری)
        end_date: تاریخ پایان (اختیاری)
        return: مسیر فایل نمودار ذخیره شده
        """
        try:
            # فیلتر تاریخ
            if start_date:
                data = data[data.index >= start_date]
            if end_date:
                data = data[data.index <= end_date]
                
            # تنظیم پارامترهای نمودار
            title = f'نمودار قیمت {symbol}'
            filename = f'charts/{symbol}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            
            # رسم نمودار
            mpf.plot(data, type='candle', style=self.style,
                    title=title, savefig=filename,
                    volume=True, figsize=self.figsize, dpi=self.dpi)
            
            return filename
            
        except Exception as e:
            raise ValidationError(f"خطا در ایجاد نمودار قیمت: {str(e)}")
    
    def load_data(self, data, symbol):
        """
        بارگذاری داده‌های سهم برای رسم نمودار
        data: دیتافریم داده‌های سهم
        symbol: نماد سهم
        """
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
        
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            raise ValidationError("ستون‌های مورد نیاز در داده‌ها موجود نیست")
            
        # تنظیم ایندکس تاریخ
        data.set_index('date', inplace=True)
        data.index = pd.to_datetime(data.index)
        
        self.data = data
        self.symbol = symbol
    
    def plot_candlestick(self, ma_periods=None, volume=True):
        """
        رسم نمودار شمعی قیمت
        ma_periods: لیست دوره‌های میانگین متحرک
        volume: نمایش حجم معاملات
        return: شیء نمودار
        """
        if self.data is None:
            raise ValidationError("داده‌ای برای رسم نمودار بارگذاری نشده است")
            
        # تنظیم پنل‌های نمودار
        panels = []
        if volume:
            panels.append('volume')
            
        # تنظیم میانگین‌های متحرک
        addplot = []
        if ma_periods:
            for period in ma_periods:
                ma = self.data['close'].rolling(window=period).mean()
                addplot.append(
                    mpf.make_addplot(ma, panel=0, color=f'C{len(addplot)}')
                )
        
        # رسم نمودار
        fig, axes = mpf.plot(
            self.data,
            type='candle',
            style=self.style,
            title=f'نمودار قیمت {self.symbol}',
            volume=volume,
            addplot=addplot,
            returnfig=True
        )
        
        return fig
    
    def plot_technical_indicators(self, indicators):
        """
        رسم نمودار با اندیکاتورهای تکنیکال
        indicators: دیکشنری اندیکاتورها و پارامترهای آنها
        return: شیء نمودار
        """
        if self.data is None:
            raise ValidationError("داده‌ای برای رسم نمودار بارگذاری نشده است")
            
        fig, axes = plt.subplots(len(indicators) + 1, 1, figsize=(12, 8))
        
        # رسم نمودار قیمت در پنل اول
        mpf.plot(
            self.data,
            type='candle',
            style=self.style,
            ax=axes[0],
            volume=False
        )
        
        # رسم اندیکاتورها در پنل‌های بعدی
        for i, (name, params) in enumerate(indicators.items(), 1):
            if name == 'RSI':
                rsi = self.data['close'].ta.rsi(**params)
                axes[i].plot(self.data.index, rsi)
                axes[i].set_title('RSI')
                axes[i].axhline(70, color='r', linestyle='--')
                axes[i].axhline(30, color='g', linestyle='--')
            
            elif name == 'MACD':
                macd = self.data['close'].ta.macd(**params)
                macd.plot(ax=axes[i])
                axes[i].set_title('MACD')
        
        plt.tight_layout()
        return fig
    
    def plot_support_resistance(self, levels):
        """
        رسم نمودار با سطوح حمایت و مقاومت
        levels: تاپل (سطوح حمایت، سطوح مقاومت)
        return: شیء نمودار
        """
        if self.data is None:
            raise ValidationError("داده‌ای برای رسم نمودار بارگذاری نشده است")
            
        support_levels, resistance_levels = levels
        
        # رسم نمودار پایه
        fig = self.plot_candlestick(volume=False)
        ax = fig.axes[0]
        
        # رسم خطوط حمایت
        for level in support_levels:
            ax.axhline(
                y=level,
                color='g',
                linestyle='--',
                alpha=0.5,
                label='Support'
            )
        
        # رسم خطوط مقاومت
        for level in resistance_levels:
            ax.axhline(
                y=level,
                color='r',
                linestyle='--',
                alpha=0.5,
                label='Resistance'
            )
        
        ax.legend()
        return fig
    
    def save_chart(self, fig, filename):
        """
        ذخیره نمودار در فایل
        fig: شیء نمودار
        filename: نام فایل خروجی
        return: نتیجه موفقیت‌آمیز بودن ذخیره‌سازی
        """
        try:
            fig.savefig(
                f'data/charts/{filename}',
                dpi=300,  # وضوح بالا برای خروجی
                bbox_inches='tight'  # حذف حاشیه‌های اضافی
            )
            return True
        except Exception as e:
            print(f"Error saving chart: {str(e)}")
            return False 