class Stock:
    def __init__(self, symbol, code, last_price=None, closing_price=None, volume=None):
        self.symbol = symbol
        self.code = code
        self.last_price = last_price
        self.closing_price = closing_price
        self.volume = volume
        self.change_percent = self.calculate_change_percent()
    
    def calculate_change_percent(self):
        """محاسبه درصد تغییر قیمت"""
        if not self.last_price or not self.closing_price:
            return 0
        return ((self.closing_price - self.last_price) / self.last_price) * 100
    
    def to_dict(self):
        """تبدیل به دیکشنری"""
        return {
            'symbol': self.symbol,
            'code': self.code,
            'last_price': self.last_price,
            'closing_price': self.closing_price,
            'volume': self.volume,
            'change_percent': self.change_percent
        }
    
    @classmethod
    def from_api_data(cls, symbol, code, api_data):
        """ساخت شیء Stock از داده‌های API"""
        info = api_data.get('closingPriceInfo', {})
        return cls(
            symbol=symbol,
            code=code,
            last_price=info.get('pClosing'),
            closing_price=info.get('pDrCotVal'),
            volume=info.get('qTotTran5J')
        )