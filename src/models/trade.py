"""
Data models for trading operations
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"


class OrderStatus(Enum):
    """Order status enumeration"""
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


@dataclass
class Trade:
    """Trade data model"""
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime
    order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.NEW
    commission: float = 0.0
    commission_asset: str = "USDT"
    
    def __post_init__(self):
        if isinstance(self.side, str):
            self.side = OrderSide(self.side)
        if isinstance(self.status, str):
            self.status = OrderStatus(self.status)
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
    
    @property
    def total_value(self) -> float:
        """Calculate total trade value"""
        return self.quantity * self.price
    
    @property
    def net_value(self) -> float:
        """Calculate net trade value after commission"""
        return self.total_value - self.commission


@dataclass
class Position:
    """Position data model"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    timestamp: datetime
    side: OrderSide = OrderSide.BUY
    
    def __post_init__(self):
        if isinstance(self.side, str):
            self.side = OrderSide(self.side)
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
    
    @property
    def market_value(self) -> float:
        """Calculate current market value"""
        return self.quantity * self.current_price
    
    @property
    def unrealized_pnl(self) -> float:
        """Calculate unrealized profit/loss"""
        if self.side == OrderSide.BUY:
            return (self.current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.current_price) * self.quantity
    
    @property
    def unrealized_pnl_percentage(self) -> float:
        """Calculate unrealized profit/loss percentage"""
        if self.entry_price == 0:
            return 0.0
        return (self.unrealized_pnl / (self.entry_price * self.quantity)) * 100


@dataclass
class MarketData:
    """Market data model"""
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    high_24h: float = 0.0
    low_24h: float = 0.0
    change_24h: float = 0.0
    change_percent_24h: float = 0.0
    quote_volume: float = 0.0  # Volume in quote currency (e.g., USDT)
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00')) 