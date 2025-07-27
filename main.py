#!/usr/bin/env python3
"""
Crypto Trading Bot - Main Entry Point
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.config import Config
from src.api.binance_client import BinanceClient
from src.strategies.trading_bot import TradingBot
from src.utils.logger import setup_logger


def main():
    """Main application entry point"""
    try:
        # Setup logging
        logger = setup_logger()
        logger.info("Starting Crypto Trading Bot...")
        
        # Load configuration
        config = Config()
        logger.info(f"Configuration loaded. Trading symbol: {config.default_symbol}")
        
        # Initialize Binance client
        binance_client = BinanceClient(config)
        logger.info("Binance client initialized")
        
        # Initialize trading bot
        trading_bot = TradingBot(config, binance_client)
        logger.info("Trading bot initialized")
        
        # Start trading
        trading_bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 