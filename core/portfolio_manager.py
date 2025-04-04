"""
این ماژول مسئول مدیریت پورتفوی و سبد سهام است.
قابلیت‌های اصلی این ماژول عبارتند از:
- مدیریت خرید و فروش سهام
- محاسبه سود و زیان
- تحلیل عملکرد پورتفوی
- مدیریت ریسک
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .exceptions import ValidationError
from .data_analyzer import DataAnalyzer
import numpy as np

class PortfolioManager:
    def __init__(self):
        """
        سازنده کلاس PortfolioManager
        راه‌اندازی تحلیلگر و ساختارهای داده پورتفوی
        """
        self.analyzer = DataAnalyzer()
        self.portfolio = {}  # دیکشنری نگهداری سهام
        self.transactions = []  # لیست معاملات
        
    def get_portfolio_summary(self) -> Dict:
        """
        دریافت خلاصه وضعیت پورتفوی
        return: دیکشنری شامل خلاصه اطلاعات پورتفوی
        """
        try:
            current_prices = self.get_current_prices()
            portfolio_value = self.calculate_portfolio_value(current_prices)
            portfolio_metrics = self.calculate_portfolio_metrics(current_prices)
            
            return {
                'total_positions': portfolio_metrics['total_positions'],
                'total_value': portfolio_metrics['portfolio_value'],
                'total_profit_loss': portfolio_metrics['total_profit_loss'],
                'profit_loss_percent': portfolio_metrics['profit_loss_percent'],
                'positions': portfolio_value['positions'],
                'max_position_weight': portfolio_metrics['max_position_weight'],
                'position_weights': portfolio_metrics['position_weights']
            }
        except Exception as e:
            return {
                'total_positions': 0,
                'total_value': 0,
                'total_profit_loss': 0,
                'profit_loss_percent': 0,
                'positions': {},
                'max_position_weight': 0,
                'position_weights': {},
                'error': str(e)
            }
        
    def add_position(self, symbol: str, shares: int, price: float, date: datetime):
        """
        افزودن موقعیت جدید به پورتفوی
        symbol: نماد سهم
        shares: تعداد سهام
        price: قیمت خرید
        date: تاریخ خرید
        """
        if shares <= 0:
            raise ValidationError("تعداد سهام باید مثبت باشد")
            
        if symbol in self.portfolio:
            # به‌روزرسانی موقعیت موجود
            position = self.portfolio[symbol]
            total_cost = position['shares'] * position['avg_price']
            new_cost = shares * price
            position['shares'] += shares
            position['avg_price'] = (total_cost + new_cost) / position['shares']
        else:
            # ایجاد موقعیت جدید
            self.portfolio[symbol] = {
                'shares': shares,
                'avg_price': price,
                'date_added': date
            }
            
        # ثبت تراکنش
        self.transactions.append({
            'date': date,
            'symbol': symbol,
            'type': 'buy',
            'shares': shares,
            'price': price
        })
        
    def remove_position(self, symbol: str, shares: int, price: float, date: datetime):
        """
        حذف موقعیت از پورتفوی (فروش)
        symbol: نماد سهم
        shares: تعداد سهام
        price: قیمت فروش
        date: تاریخ فروش
        """
        if symbol not in self.portfolio:
            raise ValidationError(f"سهم {symbol} در پورتفوی موجود نیست")
            
        position = self.portfolio[symbol]
        if shares > position['shares']:
            raise ValidationError("تعداد سهام برای فروش بیشتر از موجودی است")
            
        # به‌روزرسانی موقعیت
        position['shares'] -= shares
        if position['shares'] == 0:
            del self.portfolio[symbol]
            
        # ثبت تراکنش
        self.transactions.append({
            'date': date,
            'symbol': symbol,
            'type': 'sell',
            'shares': shares,
            'price': price
        })

    def calculate_position_value(self, symbol: str, current_price: float) -> Dict:
        """
        محاسبه ارزش فعلی یک موقعیت
        symbol: نماد سهم
        current_price: قیمت فعلی سهم
        return: دیکشنری اطلاعات ارزش موقعیت
        """
        if symbol not in self.portfolio:
            raise ValidationError(f"سهم {symbol} در پورتفوی موجود نیست")
        
        position = self.portfolio[symbol]
        cost_basis = position['shares'] * position['avg_price']
        current_value = position['shares'] * current_price
        profit_loss = current_value - cost_basis
        
        return {
            'shares': position['shares'],
            'avg_price': position['avg_price'],
            'cost_basis': cost_basis,
            'current_value': current_value,
            'profit_loss': profit_loss,
            'profit_loss_percent': (profit_loss / cost_basis) * 100
        }

    def calculate_portfolio_value(self, current_prices: Dict[str, float]) -> Dict:
        """
        محاسبه ارزش کل پورتفوی
        current_prices: دیکشنری قیمت‌های فعلی سهام
        return: دیکشنری اطلاعات ارزش پورتفوی
        """
        total_cost = 0
        total_value = 0
        positions_summary = {}
        
        for symbol in self.portfolio:
            if symbol not in current_prices:
                raise ValidationError(f"قیمت فعلی برای سهم {symbol} موجود نیست")
            
            position_value = self.calculate_position_value(symbol, current_prices[symbol])
            positions_summary[symbol] = position_value
            total_cost += position_value['cost_basis']
            total_value += position_value['current_value']
        
        return {
            'total_cost': total_cost,
            'total_value': total_value,
            'total_profit_loss': total_value - total_cost,
            'total_profit_loss_percent': ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0,
            'positions': positions_summary
        }

    def calculate_portfolio_metrics(self, current_prices: Dict[str, float]) -> Dict:
        """
        محاسبه معیارهای عملکرد پورتفوی
        current_prices: دیکشنری قیمت‌های فعلی سهام
        return: دیکشنری معیارهای عملکرد
        """
        portfolio_value = self.calculate_portfolio_value(current_prices)
        
        # محاسبه تنوع پورتفوی
        position_weights = {}
        for symbol, position in portfolio_value['positions'].items():
            weight = position['current_value'] / portfolio_value['total_value']
            position_weights[symbol] = weight
        
        # محاسبه بزرگترین موقعیت
        max_position = max(position_weights.values()) if position_weights else 0
        
        return {
            'total_positions': len(self.portfolio),
            'portfolio_value': portfolio_value['total_value'],
            'total_profit_loss': portfolio_value['total_profit_loss'],
            'profit_loss_percent': portfolio_value['total_profit_loss_percent'],
            'max_position_weight': max_position,
            'position_weights': position_weights
        }

    def analyze_risk(self, historical_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        تحلیل ریسک پورتفوی
        historical_data: دیکشنری داده‌های تاریخی سهام
        return: دیکشنری معیارهای ریسک
        """
        risk_metrics = {}
        
        for symbol in self.portfolio:
            if symbol not in historical_data:
                raise ValidationError(f"داده تاریخی برای سهم {symbol} موجود نیست")
            
            data = historical_data[symbol]
            position = self.portfolio[symbol]
            
            # محاسبه نوسان‌پذیری (انحراف معیار بازده روزانه)
            daily_returns = data['close'].pct_change()
            volatility = daily_returns.std() * np.sqrt(252)  # تبدیل به نوسان سالانه
            
            # محاسبه بتا (حساسیت به بازار)
            market_returns = data['market_index'].pct_change()
            beta = daily_returns.cov(market_returns) / market_returns.var()
            
            risk_metrics[symbol] = {
                'volatility': volatility,
                'beta': beta,
                'position_size': position['shares'] * data['close'].iloc[-1],
                'risk_contribution': volatility * position['shares'] * data['close'].iloc[-1]
            }
        
        return risk_metrics

    def analyze_performance(self, start_date: datetime, end_date: datetime) -> Dict:
        """
        تحلیل عملکرد پورتفوی در بازه زمانی مشخص
        start_date: تاریخ شروع
        end_date: تاریخ پایان
        return: دیکشنری معیارهای عملکرد
        """
        # فیلتر تراکنش‌ها در بازه زمانی
        period_transactions = [
            t for t in self.transactions
            if start_date <= t['date'] <= end_date
        ]
        
        # محاسبه سود/زیان تحقق یافته
        realized_pl = sum(
            (t['price'] - self.get_cost_basis(t['symbol'], t['date'])) * t['shares']
            for t in period_transactions
            if t['type'] == 'sell'
        )
        
        # محاسبه بازده
        start_value = self.get_portfolio_value_at_date(start_date)
        end_value = self.get_portfolio_value_at_date(end_date)
        
        if start_value == 0:
            return_pct = 0
        else:
            return_pct = ((end_value - start_value) / start_value) * 100
        
        return {
            'period_start': start_date,
            'period_end': end_date,
            'start_value': start_value,
            'end_value': end_value,
            'realized_profit_loss': realized_pl,
            'return_percent': return_pct,
            'transaction_count': len(period_transactions)
        }

    def get_rebalancing_suggestions(self, target_weights: Dict[str, float]) -> Dict:
        """
        محاسبه پیشنهادات برای متوازن‌سازی پورتفوی
        target_weights: دیکشنری وزن‌های هدف
        return: دیکشنری پیشنهادات خرید/فروش
        """
        current_values = self.calculate_portfolio_value(self.get_current_prices())
        total_value = current_values['total_value']
        suggestions = {}
        
        for symbol, target_weight in target_weights.items():
            current_value = current_values['positions'].get(symbol, {'current_value': 0})['current_value']
            current_weight = current_value / total_value if total_value > 0 else 0
            
            # محاسبه اختلاف با وزن هدف
            value_difference = (target_weight - current_weight) * total_value
            
            if abs(value_difference) > total_value * 0.01:  # حداقل 1% تغییر
                suggestions[symbol] = {
                    'current_weight': current_weight * 100,
                    'target_weight': target_weight * 100,
                    'value_difference': value_difference,
                    'action': 'buy' if value_difference > 0 else 'sell'
                }
        
        return suggestions

    def get_cost_basis(self, symbol: str, date: datetime) -> float:
        """
        محاسبه قیمت تمام شده یک سهم در تاریخ مشخص
        symbol: نماد سهم
        date: تاریخ مورد نظر
        return: قیمت تمام شده
        """
        # فیلتر تراکنش‌های قبل از تاریخ مورد نظر
        relevant_transactions = [
            t for t in self.transactions
            if t['symbol'] == symbol and t['date'] <= date
        ]
        
        total_shares = 0
        total_cost = 0
        
        for transaction in relevant_transactions:
            if transaction['type'] == 'buy':
                total_shares += transaction['shares']
                total_cost += transaction['shares'] * transaction['price']
            else:  # sell
                total_shares -= transaction['shares']
                total_cost -= transaction['shares'] * (total_cost / total_shares)
            
        return total_cost / total_shares if total_shares > 0 else 0

    def get_portfolio_value_at_date(self, date: datetime) -> float:
        """
        محاسبه ارزش پورتفوی در تاریخ مشخص
        date: تاریخ مورد نظر
        return: ارزش کل پورتفوی
        """
        # فیلتر تراکنش‌های تا تاریخ مورد نظر
        relevant_transactions = [
            t for t in self.transactions
            if t['date'] <= date
        ]
        
        positions = {}
        for transaction in relevant_transactions:
            symbol = transaction['symbol']
            
            if symbol not in positions:
                positions[symbol] = {'shares': 0, 'cost': 0}
            
            if transaction['type'] == 'buy':
                positions[symbol]['shares'] += transaction['shares']
                positions[symbol]['cost'] += transaction['shares'] * transaction['price']
            else:  # sell
                positions[symbol]['shares'] -= transaction['shares']
                positions[symbol]['cost'] -= transaction['shares'] * (
                    positions[symbol]['cost'] / positions[symbol]['shares']
                )
            
        total_value = sum(
            position['shares'] * self.get_historical_price(symbol, date)
            for symbol, position in positions.items()
            if position['shares'] > 0
        )
        
        return total_value

    def get_historical_price(self, symbol: str, date: datetime) -> float:
        """
        دریافت قیمت تاریخی یک سهم
        symbol: نماد سهم
        date: تاریخ مورد نظر
        return: قیمت سهم در تاریخ مشخص
        """
        # این متد باید به دیتابیس یا API متصل شود
        # فعلاً یک مقدار پیش‌فرض برمی‌گرداند
        return 0.0

    def get_current_prices(self) -> Dict[str, float]:
        """
        دریافت قیمت‌های فعلی سهام پورتفوی
        return: دیکشنری قیمت‌های فعلی
        """
        # این متد باید به API بازار متصل شود
        # فعلاً یک دیکشنری خالی برمی‌گرداند
        return {}

    def generate_portfolio_report(self, current_prices: Dict[str, float], period: str = 'YTD') -> Dict:
        """
        تولید گزارش جامع پورتفوی
        current_prices: دیکشنری قیمت‌های فعلی
        period: دوره زمانی گزارش ('YTD', 'MTD', '1Y', '3M')
        return: دیکشنری گزارش جامع
        """
        # تعیین بازه زمانی
        end_date = datetime.now()
        if period == 'YTD':
            start_date = datetime(end_date.year, 1, 1)
        elif period == 'MTD':
            start_date = datetime(end_date.year, end_date.month, 1)
        elif period == '1Y':
            start_date = end_date - timedelta(days=365)
        elif period == '3M':
            start_date = end_date - timedelta(days=90)
        else:
            raise ValidationError("دوره زمانی نامعتبر است")

        # جمع‌آوری اطلاعات مختلف
        return {
            'portfolio_metrics': self.calculate_portfolio_metrics(current_prices),
            'performance': self.analyze_performance(start_date, end_date),
            'risk_metrics': self.analyze_risk(self.get_historical_data(start_date, end_date)),
            'top_holdings': self.get_top_holdings(current_prices, limit=5),
            'sector_allocation': self.calculate_sector_allocation(),
            'transaction_summary': self.summarize_transactions(start_date, end_date)
        }

    def get_top_holdings(self, current_prices: Dict[str, float], limit: int = 5) -> List[Dict]:
        """
        دریافت لیست بزرگترین موقعیت‌های پورتفوی
        current_prices: دیکشنری قیمت‌های فعلی
        limit: تعداد موقعیت‌های مورد نظر
        return: لیست موقعیت‌های برتر
        """
        portfolio_value = self.calculate_portfolio_value(current_prices)
        positions = portfolio_value['positions'].items()
        
        # مرتب‌سازی بر اساس ارزش فعلی
        sorted_positions = sorted(
            positions,
            key=lambda x: x[1]['current_value'],
            reverse=True
        )
        
        return [
            {
                'symbol': symbol,
                'value': position['current_value'],
                'weight': position['current_value'] / portfolio_value['total_value'] * 100,
                'profit_loss': position['profit_loss']
            }
            for symbol, position in sorted_positions[:limit]
        ]

    def calculate_sector_allocation(self) -> Dict[str, float]:
        """
        محاسبه توزیع سرمایه در بخش‌های مختلف
        return: دیکشنری درصد تخصیص به هر بخش
        """
        sector_values = {}
        total_value = 0
        
        for symbol, position in self.portfolio.items():
            sector = self.get_stock_sector(symbol)
            value = position['shares'] * position['avg_price']
            
            sector_values[sector] = sector_values.get(sector, 0) + value
            total_value += value
        
        # تبدیل به درصد
        return {
            sector: (value / total_value) * 100
            for sector, value in sector_values.items()
        } if total_value > 0 else {}

    def summarize_transactions(self, start_date: datetime, end_date: datetime) -> Dict:
        """
        خلاصه معاملات در بازه زمانی مشخص
        start_date: تاریخ شروع
        end_date: تاریخ پایان
        return: دیکشنری خلاصه معاملات
        """
        period_transactions = [
            t for t in self.transactions
            if start_date <= t['date'] <= end_date
        ]
        
        buy_count = sum(1 for t in period_transactions if t['type'] == 'buy')
        sell_count = sum(1 for t in period_transactions if t['type'] == 'sell')
        
        buy_volume = sum(t['shares'] for t in period_transactions if t['type'] == 'buy')
        sell_volume = sum(t['shares'] for t in period_transactions if t['type'] == 'sell')
        
        return {
            'total_transactions': len(period_transactions),
            'buy_transactions': buy_count,
            'sell_transactions': sell_count,
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'net_volume': buy_volume - sell_volume
        } 