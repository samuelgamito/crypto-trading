"""
Position tracking model for managing buy/sell timing and profit calculations
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class Position:
    """Tracks a trading position with timing and profit calculations"""
    
    def __init__(self, symbol: str, quantity: float, buy_price: float, buy_time: datetime):
        self.symbol = symbol
        self.quantity = quantity
        self.buy_price = buy_price
        self.buy_time = buy_time
        self.buy_value = quantity * buy_price
        self.fees_paid = 0.0
        
    def calculate_profit_percentage(self, current_price: float, sell_fee_rate: float = 0.001) -> float:
        """Calculate profit percentage including fees"""
        current_value = self.quantity * current_price
        sell_fees = current_value * sell_fee_rate
        total_fees = self.fees_paid + sell_fees
        net_profit = current_value - self.buy_value - total_fees
        profit_percentage = (net_profit / self.buy_value) * 100
        return profit_percentage
    
    def calculate_net_profit(self, current_price: float, sell_fee_rate: float = 0.001) -> float:
        """Calculate net profit in currency units"""
        current_value = self.quantity * current_price
        sell_fees = current_value * sell_fee_rate
        total_fees = self.fees_paid + sell_fees
        net_profit = current_value - self.buy_value - total_fees
        return net_profit
    
    def get_holding_time_minutes(self) -> int:
        """Get how long the position has been held in minutes"""
        now = datetime.now()
        holding_time = now - self.buy_time
        return int(holding_time.total_seconds() / 60)
    
    def get_holding_time_hours(self) -> float:
        """Get how long the position has been held in hours"""
        return self.get_holding_time_minutes() / 60.0
    
    def should_sell_for_profit(self, current_price: float, min_profit_percentage: float, sell_fee_rate: float = 0.001) -> bool:
        """Check if position should be sold for profit"""
        profit_percentage = self.calculate_profit_percentage(current_price, sell_fee_rate)
        return profit_percentage >= min_profit_percentage
    
    def should_sell_for_time(self, max_holding_hours: int) -> bool:
        """Check if position should be sold due to time limit"""
        return self.get_holding_time_hours() >= max_holding_hours
    
    def should_sell_for_stop_loss(self, current_price: float, stop_loss_percentage: float, sell_fee_rate: float = 0.001) -> bool:
        """Check if position should be sold for stop loss"""
        profit_percentage = self.calculate_profit_percentage(current_price, sell_fee_rate)
        return profit_percentage <= -stop_loss_percentage
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert position to dictionary for MongoDB storage"""
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'buy_price': self.buy_price,
            'buy_time': self.buy_time.isoformat(),
            'buy_value': self.buy_value,
            'fees_paid': self.fees_paid,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Position':
        """Create position from dictionary (for MongoDB recovery)"""
        buy_time = datetime.fromisoformat(data['buy_time'])
        position = cls(
            symbol=data['symbol'],
            quantity=data['quantity'],
            buy_price=data['buy_price'],
            buy_time=buy_time
        )
        position.fees_paid = data.get('fees_paid', 0.0)
        return position 