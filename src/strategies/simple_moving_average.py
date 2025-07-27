"""
Simple Moving Average (SMA) trading strategy
"""

from typing import List
import logging

from src.strategies.base_strategy import BaseStrategy
from src.models.trade import MarketData


class SimpleMovingAverageStrategy(BaseStrategy):
    """Simple Moving Average trading strategy"""
    
    def __init__(self, config, binance_client, short_period: int = 12, long_period: int = 15):
        super().__init__(config, binance_client)
        self.short_period = short_period
        self.long_period = long_period
        self.price_history: List[float] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize price history with recent data for live trading
        self._initialize_price_history()
    
    def _initialize_price_history(self):
        """Initialize price history with recent historical data"""
        try:
            # Get recent klines data (1-hour intervals)
            klines = self.binance_client.get_klines(
                symbol=self.config.default_symbol,
                interval='1h',
                limit=self.long_period + 5  # Get extra data for safety
            )
            
            # Extract closing prices
            for kline in klines:
                close_price = float(kline[4])  # Close price is at index 4
                self.price_history.append(close_price)
            
            self.logger.info(f"Initialized price history with {len(self.price_history)} data points")
            
        except Exception as e:
            self.logger.warning(f"Could not initialize price history: {e}")
            # If we can't get historical data, we'll build it up gradually
            self.logger.info("Price history will be built up gradually from live data")
    
    def should_buy(self, market_data: MarketData) -> bool:
        """Buy when short SMA crosses above long SMA (golden cross)"""
        # Don't add price here - it's handled by the backtest engine
        # self.price_history.append(market_data.price)
        
        # Keep only the last long_period + 1 prices (need extra for crossover detection)
        if len(self.price_history) > self.long_period + 1:
            self.price_history = self.price_history[-(self.long_period + 1):]
        
        # Need enough data for both SMAs
        if len(self.price_history) < self.long_period:
            return False
        
        short_sma = self._calculate_sma(self.short_period)
        long_sma = self._calculate_sma(self.long_period)
        
        # Golden cross: short SMA crosses above long SMA
        if len(self.price_history) >= self.long_period + 1:
            prev_short_sma = self._calculate_sma(self.short_period, -1)
            prev_long_sma = self._calculate_sma(self.long_period, -1)
            
            golden_cross = (prev_short_sma <= prev_long_sma and short_sma > long_sma)
            
            if golden_cross:
                self.logger.info(f"Golden cross detected: Short SMA ({short_sma:.2f}) > Long SMA ({long_sma:.2f})")
                return True
        
        return False
    
    def should_sell(self, market_data: MarketData) -> bool:
        """Sell when short SMA crosses below long SMA (death cross) or take profit/stop loss"""
        # Don't add price here - it's handled by the backtest engine
        # self.price_history.append(market_data.price)
        
        # Keep only the last long_period + 1 prices (need extra for crossover detection)
        if len(self.price_history) > self.long_period + 1:
            self.price_history = self.price_history[-(self.long_period + 1):]
        
        # Need enough data for both SMAs
        if len(self.price_history) < self.long_period:
            return False
        
        short_sma = self._calculate_sma(self.short_period)
        long_sma = self._calculate_sma(self.long_period)
        
        # Death cross: short SMA crosses below long SMA
        if len(self.price_history) >= self.long_period + 1:
            prev_short_sma = self._calculate_sma(self.short_period, -1)
            prev_long_sma = self._calculate_sma(self.long_period, -1)
            
            death_cross = (prev_short_sma >= prev_long_sma and short_sma < long_sma)
            
            if death_cross:
                self.logger.info(f"Death cross detected: Short SMA ({short_sma:.2f}) < Long SMA ({long_sma:.2f})")
                return True
        
        # Check take profit and stop loss
        if self._check_take_profit_stop_loss(market_data):
            return True
        
        return False
    
    def calculate_position_size(self, market_data: MarketData) -> float:
        """Calculate position size based on percentage of total wallet balance"""
        try:
            current_price = market_data.price
            
            # Get total wallet balance
            usdt_balance = self.binance_client.get_balance('USDT')
            btc_balance = self.binance_client.get_balance('BTC')
            total_wallet_usd = usdt_balance + (btc_balance * current_price)
            
            # Calculate trade amount as percentage of total wallet
            trade_amount_usd = total_wallet_usd * (self.config.trade_percentage / 100.0)
            
            # Calculate BTC quantity
            quantity = trade_amount_usd / current_price
            
            # Round to appropriate decimal places
            quantity = round(quantity, 6)  # Default for most crypto pairs
            
            # Ensure minimum trade size ($10)
            if trade_amount_usd < 10:
                self.logger.warning(f"Trade amount ${trade_amount_usd:.2f} below minimum $10")
                return 0.0
            
            # Ensure we have enough USDT
            if trade_amount_usd > usdt_balance:
                self.logger.warning(f"Insufficient USDT balance: ${usdt_balance:.2f} < ${trade_amount_usd:.2f}")
                return 0.0
            
            # Log the calculation
            self.logger.info(f"Position calculation: {self.config.trade_percentage}% of ${total_wallet_usd:.2f} = ${trade_amount_usd:.2f} = {quantity:.6f} BTC")
            
            return quantity
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def get_market_data(self, symbol: str) -> MarketData:
        """Get current market data for live trading"""
        try:
            # Get current price from Binance
            ticker_data = self.binance_client.get_ticker_price(symbol)
            price = float(ticker_data['price'])
            
            # Get current timestamp
            from datetime import datetime
            timestamp = datetime.now()
            
            # Create market data object
            market_data = MarketData(
                symbol=symbol,
                price=price,
                volume=1000.0,  # Default volume for live trading
                timestamp=timestamp
            )
            
            # Update price history for strategy calculations
            self.price_history.append(market_data.price)
            if len(self.price_history) > self.long_period + 1:
                self.price_history = self.price_history[-(self.long_period + 1):]
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            # Return dummy data if API fails
            from datetime import datetime
            return MarketData(
                symbol=symbol,
                price=0.0,
                volume=0.0,
                timestamp=datetime.now()
            )
    
    def _calculate_sma(self, period: int, offset: int = 0) -> float:
        """Calculate Simple Moving Average"""
        if len(self.price_history) < period:
            return 0.0
        
        start_idx = len(self.price_history) - period + offset
        end_idx = len(self.price_history) + offset
        
        if start_idx < 0 or end_idx <= 0:
            return 0.0
        
        prices = self.price_history[start_idx:end_idx]
        return sum(prices) / len(prices)
    
    def _check_take_profit_stop_loss(self, market_data: MarketData) -> bool:
        """Check if take profit or stop loss conditions are met"""
        # This is a simplified version - in practice you'd track entry prices
        # For now, we'll use a simple percentage-based approach
        
        if not self.trades:
            return False
        
        # Get the last buy trade
        last_buy_trade = None
        for trade in reversed(self.trades):
            if trade.side.value == 'BUY':
                last_buy_trade = trade
                break
        
        if not last_buy_trade:
            return False
        
        entry_price = last_buy_trade.price
        current_price = market_data.price
        
        # Calculate percentage change
        price_change_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Check stop loss
        if price_change_percent <= -self.config.stop_loss_percentage:
            self.logger.info(f"Stop loss triggered: {price_change_percent:.2f}%")
            return True
        
        # Check take profit
        if price_change_percent >= self.config.take_profit_percentage:
            self.logger.info(f"Take profit triggered: {price_change_percent:.2f}%")
            return True
        
        return False 