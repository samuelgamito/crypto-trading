"""
Logging utilities for the crypto trading bot
"""

import logging
import os
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = 'crypto_trading_bot', log_level: str = 'INFO', 
                log_file: str = 'logs/trading_bot.log') -> logging.Logger:
    """
    Setup and configure logger for the trading bot
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler for detailed logging
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler for simple logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (optional)
        
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(name)
    return logging.getLogger('crypto_trading_bot')


def log_trade(logger: logging.Logger, trade_type: str, symbol: str, 
              quantity: float, price: float, order_id: str = None):
    """
    Log a trade execution
    
    Args:
        logger: Logger instance
        trade_type: Type of trade (BUY/SELL)
        symbol: Trading symbol
        quantity: Trade quantity
        price: Trade price
        order_id: Order ID (optional)
    """
    log_message = f"TRADE EXECUTED: {trade_type} {quantity} {symbol} @ ${price:.2f}"
    if order_id:
        log_message += f" (Order ID: {order_id})"
    
    logger.info(log_message)


def log_market_data(logger: logging.Logger, symbol: str, price: float, 
                   volume: float = None, change_24h: float = None):
    """
    Log market data
    
    Args:
        logger: Logger instance
        symbol: Trading symbol
        price: Current price
        volume: Trading volume (optional)
        change_24h: 24h price change (optional)
    """
    log_message = f"MARKET DATA: {symbol} = ${price:.2f}"
    if volume:
        log_message += f" | Volume: {volume:.2f}"
    if change_24h:
        log_message += f" | 24h Change: {change_24h:+.2f}%"
    
    logger.debug(log_message)


def log_performance(logger: logging.Logger, total_trades: int, win_rate: float, 
                   total_pnl: float, positions: dict):
    """
    Log performance metrics
    
    Args:
        logger: Logger instance
        total_trades: Total number of trades
        win_rate: Win rate percentage
        total_pnl: Total profit/loss
        positions: Current positions
    """
    logger.info("=" * 50)
    logger.info("PERFORMANCE SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total Trades: {total_trades}")
    logger.info(f"Win Rate: {win_rate:.1f}%")
    logger.info(f"Total P&L: ${total_pnl:.2f}")
    logger.info(f"Current Positions: {positions}")
    logger.info("=" * 50) 