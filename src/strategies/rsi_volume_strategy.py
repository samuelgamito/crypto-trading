"""
RSI + Volume Filters trading strategy
"""

from typing import List
import logging

from src.strategies.base_strategy import BaseStrategy
from src.models.trade import MarketData
from src.utils.fee_manager import FeeManager
from src.utils.indicators import RSIIndicator, VolumeIndicator


class RSIVolumeStrategy(BaseStrategy):
    """RSI + Volume Filters trading strategy"""
    
    def __init__(self, config, binance_client, rsi_period: int = 14, volume_period: int = 20):
        super().__init__(config, binance_client)
        self.rsi_period = rsi_period
        self.volume_period = volume_period
        
        # Initialize indicators
        self.rsi_indicator = RSIIndicator(period=rsi_period)
        self.volume_indicator = VolumeIndicator(period=volume_period)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize fee manager
        self.fee_manager = FeeManager(binance_client)
        
        # Initialize price and volume history with recent data for live trading
        self._initialize_history()
    
    def _initialize_history(self):
        """Initialize price and volume history with recent historical data"""
        try:
            # Get recent klines data (1-hour intervals)
            klines = self.binance_client.get_klines(
                symbol=self.config.default_symbol,
                interval='1h',
                limit=max(self.rsi_period, self.volume_period) + 5  # Get extra data for safety
            )
            
            # Extract closing prices and volumes
            for kline in klines:
                close_price = float(kline[4])  # Close price is at index 4
                volume = float(kline[5])       # Volume is at index 5
                quote_volume = float(kline[7]) # Quote volume is at index 7
                
                self.rsi_indicator.add_price(close_price)
                self.volume_indicator.add_volume(quote_volume)
            
            self.logger.info(f"Initialized history with {len(klines)} data points")
            
        except Exception as e:
            self.logger.warning(f"Could not initialize history: {e}")
            # If we can't get historical data, we'll build it up gradually
            self.logger.info("History will be built up gradually from live data")
    
    def should_buy(self, market_data: MarketData) -> bool:
        """Buy when RSI < 70 (not overbought) and volume > average volume"""
        # Update indicators with new data
        self.rsi_indicator.add_price(market_data.price)
        self.volume_indicator.add_volume(market_data.quote_volume)
        
        # Get current RSI value
        current_rsi = self.rsi_indicator.calculate_rsi()
        
        # Check RSI condition: not overbought (< 70)
        rsi_condition = current_rsi < 70.0
        
        # Check volume condition: current volume > average volume
        volume_condition = self.volume_indicator.is_volume_above_average(market_data.quote_volume)
        
        # Log conditions for debugging
        avg_volume = self.volume_indicator.calculate_volume_sma()
        volume_ratio = self.volume_indicator.get_volume_ratio(market_data.quote_volume)
        
        self.logger.info(f"Buy conditions - RSI: {current_rsi:.2f} (need < 70), "
                        f"Volume: {market_data.quote_volume:.2f} vs avg {avg_volume:.2f} "
                        f"(ratio: {volume_ratio:.2f})")
        
        if rsi_condition and volume_condition:
            self.logger.info(f"Buy signal triggered: RSI {current_rsi:.2f} < 70 and "
                           f"volume {volume_ratio:.2f}x above average")
            return True
        
        return False
    
    def should_sell(self, market_data: MarketData) -> bool:
        """Sell when RSI > 30 (not oversold) or take profit/stop loss"""
        # Update indicators with new data
        self.rsi_indicator.add_price(market_data.price)
        self.volume_indicator.add_volume(market_data.quote_volume)
        
        # Get current RSI value
        current_rsi = self.rsi_indicator.calculate_rsi()
        
        # Check RSI condition: not oversold (> 30)
        rsi_condition = current_rsi > 30.0
        
        # Check volume condition: current volume > average volume
        volume_condition = self.volume_indicator.is_volume_above_average(market_data.quote_volume)
        
        # Log conditions for debugging
        avg_volume = self.volume_indicator.calculate_volume_sma()
        volume_ratio = self.volume_indicator.get_volume_ratio(market_data.quote_volume)
        
        self.logger.info(f"Sell conditions - RSI: {current_rsi:.2f} (need > 30), "
                        f"Volume: {market_data.quote_volume:.2f} vs avg {avg_volume:.2f} "
                        f"(ratio: {volume_ratio:.2f})")
        
        if rsi_condition and volume_condition:
            self.logger.info(f"Sell signal triggered: RSI {current_rsi:.2f} > 30 and "
                           f"volume {volume_ratio:.2f}x above average")
            return True
        
        # Check take profit and stop loss
        if self._check_take_profit_stop_loss(market_data):
            return True
        
        return False
    
    def calculate_position_size(self, market_data: MarketData) -> float:
        """Calculate position size based on percentage of total wallet balance"""
        try:
            current_price = market_data.price
            
            # Get total wallet balance in BRL
            brl_balance = self.binance_client.get_balance('BRL')
            btc_balance = self.binance_client.get_balance('BTC')
            total_wallet_brl = brl_balance + (btc_balance * current_price)
            
            # Calculate trade amount as percentage of total wallet
            trade_amount_brl = total_wallet_brl * (self.config.trade_percentage / 100.0)
            
            # If fees are enabled, adjust for fees
            if self.config.include_fees:
                # Get fee information
                fee_summary = self.fee_manager.get_fee_summary(market_data.symbol)
                taker_fee_rate = fee_summary['taker_fee_rate']
                
                # Calculate required gross amount to achieve desired net amount
                # desired_net = gross_amount * (1 - fee_rate)
                # gross_amount = desired_net / (1 - fee_rate)
                gross_amount_brl = trade_amount_brl / (1 - taker_fee_rate)
                
                # Add fee buffer for safety
                fee_buffer = gross_amount_brl * (self.config.fee_buffer_percentage / 100.0)
                total_required_brl = gross_amount_brl + fee_buffer
                
                # Check if we have enough balance for the gross amount
                if total_required_brl > brl_balance:
                    self.logger.warning(f"Insufficient BRL balance for fees. Required: R$ {total_required_brl:.2f}, Available: R$ {brl_balance:.2f}")
                    # Try with available balance
                    available_for_trade = brl_balance * (1 - taker_fee_rate - self.config.fee_buffer_percentage / 100.0)
                    if available_for_trade < 50:
                        self.logger.warning(f"Available trade amount R$ {available_for_trade:.2f} below minimum R$ 50")
                        return 0.0
                    trade_amount_brl = available_for_trade
                else:
                    trade_amount_brl = gross_amount_brl * (1 - taker_fee_rate)
                
                self.logger.info(f"Fee-adjusted calculation: Gross R$ {gross_amount_brl:.2f}, Net R$ {trade_amount_brl:.2f}, Fee: {taker_fee_rate*100:.3f}%")
            
            # Calculate BTC quantity
            quantity = trade_amount_brl / current_price
            
            # Round quantity to meet symbol requirements
            quantity = self.fee_manager.round_quantity(quantity, market_data.symbol, is_sell_order=False)
            
            # Ensure minimum trade size (R$ 50)
            if trade_amount_brl < 50:
                self.logger.warning(f"Trade amount R$ {trade_amount_brl:.2f} below minimum R$ 50")
                return 0.0
            
            # Log the calculation
            self.logger.info(f"Position calculation: {self.config.trade_percentage}% of R$ {total_wallet_brl:.2f} = R$ {trade_amount_brl:.2f} = {quantity:.6f} BTC")
            
            return quantity
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def get_market_data(self, symbol: str) -> MarketData:
        """Get current market data for live trading"""
        try:
            # Get current price and volume from Binance
            ticker_data = self.binance_client.get_ticker_price(symbol)
            price = float(ticker_data['price'])
            
            # Get 24hr stats for volume
            stats_24hr = self.binance_client.get_24hr_stats(symbol)
            volume = float(stats_24hr['volume'])
            quote_volume = float(stats_24hr['quoteVolume'])
            
            # Get current timestamp
            from datetime import datetime
            timestamp = datetime.now()
            
            # Create market data object
            market_data = MarketData(
                symbol=symbol,
                price=price,
                volume=volume,
                quote_volume=quote_volume,
                timestamp=timestamp
            )
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            # Return dummy data if API fails
            from datetime import datetime
            return MarketData(
                symbol=symbol,
                price=0.0,
                volume=0.0,
                quote_volume=0.0,
                timestamp=datetime.now()
            )
    
    def _check_take_profit_stop_loss(self, market_data: MarketData) -> bool:
        """Check if take profit or stop loss conditions are met"""
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