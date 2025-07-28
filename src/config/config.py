"""
Configuration management for the crypto trading bot
"""

import os
from dotenv import load_dotenv
from pathlib import Path


class Config:
    """Configuration class for the trading bot"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Binance API Configuration
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.secret_key = os.getenv('BINANCE_SECRET_KEY')
        print(os.getenv('BINANCE_TESTNET', 'true').lower())
        self.testnet = os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'
        
        # Trading Configuration
        self.currency_symbol = os.getenv('CURRENCY_SYMBOL', 'BRL')
        self.crypto_symbol = os.getenv('CRYPTO_SYMBOL', 'BTC')
        self.default_symbol = f"{self.crypto_symbol}{self.currency_symbol}"
        self.trade_amount = float(os.getenv('TRADE_AMOUNT', '0.001'))
        self.max_position_size = float(os.getenv('MAX_POSITION_SIZE', '0.01'))
        self.trade_percentage = float(os.getenv('TRADE_PERCENTAGE', '5.0'))  # Percentage of total wallet
        
        # Risk Management
        self.stop_loss_percentage = float(os.getenv('STOP_LOSS_PERCENTAGE', '2.0'))
        self.take_profit_percentage = float(os.getenv('TAKE_PROFIT_PERCENTAGE', '5.0'))
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', '10'))
        
        # Profit Management
        self.min_profit_percentage = float(os.getenv('MIN_PROFIT_PERCENTAGE', '1.5'))  # Minimum profit before selling
        self.min_holding_time_minutes = int(os.getenv('MIN_HOLDING_TIME_MINUTES', '30'))  # Minimum time to hold position
        self.max_position_age_hours = int(os.getenv('MAX_POSITION_AGE_HOURS', '24'))  # Maximum time to hold position
        
        # Fee Management
        self.include_fees = os.getenv('INCLUDE_FEES', 'true').lower() == 'true'
        self.fee_buffer_percentage = float(os.getenv('FEE_BUFFER_PERCENTAGE', '0.2'))  # Extra buffer for fees
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/trading_bot.log')
        
        # MongoDB Configuration
        self.mongo_connection_string = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
        self.mongo_database = os.getenv('MONGO_DATABASE', 'crypto_trading')
        self.mongo_username = os.getenv('MONGO_USERNAME')
        self.mongo_password = os.getenv('MONGO_PASSWORD')
        self.enable_mongo_logging = os.getenv('ENABLE_MONGO_LOGGING', 'true').lower() == 'true'
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that required configuration is present"""
        if not self.api_key or not self.secret_key:
            raise ValueError("BINANCE_API_KEY and BINANCE_SECRET_KEY must be set")
        
        if self.trade_amount <= 0:
            raise ValueError("TRADE_AMOUNT must be greater than 0")
        
        if self.max_position_size <= 0:
            raise ValueError("MAX_POSITION_SIZE must be greater than 0")
    
    def get_binance_url(self):
        """Get the appropriate Binance API URL based on testnet setting"""
        if self.testnet:
            return "https://testnet.binance.vision"
        return "https://api.binance.com"
    
    def __str__(self):
        return f"Config(symbol={self.default_symbol}, testnet={self.testnet})" 