"""
Data loader for backtesting - fetches historical data from Binance
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from src.models.trade import MarketData
from src.api.binance_client import BinanceClient


class HistoricalDataLoader:
    """Load historical market data for backtesting"""
    
    def __init__(self, binance_client: BinanceClient):
        self.binance_client = binance_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_historical_data(self, symbol: str, interval: str = '1h', 
                           days: int = 30) -> List[MarketData]:
        """
        Load historical data for backtesting
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            interval: Time interval ('1m', '5m', '15m', '1h', '4h', '1d')
            days: Number of days to load
            
        Returns:
            List of MarketData objects
        """
        try:
            self.logger.info(f"Loading {days} days of {interval} data for {symbol}")
            
            # Calculate start time
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Get klines data
            klines = self.binance_client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=1000  # Maximum allowed by Binance
            )
            
            # Convert klines to MarketData objects
            market_data_list = []
            for kline in klines:
                # Binance kline format: [open_time, open, high, low, close, volume, close_time, ...]
                timestamp = datetime.fromtimestamp(kline[0] / 1000)
                
                # Only include data within our date range
                if start_time <= timestamp <= end_time:
                    market_data = MarketData(
                        symbol=symbol,
                        price=float(kline[4]),  # Close price
                        volume=float(kline[5]),
                        timestamp=timestamp,
                        high_24h=float(kline[2]),
                        low_24h=float(kline[3])
                    )
                    market_data_list.append(market_data)
            
            self.logger.info(f"Loaded {len(market_data_list)} data points")
            return market_data_list
            
        except Exception as e:
            self.logger.error(f"Error loading historical data: {e}")
            raise
    
    def load_recent_data(self, symbol: str, interval: str = '1h', 
                        hours: int = 24) -> List[MarketData]:
        """
        Load recent data for quick testing
        
        Args:
            symbol: Trading symbol
            interval: Time interval
            hours: Number of hours to load
            
        Returns:
            List of MarketData objects
        """
        return self.load_historical_data(symbol, interval, days=hours//24 + 1)
    
    def load_custom_period(self, symbol: str, interval: str, 
                          start_date: datetime, end_date: datetime) -> List[MarketData]:
        """
        Load data for a custom time period
        
        Args:
            symbol: Trading symbol
            interval: Time interval
            start_date: Start date
            end_date: End date
            
        Returns:
            List of MarketData objects
        """
        try:
            self.logger.info(f"Loading data from {start_date} to {end_date} for {symbol}")
            
            # Get klines data
            klines = self.binance_client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=1000
            )
            
            # Convert klines to MarketData objects
            market_data_list = []
            for kline in klines:
                timestamp = datetime.fromtimestamp(kline[0] / 1000)
                
                # Only include data within our date range
                if start_date <= timestamp <= end_date:
                    market_data = MarketData(
                        symbol=symbol,
                        price=float(kline[4]),  # Close price
                        volume=float(kline[5]),
                        timestamp=timestamp,
                        high_24h=float(kline[2]),
                        low_24h=float(kline[3])
                    )
                    market_data_list.append(market_data)
            
            self.logger.info(f"Loaded {len(market_data_list)} data points")
            return market_data_list
            
        except Exception as e:
            self.logger.error(f"Error loading custom period data: {e}")
            raise
    
    def get_available_intervals(self) -> List[str]:
        """Get list of available time intervals"""
        return ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validate if a symbol exists on Binance"""
        try:
            symbol_info = self.binance_client.get_symbol_info(symbol)
            return symbol_info is not None
        except Exception:
            return False 