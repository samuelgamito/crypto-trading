"""
Technical indicators for trading strategies
"""

from typing import List, Optional
import logging


class RSIIndicator:
    """Relative Strength Index (RSI) indicator"""
    
    def __init__(self, period: int = 14):
        self.period = period
        self.price_history: List[float] = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_price(self, price: float):
        """Add a new price to the history"""
        self.price_history.append(price)
        
        # Keep only the last period + 1 prices (need extra for RSI calculation)
        if len(self.price_history) > self.period + 1:
            self.price_history = self.price_history[-(self.period + 1):]
    
    def calculate_rsi(self) -> float:
        """Calculate RSI value"""
        if len(self.price_history) < self.period + 1:
            return 50.0  # Neutral RSI when not enough data
        
        # Calculate price changes
        gains = []
        losses = []
        
        for i in range(1, len(self.price_history)):
            change = self.price_history[i] - self.price_history[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0.0)
            else:
                gains.append(0.0)
                losses.append(abs(change))
        
        # Calculate average gain and loss over the period
        avg_gain = sum(gains[-self.period:]) / self.period
        avg_loss = sum(losses[-self.period:]) / self.period
        
        if avg_loss == 0:
            return 100.0  # RSI is 100 when there are no losses
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def is_oversold(self, threshold: float = 30.0) -> bool:
        """Check if RSI indicates oversold condition"""
        rsi = self.calculate_rsi()
        return rsi < threshold
    
    def is_overbought(self, threshold: float = 70.0) -> bool:
        """Check if RSI indicates overbought condition"""
        rsi = self.calculate_rsi()
        return rsi > threshold


class VolumeIndicator:
    """Volume-based indicators"""
    
    def __init__(self, period: int = 20):
        self.period = period
        self.volume_history: List[float] = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_volume(self, volume: float):
        """Add a new volume to the history"""
        self.volume_history.append(volume)
        
        # Keep only the last period volumes
        if len(self.volume_history) > self.period:
            self.volume_history = self.volume_history[-self.period:]
    
    def calculate_volume_sma(self) -> float:
        """Calculate Simple Moving Average of volume"""
        if len(self.volume_history) < self.period:
            return 0.0
        
        return sum(self.volume_history) / len(self.volume_history)
    
    def is_volume_above_average(self, current_volume: float, multiplier: float = 1.0) -> bool:
        """Check if current volume is above the average volume"""
        avg_volume = self.calculate_volume_sma()
        if avg_volume == 0:
            return True  # If no average volume data, assume volume is sufficient
        
        return current_volume > (avg_volume * multiplier)
    
    def get_volume_ratio(self, current_volume: float) -> float:
        """Get the ratio of current volume to average volume"""
        avg_volume = self.calculate_volume_sma()
        if avg_volume == 0:
            return 1.0
        
        return current_volume / avg_volume 