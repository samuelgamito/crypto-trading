"""
Base strategy class for trading strategies
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
import logging

from src.models.trade import MarketData, Trade, OrderSide
from src.api.binance_client import BinanceClient


class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, config, binance_client: BinanceClient):
        self.config = config
        self.binance_client = binance_client
        self.logger = logging.getLogger(self.__class__.__name__)
        self.trades: List[Trade] = []
        self.positions: Dict[str, float] = {}
        
        # Initialize positions with actual wallet balances
        self.sync_positions_with_wallet()
        
    @abstractmethod
    def should_buy(self, market_data: MarketData) -> bool:
        """Determine if we should buy based on market data"""
        pass
    
    @abstractmethod
    def should_sell(self, market_data: MarketData) -> bool:
        """Determine if we should sell based on market data"""
        pass
    
    @abstractmethod
    def calculate_position_size(self, market_data: MarketData) -> float:
        """Calculate the position size for the trade"""
        pass
    
    def execute_buy(self, symbol: str, quantity: float) -> Optional[Trade]:
        """Execute a buy order"""
        try:
            self.logger.info(f"Executing BUY order: {symbol} {quantity}")
            
            # Get current price for validation
            current_price = float(self.binance_client.get_ticker_price(symbol)['price'])
            
            # Validate order parameters
            if hasattr(self, 'fee_manager'):
                validation = self.fee_manager.validate_order_parameters(symbol, quantity, current_price)
                if not validation['valid']:
                    self.logger.error(f"Order validation failed: {validation['errors']}")
                    return None
            
            # Check if we have enough balance
            balance = self.binance_client.get_balance(self.config.currency_symbol)
            required_balance = quantity * current_price
            
            if balance < required_balance:
                self.logger.warning(f"Insufficient balance. Required: {required_balance}, Available: {balance}")
                return None
            
            # Place the order
            order_response = self.binance_client.place_order(
                symbol=symbol,
                side='BUY',
                quantity=quantity
            )
            
            # Create trade record
            trade = Trade(
                symbol=symbol,
                side=OrderSide.BUY,
                quantity=quantity,
                price=current_price,
                timestamp=datetime.now(),
                order_id=order_response.get('orderId')
            )
            
            self.trades.append(trade)
            # For BTCBRL trades, track BTC position
            if symbol == 'BTCBRL':
                self.positions['BTC'] = self.positions.get('BTC', 0) + quantity
            else:
                self.positions[symbol] = self.positions.get(symbol, 0) + quantity
            
            self.logger.info(f"BUY order executed successfully: {trade}")
            return trade
            
        except Exception as e:
            self.logger.error(f"Error executing BUY order: {e}")
            return None
    
    def execute_sell(self, symbol: str, quantity: float) -> Optional[Trade]:
        """Execute a sell order"""
        try:
            self.logger.info(f"Executing SELL order: {symbol} {quantity}")
            
            # Round quantity to meet symbol requirements
            if hasattr(self, 'fee_manager'):
                # Get current balance for smart rounding
                if symbol == 'BTCBRL':
                    current_quantity = self.positions.get('BTC', 0)
                else:
                    current_quantity = self.positions.get(symbol, 0)
                
                quantity = self.fee_manager.round_quantity(quantity, symbol, available_balance=current_quantity, is_sell_order=True)
                self.logger.info(f"Rounded sell quantity: {quantity:.8f} (available: {current_quantity:.8f})")
            
            # Get current price for validation
            current_price = float(self.binance_client.get_ticker_price(symbol)['price'])
            
            # Validate order parameters
            if hasattr(self, 'fee_manager'):
                validation = self.fee_manager.validate_order_parameters(symbol, quantity, current_price)
                if not validation['valid']:
                    self.logger.error(f"Order validation failed: {validation['errors']}")
                    return None
            
            # Check if we have enough of the asset
            if symbol == 'BTCBRL':
                current_quantity = self.positions.get('BTC', 0)
            else:
                current_quantity = self.positions.get(symbol, 0)
                
            if current_quantity < quantity:
                self.logger.warning(f"Insufficient {symbol}. Required: {quantity:.8f}, Available: {current_quantity:.8f}")
                return None
            
            # Place the order
            order_response = self.binance_client.place_order(
                symbol=symbol,
                side='SELL',
                quantity=quantity
            )
            
            # Get current price
            current_price = float(self.binance_client.get_ticker_price(symbol)['price'])
            
            # Create trade record
            trade = Trade(
                symbol=symbol,
                side=OrderSide.SELL,
                quantity=quantity,
                price=current_price,
                timestamp=datetime.now(),
                order_id=order_response.get('orderId')
            )
            
            self.trades.append(trade)
            # For BTCBRL trades, track BTC position
            if symbol == 'BTCBRL':
                self.positions['BTC'] = current_quantity - quantity
            else:
                self.positions[symbol] = current_quantity - quantity
            
            self.logger.info(f"SELL order executed successfully: {trade}")
            return trade
            
        except Exception as e:
            self.logger.error(f"Error executing SELL order: {e}")
            return None
    
    def get_market_data(self, symbol: str) -> MarketData:
        """Get current market data for a symbol"""
        try:
            ticker_data = self.binance_client.get_ticker_price(symbol)
            
            # Get 24h stats if available
            klines = self.binance_client.get_klines(symbol, interval='1d', limit=1)
            
            market_data = MarketData(
                symbol=symbol,
                price=float(ticker_data['price']),
                volume=0.0,  # Would need additional API call for volume
                timestamp=datetime.now()
            )
            
            if klines:
                kline = klines[0]
                market_data.high_24h = float(kline[2])
                market_data.low_24h = float(kline[3])
                market_data.volume = float(kline[5])
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            raise
    
    def get_total_pnl(self) -> float:
        """Calculate total profit/loss from all trades"""
        total_pnl = 0.0
        for trade in self.trades:
            if trade.side == OrderSide.BUY:
                total_pnl -= trade.total_value
            else:
                total_pnl += trade.total_value
        return total_pnl
    
    def sync_positions_with_wallet(self):
        """Sync internal positions with actual wallet balances"""
        try:
            # For BTCUSDT trading, we need to track BTC and BRL positions
            if self.config.default_symbol == 'BTCBRL':
                # Get actual wallet balances
                btc_balance = self.binance_client.get_balance('BTC')
                brl_balance = self.binance_client.get_balance('BRL')
                
                # Update internal positions with real balances
                self.positions['BTC'] = btc_balance
                self.positions['BRL'] = brl_balance
                self.logger.info(f"Synced positions with wallet: BTC={btc_balance:.8f}, BRL={brl_balance:.2f}")
            else:
                # Generic case for other symbols
                crypto_balance = self.binance_client.get_balance(self.config.crypto_symbol)
                currency_balance = self.binance_client.get_balance(self.config.currency_symbol)
                
                # Update internal positions with real balances
                self.positions[self.config.crypto_symbol] = crypto_balance
                self.positions[self.config.currency_symbol] = currency_balance
                self.logger.info(f"Synced positions with wallet: {self.config.crypto_symbol}={crypto_balance:.6f}, {self.config.currency_symbol}={currency_balance:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error syncing positions with wallet: {e}")
    
    def get_position_summary(self) -> Dict[str, float]:
        """Get summary of current positions"""
        return self.positions.copy()
    
    def has_position(self) -> bool:
        """Check if we have any open positions"""
        # Check if we have any crypto positions (excluding currency positions)
        for symbol, quantity in self.positions.items():
            if symbol != self.config.currency_symbol and quantity > 0:
                return True
        return False 