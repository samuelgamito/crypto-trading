#!/usr/bin/env python3
"""
Backtesting script for crypto trading strategies
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.config import Config
from src.api.binance_client import BinanceClient
from src.strategies.simple_moving_average import SimpleMovingAverageStrategy
from src.backtesting.backtest_engine import BacktestEngine
from src.backtesting.data_loader import HistoricalDataLoader
from src.utils.logger import setup_logger


def run_backtest(symbol: str = "BTCUSDT", interval: str = "1h", days: int = 30, 
                initial_balance: float = 10000.0, short_period: int = 10, 
                long_period: int = 20):
    """
    Run a backtest with the specified parameters
    
    Args:
        symbol: Trading symbol
        interval: Time interval
        days: Number of days to test
        initial_balance: Starting balance
        short_period: Short SMA period
        long_period: Long SMA period
    """
    # Setup logging
    logger = setup_logger()
    logger.info("Starting backtest...")
    
    try:
        # Load configuration
        config = Config()
        logger.info(f"Configuration loaded. Testnet: {config.testnet}")
        
        # Initialize Binance client
        binance_client = BinanceClient(config)
        logger.info("Binance client initialized")
        
        # Initialize data loader
        data_loader = HistoricalDataLoader(binance_client)
        
        # Validate symbol
        if not data_loader.validate_symbol(symbol):
            logger.error(f"Symbol {symbol} not found on Binance")
            return
        
        # Load historical data
        logger.info(f"Loading {days} days of {interval} data for {symbol}")
        historical_data = data_loader.load_historical_data(symbol, interval, days)
        
        if not historical_data:
            logger.error("No historical data loaded")
            return
        
        # Initialize strategy
        strategy = SimpleMovingAverageStrategy(
            config, 
            binance_client, 
            short_period=short_period, 
            long_period=long_period
        )
        logger.info(f"Strategy initialized: SMA({short_period}, {long_period})")
        
        # Initialize backtest engine
        backtest_engine = BacktestEngine(initial_balance=initial_balance)
        logger.info(f"Backtest engine initialized with ${initial_balance:.2f}")
        
        # Run backtest
        result = backtest_engine.run_backtest(strategy, historical_data, symbol)
        
        # Print results
        print_backtest_results(result, symbol, interval, days)
        
    except Exception as e:
        logger.error(f"Error in backtest: {e}")
        raise


def print_backtest_results(result, symbol: str, interval: str, days: int):
    """Print formatted backtest results"""
    print("\n" + "="*60)
    print("BACKTEST RESULTS")
    print("="*60)
    print(f"Symbol: {symbol}")
    print(f"Period: {days} days ({interval} intervals)")
    print(f"Strategy: Simple Moving Average")
    print()
    
    print("PERFORMANCE METRICS:")
    print(f"  Initial Balance: ${result.initial_balance:,.2f}")
    print(f"  Final Balance:   ${result.final_balance:,.2f}")
    print(f"  Total Return:    {result.total_return:+.2f}%")
    print(f"  Total P&L:       ${result.total_pnl:+,.2f}")
    print()
    
    print("TRADING STATISTICS:")
    print(f"  Total Trades:    {result.total_trades}")
    print(f"  Winning Trades:  {result.winning_trades}")
    print(f"  Losing Trades:   {result.losing_trades}")
    print(f"  Win Rate:        {result.win_rate:.1f}%")
    print()
    
    print("RISK METRICS:")
    print(f"  Max Drawdown:    {result.max_drawdown:.2f}%")
    print(f"  Sharpe Ratio:    {result.sharpe_ratio:.3f}")
    print()
    
    if result.trades:
        print("TRADE HISTORY:")
        print("-" * 60)
        for i, trade in enumerate(result.trades[-10:], 1):  # Show last 10 trades
            print(f"{i:2d}. {trade.side.value:4s} {trade.quantity:8.6f} {trade.symbol} @ ${trade.price:8.2f}")
        if len(result.trades) > 10:
            print(f"... and {len(result.trades) - 10} more trades")
    
    print("="*60)


def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description='Backtest crypto trading strategies')
    parser.add_argument('--symbol', default='BTCUSDT', help='Trading symbol (default: BTCUSDT)')
    parser.add_argument('--interval', default='1h', help='Time interval (default: 1h)')
    parser.add_argument('--days', type=int, default=30, help='Number of days to test (default: 30)')
    parser.add_argument('--balance', type=float, default=10000.0, help='Initial balance (default: 10000)')
    parser.add_argument('--short-period', type=int, default=10, help='Short SMA period (default: 10)')
    parser.add_argument('--long-period', type=int, default=20, help='Long SMA period (default: 20)')
    
    args = parser.parse_args()
    
    # Run backtest with provided arguments
    run_backtest(
        symbol=args.symbol,
        interval=args.interval,
        days=args.days,
        initial_balance=args.balance,
        short_period=args.short_period,
        long_period=args.long_period
    )


if __name__ == "__main__":
    main() 