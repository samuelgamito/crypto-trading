"""
Enhanced trading bot that orchestrates multiple strategies for better performance
"""

import time
import logging
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional

from src.strategies.base_strategy import BaseStrategy
from src.strategies.simple_moving_average import SimpleMovingAverageStrategy
from src.strategies.rsi_volume_strategy import RSIVolumeStrategy
from src.models.trade import MarketData, Trade
from src.models.position import Position
from src.api.binance_client import BinanceClient
from src.config.config import Config
from src.utils.mongo_service import MongoService
from src.utils.signal_builder import SignalBuilder


class TradingBot:
    """Enhanced trading bot that manages multiple strategies for better performance"""
    
    def __init__(self, config, binance_client: BinanceClient):
        self.config = config
        self.binance_client = binance_client
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize MongoDB service and signal builder
        self.mongo_service = MongoService(
            connection_string=config.mongo_connection_string,
            database_name=config.mongo_database,
            username=config.mongo_username,
            password=config.mongo_password
        )
        self.signal_builder = SignalBuilder()
        
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
        
        # Position tracking
        self.current_position: Optional[Position] = None
        
        # Recover position from MongoDB on startup
        self._recover_position()
    
    def _recover_position(self):
        """Recover position from MongoDB on startup"""
        try:
            if not self.config.enable_mongo_logging:
                self.logger.info("MongoDB logging disabled, skipping position recovery")
                return
            
            position_data = self.mongo_service.get_current_position(self.config.default_symbol)
            
            if position_data:
                self.current_position = Position.from_dict(position_data)
                self.logger.info(f"Position recovered from MongoDB: {self.current_position.quantity:.8f} {self.current_position.symbol} at {self.current_position.buy_price:.2f}")
                print(f"🔄 Position recovered: {self.current_position.quantity:.8f} {self.current_position.symbol} at {self.current_position.buy_price:.2f}")
                print(f"   Holding time: {self.current_position.get_holding_time_minutes()} minutes")
            else:
                self.logger.info("No position found in MongoDB")
                print("🔄 No position to recover from MongoDB")
                
        except Exception as e:
            self.logger.error(f"Error recovering position from MongoDB: {e}")
            print(f"❌ Error recovering position: {e}")
        
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
            self.cleanup()
    
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
        
        # Display position status if we have one
        if self.current_position:
            profit_percentage = self.current_position.calculate_profit_percentage(market_data.price)
            holding_time = self.current_position.get_holding_time_minutes()
            print(f"   📈 Position: {self.current_position.quantity:.8f} BTC | Profit: {profit_percentage:+.2f}% | Time: {holding_time}m")
    
    def _log_signal_to_mongodb(self, market_data: MarketData, decision: str, strength: str, reason: str, executed: bool = False, failure_reason: str = None):
        """Log trading signal to MongoDB with execution status"""
        if not self.config.enable_mongo_logging or not self.mongo_service.is_connected():
            return
        
        try:
            # Get current signal values
            sma_buy, sma_sell = self._get_strategy_signals(market_data)[:2]
            rsi_buy, rsi_sell = self._get_strategy_signals(market_data)[2:]
            
            # Get indicator values
            rsi_value = self.rsi_volume_strategy.rsi_indicator.calculate_rsi()
            volume_ratio = self.rsi_volume_strategy.volume_indicator.get_volume_ratio(market_data.quote_volume)
            
            # Build signal document with execution status
            signal_document = self.signal_builder.build_enhanced_signal_document(
                market_data=market_data,
                sma_buy=sma_buy,
                sma_sell=sma_sell,
                rsi_buy=rsi_buy,
                rsi_sell=rsi_sell,
                rsi_value=rsi_value,
                volume_ratio=volume_ratio,
                decision=decision,
                strength=strength,
                reason=reason,
                executed=executed,
                failure_reason=failure_reason
            )
            
            # Store in MongoDB
            success = self.mongo_service.store_trading_signal(signal_document)
            if success:
                execution_status = "✅ EXECUTED" if executed else "❌ NOT EXECUTED"
                self.logger.info(f"Signal logged to MongoDB: {decision} ({strength}) - {execution_status} - {reason}")
            else:
                self.logger.warning("Failed to log signal to MongoDB")
                
        except Exception as e:
            self.logger.error(f"Error logging signal to MongoDB: {e}")

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
            has_position = self.strategy.has_position()
            
            # Evaluate buy signals
            buy_signal_strength = self._evaluate_buy_signals(sma_buy, rsi_buy, market_data)
            should_buy = False
            buy_failure_reason = None
            
            if buy_signal_strength:
                if not has_position:
                    if buy_signal_strength in ["CONSERVATIVE", "STRONG"]:
                        should_buy = True
                        self.logger.info(f"Buy signal for new position: {buy_signal_strength}")
                        print(f"🟢 New position buy signal: {buy_signal_strength}")
                    else:
                        buy_failure_reason = f"MODERATE signal not strong enough for new position"
                else:
                    if buy_signal_strength == "STRONG":
                        should_buy = True
                        self.logger.info(f"Buy signal for existing position: {buy_signal_strength}")
                        print(f"📈 Adding to position: {buy_signal_strength}")
                    else:
                        buy_failure_reason = f"Have position, need STRONG signal (got {buy_signal_strength})"
                        self.logger.info(f"Skipping {buy_signal_strength} signal - have position")
                        print(f"⚠️  Skipping {buy_signal_strength} signal - have position")
            else:
                # No buy signal detected
                self._log_signal_to_mongodb(market_data, "KEEP", "NONE", "No buy signals detected", executed=False, failure_reason="No buy signals")
            
            # Execute buy if conditions met
            if should_buy:
                execution_success = self._execute_enhanced_buy_signal(market_data, sma_buy, rsi_buy)
                if execution_success:
                    self._log_signal_to_mongodb(market_data, "BUY", buy_signal_strength, f"Buy signal executed: {buy_signal_strength}", executed=True)
                else:
                    self._log_signal_to_mongodb(market_data, "BUY", buy_signal_strength, f"Buy signal failed to execute: {buy_signal_strength}", executed=False, failure_reason="Order execution failed")
            elif buy_signal_strength and buy_failure_reason:
                # Log failed buy signal
                self._log_signal_to_mongodb(market_data, "BUY", buy_signal_strength, f"Buy signal not executed: {buy_signal_strength}", executed=False, failure_reason=buy_failure_reason)
            
            # Enhanced sell logic
            if has_position:
                sell_signal = self._evaluate_sell_signals(sma_sell, rsi_sell, market_data)
                if sell_signal:
                    execution_success = self._execute_enhanced_sell_signal(market_data, sma_sell, rsi_sell)
                    if execution_success:
                        self._log_signal_to_mongodb(market_data, "SELL", "STRONG", "Sell signal executed", executed=True)
                    else:
                        self._log_signal_to_mongodb(market_data, "SELL", "STRONG", "Sell signal failed to execute", executed=False, failure_reason="Order execution failed")
                else:
                    # No sell signal when we have position
                    self._log_signal_to_mongodb(market_data, "KEEP", "NONE", "No sell signals detected", executed=False, failure_reason="No sell signals")
            else:
                # No position, no sell possible
                self._log_signal_to_mongodb(market_data, "KEEP", "NONE", "No position to sell", executed=False, failure_reason="No position")
                
        except Exception as e:
            self.logger.error(f"Error processing enhanced trading signals: {e}")
            print(f"❌ Error processing signals: {e}")

    def _evaluate_buy_signals(self, sma_buy: bool, rsi_buy: bool, market_data: MarketData) -> str:
        """Evaluate buy signals using smart combination logic. Returns 'STRONG', 'CONSERVATIVE', 'MODERATE', or None."""
        try:
            # Strong buy: Both strategies agree
            if sma_buy and rsi_buy:
                self.combined_signals += 1
                return "STRONG"
            # Conservative buy: RSI oversold with volume confirmation
            elif rsi_buy and self.rsi_volume_strategy.rsi_indicator.is_oversold():
                self.combined_signals += 1
                return "CONSERVATIVE"
            # Moderate buy: SMA agrees, RSI not overbought
            elif sma_buy and not self.rsi_volume_strategy.rsi_indicator.is_overbought():
                self.combined_signals += 1
                return "MODERATE"
            # No buy signal
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error evaluating buy signals: {e}")
            return None

    def _evaluate_sell_signals(self, sma_sell: bool, rsi_sell: bool, market_data: MarketData) -> bool:
        """Evaluate sell signals using smart combination logic with profit and timing checks"""
        try:
            # If we have a position, check profit and timing conditions first
            if self.current_position:
                # Check if we should sell for profit
                if self.current_position.should_sell_for_profit(
                    market_data.price, 
                    self.config.min_profit_percentage
                ):
                    self.logger.info(f"Profit target reached: {self.current_position.calculate_profit_percentage(market_data.price):.2f}%")
                    return True
                
                # Check if we should sell due to time limit
                if self.current_position.should_sell_for_time(self.config.max_position_age_hours):
                    self.logger.info(f"Position held too long: {self.current_position.get_holding_time_hours():.1f} hours")
                    return True
                
                # Check if we should sell for stop loss
                if self.current_position.should_sell_for_stop_loss(
                    market_data.price, 
                    self.config.stop_loss_percentage
                ):
                    self.logger.info(f"Stop loss triggered: {self.current_position.calculate_profit_percentage(market_data.price):.2f}%")
                    return True
                
                # Check minimum holding time
                if self.current_position.get_holding_time_minutes() < self.config.min_holding_time_minutes:
                    self.logger.info(f"Position too young: {self.current_position.get_holding_time_minutes()} minutes < {self.config.min_holding_time_minutes}")
                    return False
            
            # Strong sell: Both strategies agree
            if sma_sell and rsi_sell:
                self.combined_signals += 1
                return True
            
            # Moderate sell: SMA agrees, RSI not oversold
            elif sma_sell and not self.rsi_volume_strategy.rsi_indicator.is_oversold():
                self.combined_signals += 1
                return True
            
            # Conservative sell: RSI overbought with volume confirmation
            elif rsi_sell and self.rsi_volume_strategy.rsi_indicator.is_overbought():
                self.combined_signals += 1
                return True
            
            # No sell signal
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error evaluating sell signals: {e}")
            return False
    
    def stop(self):
        """Stop the trading bot"""
        self.logger.info("Stopping trading bot...")
        self.is_running = False
        
        # Close MongoDB connection
        if hasattr(self, 'mongo_service'):
            self.mongo_service.close_connection()
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop()
        self._print_performance_summary()
    
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
    
    def _execute_enhanced_buy_signal(self, market_data: MarketData, sma_buy: bool, rsi_buy: bool) -> bool:
        """Execute enhanced buy signal with strategy information. Returns True if successful, False otherwise."""
        try:
            # Calculate position size
            quantity = self.strategy.calculate_position_size(market_data)
            
            if quantity <= 0:
                self.logger.warning("Invalid position size calculated")
                return False
            
            # Get current position for display (but don't block execution)
            current_position = self.strategy.positions.get('BTC', 0)
            if current_position > 0:
                self.logger.info(f"Adding to existing BTC position: {current_position:.8f}")
                print(f"📈 Adding to existing position: {current_position:.8f} BTC")
            
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
                # Create or update position tracking
                if self.current_position:
                    # Add to existing position
                    self.current_position.quantity += quantity
                    self.current_position.fees_paid += estimated_fee
                    self.logger.info(f"Added {quantity:.8f} BTC to existing position")
                else:
                    # Create new position
                    self.current_position = Position(
                        symbol=market_data.symbol,
                        quantity=quantity,
                        buy_price=market_data.price,
                        buy_time=datetime.now()
                    )
                    self.current_position.fees_paid = estimated_fee
                    self.logger.info(f"Created new position: {quantity:.8f} BTC at {market_data.price:.2f}")
                
                # Store position in MongoDB
                if self.config.enable_mongo_logging:
                    position_data = self.current_position.to_dict()
                    self.mongo_service.store_position(position_data)
                    self.logger.info("Position stored in MongoDB")
                
                self.daily_trades += 1
                self.total_trades += 1
                self.trades_today.append(trade)
                
                self.logger.info(f"Enhanced BUY order executed: {trade.quantity:.8f} {market_data.symbol} at ${trade.price:.2f}")
                self.logger.info(f"SMA Signal: {sma_buy}, RSI Signal: {rsi_buy}")
                self.logger.info(f"Daily trades: {self.daily_trades}/{self.config.max_daily_trades}")
                
                print(f"   ✅ ENHANCED BUY ORDER EXECUTED!")
                print(f"   📝 Daily trades: {self.daily_trades}/{self.config.max_daily_trades}")
                return True
            else:
                print(f"   ❌ ENHANCED BUY ORDER FAILED!")
                return False
            
        except Exception as e:
            self.logger.error(f"Error executing enhanced buy signal: {e}")
            print(f"   ❌ Error executing buy: {e}")
            return False
    
    def _update_position_in_mongodb(self):
        """Update current position in MongoDB"""
        if self.current_position and self.config.enable_mongo_logging:
            try:
                position_data = self.current_position.to_dict()
                self.mongo_service.store_position(position_data)
                self.logger.debug("Position updated in MongoDB")
            except Exception as e:
                self.logger.error(f"Error updating position in MongoDB: {e}")
    
    def _execute_enhanced_sell_signal(self, market_data: MarketData, sma_sell: bool, rsi_sell: bool) -> bool:
        """Execute enhanced sell signal with strategy information. Returns True if successful, False otherwise."""
        try:
            # Check if we have a position to sell
            current_position = self.strategy.positions.get('BTC', 0)
            
            if current_position <= 0:
                self.logger.info(f"No BTC position to sell: {current_position:.8f}")
                print(f"⚠️  No BTC position to sell: {current_position:.8f}")
                return False
            
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
                # Calculate actual profit using position tracking
                if self.current_position:
                    actual_profit = self.current_position.calculate_net_profit(market_data.price)
                    profit_percentage = self.current_position.calculate_profit_percentage(market_data.price)
                    
                    self.logger.info(f"Position closed: {self.current_position.quantity:.8f} BTC")
                    self.logger.info(f"Profit: {actual_profit:.2f} BRL ({profit_percentage:.2f}%)")
                    self.logger.info(f"Holding time: {self.current_position.get_holding_time_minutes()} minutes")
                    
                    # Clear the position
                    self.current_position = None
                    
                    # Clear position from MongoDB
                    if self.config.enable_mongo_logging:
                        self.mongo_service.clear_position(market_data.symbol)
                        self.logger.info("Position cleared from MongoDB")
                
                self.daily_trades += 1
                self.total_trades += 1
                self.trades_today.append(trade)
                
                # Calculate P&L for this trade
                pnl = self._calculate_trade_pnl(trade)
                self.total_pnl += pnl
                
                self.logger.info(f"Enhanced SELL order executed: {trade.quantity:.8f} {market_data.symbol} at ${trade.price:.2f}")
                self.logger.info(f"SMA Signal: {sma_sell}, RSI Signal: {rsi_sell}")
                self.logger.info(f"Daily trades: {self.daily_trades}/{self.config.max_daily_trades}")
                
                print(f"   ✅ ENHANCED SELL ORDER EXECUTED!")
                print(f"   💰 P&L: {pnl:+.2f}")
                print(f"   📝 Daily trades: {self.daily_trades}/{self.config.max_daily_trades}")
                return True
            else:
                print(f"   ❌ ENHANCED SELL ORDER FAILED!")
                return False
            
        except Exception as e:
            self.logger.error(f"Error executing enhanced sell signal: {e}")
            print(f"   ❌ Error executing sell: {e}")
            return False
    
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