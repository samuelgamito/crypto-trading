"""
Main trading bot that orchestrates trading strategies
"""

import time
import logging
from datetime import datetime
from typing import Dict, List

from src.strategies.base_strategy import BaseStrategy
from src.strategies.simple_moving_average import SimpleMovingAverageStrategy
from src.models.trade import MarketData, Trade
from src.api.binance_client import BinanceClient


class TradingBot:
    """Main trading bot that manages trading strategies"""
    
    def __init__(self, config, binance_client: BinanceClient):
        self.config = config
        self.binance_client = binance_client
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize strategy
        self.strategy = SimpleMovingAverageStrategy(config, binance_client)
        
        # Trading state
        self.is_running = False
        self.daily_trades = 0
        self.last_trade_date = None
        self.trades_today: List[Trade] = []
        
        # Performance tracking
        self.total_pnl = 0.0
        self.win_trades = 0
        self.total_trades = 0
    
    def run(self):
        """Main trading loop"""
        self.logger.info("Starting trading bot...")
        print("🚀 Trading bot started! Monitoring BTCBRL...")
        self.is_running = True
        
        try:
            while self.is_running:
                self._update_daily_reset()
                
                # Check if we've reached daily trade limit
                if self.daily_trades >= self.config.max_daily_trades:
                    self.logger.info(f"Daily trade limit reached ({self.daily_trades}/{self.config.max_daily_trades})")
                    print(f"⚠️  Daily trade limit reached ({self.daily_trades}/{self.config.max_daily_trades})")
                    time.sleep(60)  # Wait 1 minute before checking again
                    continue
                
                # Get current market data
                market_data = self.strategy.get_market_data(self.config.default_symbol)
                
                # Sync positions with actual wallet balances
                self.strategy.sync_positions_with_wallet()
                
                # Log current market conditions
                self.logger.info(f"Current {market_data.symbol} price: ${market_data.price:.2f}")
                
                # Get and log wallet balances
                self._log_wallet_balances(market_data.price)
                
                print(f"📊 {market_data.symbol}: {market_data.price:,.2f} | Trades: {self.daily_trades}/{self.config.max_daily_trades}")
                
                # Check for trading signals
                self._process_trading_signals(market_data)
                
                # Sleep before next iteration
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            self.logger.info("Trading bot stopped by user")
        except Exception as e:
            self.logger.error(f"Error in trading bot: {e}")
            raise
        finally:
            self.is_running = False
            self._print_performance_summary()
    
    def stop(self):
        """Stop the trading bot"""
        self.logger.info("Stopping trading bot...")
        self.is_running = False
    
    def _update_daily_reset(self):
        """Reset daily counters if it's a new day"""
        today = datetime.now().date()
        
        if self.last_trade_date != today:
            if self.last_trade_date is not None:
                self.logger.info(f"New trading day. Yesterday's trades: {self.daily_trades}")
            
            self.daily_trades = 0
            self.trades_today = []
            self.last_trade_date = today
    
    def _process_trading_signals(self, market_data: MarketData):
        """Process trading signals and execute trades"""
        try:
            # Check if we should buy
            if self.strategy.should_buy(market_data):
                print("🟢 BUY SIGNAL DETECTED!")
                self._execute_buy_signal(market_data)
            
            # Check if we should sell
            elif self.strategy.should_sell(market_data):
                print("🔴 SELL SIGNAL DETECTED!")
                self._execute_sell_signal(market_data)
            
        except Exception as e:
            self.logger.error(f"Error processing trading signals: {e}")
            print(f"❌ Error processing signals: {e}")
    
    def _execute_buy_signal(self, market_data: MarketData):
        """Execute a buy signal"""
        try:
            # Calculate position size
            quantity = self.strategy.calculate_position_size(market_data)
            
            if quantity <= 0:
                self.logger.warning("Invalid position size calculated")
                return
            
            # Check if we already have a position
            current_position = self.strategy.positions.get('BTC', 0)
            if current_position > 0:
                self.logger.info(f"Already have BTC position: {current_position}")
                print(f"⚠️  Already have BTC position: {current_position}")
                return
            
            # Calculate trade details
            trade_value_brl = quantity * market_data.price
            
            # Get wallet balances for context
            currency_symbol = self.binance_client.get_balance(self.config.currency_symbol)
            btc_balance = self.binance_client.get_balance(self.config.crypto_symbol)
            
            # Get fee information
            fee_summary = self.strategy.fee_manager.get_fee_summary(market_data.symbol)
            estimated_fee = trade_value_brl * fee_summary['taker_fee_rate']
            net_value = trade_value_brl - estimated_fee
            
            # Show detailed buy information
            print(f"\n🟢 BUYING {quantity:.6f} BTC")
            print(f"   💰 Trade Value: {trade_value_brl:,.2f}")
            print(f"   💸 Estimated Fee: {estimated_fee:,.2f} ({fee_summary['taker_fee_percent']:.3f}%)")
            print(f"   💵 Net Value: {net_value:,.2f}")
            print(f"   📊 Price: {market_data.price:,.2f}")
            print(f"   📈 Percentage: {self.config.trade_percentage}% of total wallet")
            print(f"   💵 BRL Balance: {currency_symbol:,.2f}")
            print(f"   🪙 BTC Balance: {btc_balance:.6f} BTC")

            # Execute the buy order
            trade = self.strategy.execute_buy(self.config.default_symbol, quantity)
            
            if trade:
                self.daily_trades += 1
                self.total_trades += 1
                self.trades_today.append(trade)
                
                self.logger.info(f"BUY order executed: {trade.quantity} {market_data.symbol} at ${trade.price:.2f}")
                self.logger.info(f"Daily trades: {self.daily_trades}/{self.config.max_daily_trades}")
                
                print(f"   ✅ BUY ORDER EXECUTED!")
                print(f"   📝 Daily trades: {self.daily_trades}/{self.config.max_daily_trades}")
            
        except Exception as e:
            self.logger.error(f"Error executing buy signal: {e}")
            print(f"   ❌ Error executing buy: {e}")
    
    def _execute_sell_signal(self, market_data: MarketData):
        """Execute a sell signal"""
        try:
            # Check if we have a position to sell
            current_position = self.strategy.positions.get('BTC', 0)
            
            if current_position <= 0:
                self.logger.info(f"No BTC position to sell: {current_position}")
                print(f"⚠️  No BTC position to sell: {current_position}")
                return
            
            # Show detailed sell information
            trade_value_brl = current_position * market_data.price
            
            # Get fee information
            fee_summary = self.strategy.fee_manager.get_fee_summary(market_data.symbol)
            estimated_fee = trade_value_brl * fee_summary['taker_fee_rate']
            net_proceeds = trade_value_brl - estimated_fee
            
            print(f"\n🔴 SELLING {current_position:.6f} BTC")
            print(f"   💰 Trade Value: {trade_value_brl:,.2f}")
            print(f"   💸 Estimated Fee: {estimated_fee:,.2f} ({fee_summary['taker_fee_percent']:.3f}%)")
            print(f"   💵 Net Proceeds: {net_proceeds:,.2f}")
            print(f"   📊 Price: {market_data.price:,.2f}")
            print(f"   🪙 BTC Balance: {current_position:.6f} BTC")
            
            # Execute the sell order
            trade = self.strategy.execute_sell(self.config.default_symbol, current_position)
            
            if trade:
                self.daily_trades += 1
                self.total_trades += 1
                self.trades_today.append(trade)
                
                # Calculate P&L for this trade
                pnl = self._calculate_trade_pnl(trade)
                self.total_pnl += pnl
                
                if pnl > 0:
                    self.win_trades += 1
                
                self.logger.info(f"SELL order executed: {trade.quantity} BTC at {trade.price:.2f}")
                self.logger.info(f"Trade P&L: {pnl:.2f}")
                self.logger.info(f"Daily trades: {self.daily_trades}/{self.config.max_daily_trades}")
                
                print(f"   ✅ SELL ORDER EXECUTED!")
                print(f"   💰 P&L: {pnl:,.2f}")
                print(f"   📝 Daily trades: {self.daily_trades}/{self.config.max_daily_trades}")
            else:
                print(f"   ❌ SELL ORDER FAILED!")
            
        except Exception as e:
            self.logger.error(f"Error executing sell signal: {e}")
            print(f"   ❌ Error executing sell: {e}")
    
    def _calculate_trade_pnl(self, sell_trade: Trade) -> float:
        """Calculate P&L for a completed trade"""
        # Find the corresponding buy trade
        buy_trade = None
        for trade in reversed(self.strategy.trades):
            if trade.symbol == sell_trade.symbol and trade.side.value == 'BUY':
                buy_trade = trade
                break
        
        if not buy_trade:
            return 0.0
        
        # Calculate P&L
        buy_value = buy_trade.quantity * buy_trade.price
        sell_value = sell_trade.quantity * sell_trade.price
        pnl = sell_value - buy_value
        
        return pnl
    
    def _log_wallet_balances(self, current_price: float):
        """Log current wallet balances"""
        try:
            # Get BRL balance
            currency_symbol = self.binance_client.get_balance(self.config.currency_symbol)
            
            # Get BTC balance
            crypto_balance = self.binance_client.get_balance(self.config.crypto_symbol)

            # Calculate total portfolio value in BRL
            crypto_value_currency = crypto_balance * current_price
            total_portfolio_currency = currency_symbol + crypto_value_currency
            
            # Log to file
            self.logger.info(f"Wallet - {self.config.currency_symbol}: {currency_symbol:.2f}, {self.config.crypto_symbol}: {crypto_balance:.6f}  {crypto_value_currency:.2f}), Total: {total_portfolio_currency:.2f}")
            
            # Print to console
            print(f"💰 Wallet: {self.config.currency_symbol} {currency_symbol:,.2f} | {self.config.crypto_symbol} {crypto_balance:.6f}  {crypto_value_currency:,.2f}) | Total: {total_portfolio_currency:,.2f}")
            
        except Exception as e:
            self.logger.error(f"Error getting wallet balances: {e}")
            print(f"❌ Error getting balances: {e}")
    
    def _print_performance_summary(self):
        """Print trading performance summary"""
        self.logger.info("=" * 50)
        self.logger.info("TRADING BOT PERFORMANCE SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Total trades: {self.total_trades}")
        self.logger.info(f"Win rate: {(self.win_trades/self.total_trades*100):.1f}%" if self.total_trades > 0 else "Win rate: N/A")
        self.logger.info(f"Total P&L: {self.total_pnl:.2f}")
        self.logger.info(f"Current positions: {self.strategy.get_position_summary()}")
        
        # Log API statistics
        api_stats = self.binance_client.get_api_statistics()
        self.logger.info(f"API Calls: {api_stats['total_calls']} total, {api_stats['error_calls']} errors, {api_stats['success_rate']:.1f}% success rate")
        
        self.logger.info("=" * 50)
    
    def get_status(self) -> Dict:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'daily_trades': self.daily_trades,
            'max_daily_trades': self.config.max_daily_trades,
            'total_trades': self.total_trades,
            'total_pnl': self.total_pnl,
            'win_rate': (self.win_trades/self.total_trades*100) if self.total_trades > 0 else 0,
            'positions': self.strategy.get_position_summary(),
            'last_trade_date': self.last_trade_date.isoformat() if self.last_trade_date else None
        } 