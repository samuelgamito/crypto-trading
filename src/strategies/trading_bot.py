"""
Enhanced trading bot that orchestrates multiple strategies for better performance
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple

from src.strategies.base_strategy import BaseStrategy
from src.strategies.simple_moving_average import SimpleMovingAverageStrategy
from src.strategies.rsi_volume_strategy import RSIVolumeStrategy
from src.models.trade import MarketData, Trade
from src.api.binance_client import BinanceClient


class TradingBot:
    """Enhanced trading bot that manages multiple strategies for better performance"""
    
    def __init__(self, config, binance_client: BinanceClient):
        self.config = config
        self.binance_client = binance_client
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize both strategies
        self.sma_strategy = SimpleMovingAverageStrategy(config, binance_client)
        self.rsi_volume_strategy = RSIVolumeStrategy(config, binance_client)
        
        # Use SMA strategy as primary (for position management)
        self.strategy = self.sma_strategy
        
        # Trading state
        self.is_running = False
        self.daily_trades = 0
        self.last_trade_date = None
        self.trades_today: List[Trade] = []
        
        # Performance tracking
        self.total_pnl = 0.0
        self.win_trades = 0
        self.total_trades = 0
        
        # Strategy performance tracking
        self.sma_signals = 0
        self.rsi_signals = 0
        self.combined_signals = 0
    
    def run(self):
        """Enhanced trading loop with multiple strategies"""
        self.logger.info("Starting enhanced trading bot with dual strategies...")
        print("🚀 Enhanced trading bot started! Using SMA + RSI + Volume strategies...")
        print("📊 Monitoring BTCBRL with dual strategy analysis...")
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
                
                # Get current market data (shared between strategies)
                market_data = self.strategy.get_market_data(self.config.default_symbol)
                
                # Update both strategies with market data
                self._update_strategies(market_data)
                
                # Sync positions with actual wallet balances
                self.strategy.sync_positions_with_wallet()
                
                # Log current market conditions with strategy insights
                self._log_market_conditions(market_data)
                
                # Get and log wallet balances
                self._log_wallet_balances(market_data.price)
                
                # Display enhanced status with both strategies
                self._display_enhanced_status(market_data)
                
                # Check for trading signals using both strategies
                self._process_enhanced_trading_signals(market_data)
                
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
    
    def _update_strategies(self, market_data: MarketData):
        """Update both strategies with current market data"""
        try:
            # Update RSI strategy with market data
            self.rsi_volume_strategy.rsi_indicator.add_price(market_data.price)
            self.rsi_volume_strategy.volume_indicator.add_volume(market_data.quote_volume)
        except Exception as e:
            self.logger.error(f"Error updating strategies: {e}")
    
    def _log_market_conditions(self, market_data: MarketData):
        """Log market conditions with insights from both strategies"""
        self.logger.info(f"Current {market_data.symbol} price: ${market_data.price:.2f}")
        
        # Log SMA conditions
        short_sma = self.sma_strategy._calculate_sma(self.sma_strategy.short_period)
        long_sma = self.sma_strategy._calculate_sma(self.sma_strategy.long_period)
        self.logger.info(f"SMA - Short: {short_sma:.2f}, Long: {long_sma:.2f}")
        
        # Log RSI and Volume conditions
        rsi_value = self.rsi_volume_strategy.rsi_indicator.calculate_rsi()
        avg_volume = self.rsi_volume_strategy.volume_indicator.calculate_volume_sma()
        volume_ratio = self.rsi_volume_strategy.volume_indicator.get_volume_ratio(market_data.quote_volume)
        self.logger.info(f"RSI: {rsi_value:.2f}, Volume: {volume_ratio:.2f}x average")
    
    def _display_enhanced_status(self, market_data: MarketData):
        """Display enhanced status with both strategies"""
        # SMA information
        short_sma = self.sma_strategy._calculate_sma(self.sma_strategy.short_period)
        long_sma = self.sma_strategy._calculate_sma(self.sma_strategy.long_period)
        
        # RSI and Volume information
        rsi_value = self.rsi_volume_strategy.rsi_indicator.calculate_rsi()
        volume_ratio = self.rsi_volume_strategy.volume_indicator.get_volume_ratio(market_data.quote_volume)
        
        print(f"📊 {market_data.symbol}: {market_data.price:,.2f}")
        print(f"   📈 SMA: {short_sma:.2f}/{long_sma:.2f} | RSI: {rsi_value:.1f} | Vol: {volume_ratio:.1f}x")
        print(f"   🎯 Trades: {self.daily_trades}/{self.config.max_daily_trades}")
    
    def _get_strategy_signals(self, market_data: MarketData) -> Tuple[bool, bool, bool, bool]:
        """Get signals from both strategies"""
        # SMA signals
        sma_buy = self.sma_strategy.should_buy(market_data)
        sma_sell = self.sma_strategy.should_sell(market_data)
        
        # RSI + Volume signals
        rsi_buy = self.rsi_volume_strategy.should_buy(market_data)
        rsi_sell = self.rsi_volume_strategy.should_sell(market_data)
        
        return sma_buy, sma_sell, rsi_buy, rsi_sell
    
    def _process_enhanced_trading_signals(self, market_data: MarketData):
        """Process trading signals using both strategies for better performance"""
        try:
            # Get signals from both strategies
            sma_buy, sma_sell, rsi_buy, rsi_sell = self._get_strategy_signals(market_data)
            
            # Check if we have any open positions
            has_position = self.strategy.has_position()
            
            if not has_position:
                # Enhanced buy logic
                buy_signal = self._evaluate_buy_signals(sma_buy, rsi_buy, market_data)
                if buy_signal:
                    self._execute_enhanced_buy_signal(market_data, sma_buy, rsi_buy)
            else:
                # Enhanced sell logic
                sell_signal = self._evaluate_sell_signals(sma_sell, rsi_sell, market_data)
                if sell_signal:
                    self._execute_enhanced_sell_signal(market_data, sma_sell, rsi_sell)
                    
        except Exception as e:
            self.logger.error(f"Error processing enhanced trading signals: {e}")
            print(f"❌ Error processing signals: {e}")
    
    def _evaluate_buy_signals(self, sma_buy: bool, rsi_buy: bool, market_data: MarketData) -> bool:
        """Evaluate buy signals from both strategies"""
        # Strong buy: Both strategies agree
        if sma_buy and rsi_buy:
            self.combined_signals += 1
            print("🟢 STRONG BUY SIGNAL! Both SMA and RSI+Volume agree!")
            return True
        
        # Moderate buy: SMA signals but RSI is neutral (not overbought)
        elif sma_buy and not self.rsi_volume_strategy.rsi_indicator.is_overbought():
            self.sma_signals += 1
            print("🟡 MODERATE BUY SIGNAL! SMA Golden Cross with neutral RSI")
            return True
        
        # Conservative buy: RSI shows oversold with volume confirmation
        elif rsi_buy and self.rsi_volume_strategy.rsi_indicator.is_oversold():
            self.rsi_signals += 1
            print("🟡 CONSERVATIVE BUY SIGNAL! RSI oversold with volume confirmation")
            return True
        
        return False
    
    def _evaluate_sell_signals(self, sma_sell: bool, rsi_sell: bool, market_data: MarketData) -> bool:
        """Evaluate sell signals from both strategies"""
        # Strong sell: Both strategies agree
        if sma_sell and rsi_sell:
            self.combined_signals += 1
            print("🔴 STRONG SELL SIGNAL! Both SMA and RSI+Volume agree!")
            return True
        
        # Moderate sell: SMA signals but RSI is neutral (not oversold)
        elif sma_sell and not self.rsi_volume_strategy.rsi_indicator.is_oversold():
            self.sma_signals += 1
            print("🟡 MODERATE SELL SIGNAL! SMA Death Cross with neutral RSI")
            return True
        
        # Conservative sell: RSI shows overbought with volume confirmation
        elif rsi_sell and self.rsi_volume_strategy.rsi_indicator.is_overbought():
            self.rsi_signals += 1
            print("🟡 CONSERVATIVE SELL SIGNAL! RSI overbought with volume confirmation")
            return True
        
        return False
    
    def stop(self):
        """Stop the trading bot"""
        self.logger.info("Stopping enhanced trading bot...")
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
    
    def _execute_enhanced_buy_signal(self, market_data: MarketData, sma_buy: bool, rsi_buy: bool):
        """Execute enhanced buy signal with strategy information"""
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
            
            # Get strategy insights
            short_sma = self.sma_strategy._calculate_sma(self.sma_strategy.short_period)
            long_sma = self.sma_strategy._calculate_sma(self.sma_strategy.long_period)
            rsi_value = self.rsi_volume_strategy.rsi_indicator.calculate_rsi()
            volume_ratio = self.rsi_volume_strategy.volume_indicator.get_volume_ratio(market_data.quote_volume)
            
            # Show enhanced buy information
            print(f"\n🟢 ENHANCED BUY SIGNAL - {quantity:.6f} BTC")
            print(f"   📊 Price: {market_data.price:,.2f}")
            print(f"   💰 Trade Value: {trade_value_brl:,.2f} | Net: {net_value:,.2f}")
            print(f"   📈 Strategy Signals:")
            print(f"      SMA: {'✅' if sma_buy else '❌'} ({short_sma:.2f}/{long_sma:.2f})")
            print(f"      RSI: {'✅' if rsi_buy else '❌'} ({rsi_value:.1f}) | Vol: {volume_ratio:.1f}x")
            print(f"   💵 BRL: {currency_symbol:,.2f} | 🪙 BTC: {btc_balance:.6f}")

            # Execute the buy order
            trade = self.strategy.execute_buy(self.config.default_symbol, quantity)
            
            if trade:
                self.daily_trades += 1
                self.total_trades += 1
                self.trades_today.append(trade)
                
                self.logger.info(f"Enhanced BUY order executed: {trade.quantity:.8f} {market_data.symbol} at ${trade.price:.2f}")
                self.logger.info(f"SMA Signal: {sma_buy}, RSI Signal: {rsi_buy}")
                self.logger.info(f"Daily trades: {self.daily_trades}/{self.config.max_daily_trades}")
                
                print(f"   ✅ ENHANCED BUY ORDER EXECUTED!")
                print(f"   📝 Daily trades: {self.daily_trades}/{self.config.max_daily_trades}")
            
        except Exception as e:
            self.logger.error(f"Error executing enhanced buy signal: {e}")
            print(f"   ❌ Error executing buy: {e}")
    
    def _execute_enhanced_sell_signal(self, market_data: MarketData, sma_sell: bool, rsi_sell: bool):
        """Execute enhanced sell signal with strategy information"""
        try:
            # Check if we have a position to sell
            current_position = self.strategy.positions.get('BTC', 0)
            
            if current_position <= 0:
                self.logger.info(f"No BTC position to sell: {current_position:.8f}")
                print(f"⚠️  No BTC position to sell: {current_position:.8f}")
                return
            
            # Calculate trade details
            trade_value_brl = current_position * market_data.price
            
            # Get fee information
            fee_summary = self.strategy.fee_manager.get_fee_summary(market_data.symbol)
            estimated_fee = trade_value_brl * fee_summary['taker_fee_rate']
            net_proceeds = trade_value_brl - estimated_fee
            
            # Get strategy insights
            short_sma = self.sma_strategy._calculate_sma(self.sma_strategy.short_period)
            long_sma = self.sma_strategy._calculate_sma(self.sma_strategy.long_period)
            rsi_value = self.rsi_volume_strategy.rsi_indicator.calculate_rsi()
            volume_ratio = self.rsi_volume_strategy.volume_indicator.get_volume_ratio(market_data.quote_volume)
            
            # Show enhanced sell information
            print(f"\n🔴 ENHANCED SELL SIGNAL - {current_position:.6f} BTC")
            print(f"   📊 Price: {market_data.price:,.2f}")
            print(f"   💰 Trade Value: {trade_value_brl:,.2f} | Net: {net_proceeds:,.2f}")
            print(f"   📈 Strategy Signals:")
            print(f"      SMA: {'✅' if sma_sell else '❌'} ({short_sma:.2f}/{long_sma:.2f})")
            print(f"      RSI: {'✅' if rsi_sell else '❌'} ({rsi_value:.1f}) | Vol: {volume_ratio:.1f}x")
            
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
                
                self.logger.info(f"Enhanced SELL order executed: {trade.quantity:.8f} BTC at {trade.price:.2f}")
                self.logger.info(f"SMA Signal: {sma_sell}, RSI Signal: {rsi_sell}")
                self.logger.info(f"Trade P&L: {pnl:.2f}")
                self.logger.info(f"Daily trades: {self.daily_trades}/{self.config.max_daily_trades}")
                
                print(f"   ✅ ENHANCED SELL ORDER EXECUTED!")
                print(f"   💰 P&L: {pnl:,.2f}")
                print(f"   📝 Daily trades: {self.daily_trades}/{self.config.max_daily_trades}")
            else:
                print(f"   ❌ ENHANCED SELL ORDER FAILED!")
            
        except Exception as e:
            self.logger.error(f"Error executing enhanced sell signal: {e}")
            print(f"   ❌ Error executing sell: {e}")
    
    def _execute_buy_signal(self, market_data: MarketData):
        """Legacy buy signal method (kept for compatibility)"""
        self._execute_enhanced_buy_signal(market_data, False, False)
    
    def _execute_sell_signal(self, market_data: MarketData):
        """Legacy sell signal method (kept for compatibility)"""
        self._execute_enhanced_sell_signal(market_data, False, False)
    

    
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
        """Print enhanced trading performance summary"""
        self.logger.info("=" * 60)
        self.logger.info("ENHANCED TRADING BOT PERFORMANCE SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total trades: {self.total_trades}")
        self.logger.info(f"Win rate: {(self.win_trades/self.total_trades*100):.1f}%" if self.total_trades > 0 else "Win rate: N/A")
        self.logger.info(f"Total P&L: {self.total_pnl:.2f}")
        self.logger.info(f"Current positions: {self.strategy.get_position_summary()}")
        
        # Strategy performance breakdown
        self.logger.info("=" * 40)
        self.logger.info("STRATEGY PERFORMANCE BREAKDOWN")
        self.logger.info("=" * 40)
        self.logger.info(f"SMA Signals: {self.sma_signals}")
        self.logger.info(f"RSI+Volume Signals: {self.rsi_signals}")
        self.logger.info(f"Combined Signals: {self.combined_signals}")
        
        total_signals = self.sma_signals + self.rsi_signals + self.combined_signals
        if total_signals > 0:
            self.logger.info(f"SMA Signal Rate: {(self.sma_signals/total_signals*100):.1f}%")
            self.logger.info(f"RSI Signal Rate: {(self.rsi_signals/total_signals*100):.1f}%")
            self.logger.info(f"Combined Signal Rate: {(self.combined_signals/total_signals*100):.1f}%")
        
        # Log API statistics
        api_stats = self.binance_client.get_api_statistics()
        self.logger.info("=" * 40)
        self.logger.info("API PERFORMANCE")
        self.logger.info("=" * 40)
        self.logger.info(f"API Calls: {api_stats['total_calls']} total, {api_stats['error_calls']} errors, {api_stats['success_rate']:.1f}% success rate")
        
        self.logger.info("=" * 60)
        
        # Print to console
        print("\n" + "=" * 60)
        print("📊 ENHANCED TRADING BOT PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"Total Trades: {self.total_trades}")
        print(f"Win Rate: {(self.win_trades/self.total_trades*100):.1f}%" if self.total_trades > 0 else "Win Rate: N/A")
        print(f"Total P&L: {self.total_pnl:+.2f}")
        print(f"Current Positions: {self.strategy.get_position_summary()}")
        
        print("\n" + "=" * 40)
        print("📈 STRATEGY PERFORMANCE BREAKDOWN")
        print("=" * 40)
        print(f"SMA Signals: {self.sma_signals}")
        print(f"RSI+Volume Signals: {self.rsi_signals}")
        print(f"Combined Signals: {self.combined_signals}")
        
        if total_signals > 0:
            print(f"SMA Signal Rate: {(self.sma_signals/total_signals*100):.1f}%")
            print(f"RSI Signal Rate: {(self.rsi_signals/total_signals*100):.1f}%")
            print(f"Combined Signal Rate: {(self.combined_signals/total_signals*100):.1f}%")
        
        print("\n" + "=" * 40)
        print("🔌 API PERFORMANCE")
        print("=" * 40)
        print(f"API Calls: {api_stats['total_calls']} total")
        print(f"Success Rate: {api_stats['success_rate']:.1f}%")
        print("=" * 60)
    
    def get_status(self) -> Dict:
        """Get enhanced bot status with strategy information"""
        total_signals = self.sma_signals + self.rsi_signals + self.combined_signals
        
        return {
            'is_running': self.is_running,
            'daily_trades': self.daily_trades,
            'max_daily_trades': self.config.max_daily_trades,
            'total_trades': self.total_trades,
            'total_pnl': self.total_pnl,
            'win_rate': (self.win_trades/self.total_trades*100) if self.total_trades > 0 else 0,
            'positions': self.strategy.get_position_summary(),
            'last_trade_date': self.last_trade_date.isoformat() if self.last_trade_date else None,
            'strategy_performance': {
                'sma_signals': self.sma_signals,
                'rsi_signals': self.rsi_signals,
                'combined_signals': self.combined_signals,
                'total_signals': total_signals,
                'sma_signal_rate': (self.sma_signals/total_signals*100) if total_signals > 0 else 0,
                'rsi_signal_rate': (self.rsi_signals/total_signals*100) if total_signals > 0 else 0,
                'combined_signal_rate': (self.combined_signals/total_signals*100) if total_signals > 0 else 0
            }
        } 