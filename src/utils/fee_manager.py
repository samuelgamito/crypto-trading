"""
Fee management for Binance trading operations
"""

import logging
from typing import Dict, Optional
from src.api.binance_client import BinanceClient


class FeeManager:
    """Manages trading fees for Binance operations"""
    
    def __init__(self, binance_client: BinanceClient):
        self.binance_client = binance_client
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Default Binance fees (can be updated via API)
        self.default_fees = {
            'maker': 0.001,  # 0.1% for maker orders
            'taker': 0.001,  # 0.1% for taker orders (market orders)
            'min_fee': 0.0001,  # Minimum fee in BTC
            'bnb_discount': 0.00075  # 0.075% if paying with BNB
        }
        
        # Cache for symbol-specific fees
        self.symbol_fees: Dict[str, Dict] = {}
        
        # Try to get actual fees from Binance
        self._load_fees_from_binance()
    
    def _load_fees_from_binance(self):
        """Load actual trading fees from Binance API"""
        try:
            # Get account trading fees
            account_info = self.binance_client.get_account_info()
            
            # Get exchange info for symbol-specific fees
            exchange_info = self.binance_client.get_exchange_info()
            
            # Update fees based on account level
            if 'makerCommission' in account_info:
                self.default_fees['maker'] = float(account_info['makerCommission']) / 10000
                self.default_fees['taker'] = float(account_info['takerCommission']) / 10000
                
                self.logger.info(f"Loaded fees from Binance: Maker {self.default_fees['maker']:.4f}, Taker {self.default_fees['taker']:.4f}")
            
        except Exception as e:
            self.logger.warning(f"Could not load fees from Binance API: {e}")
            self.logger.info("Using default fee structure")
    
    def get_trading_fee(self, symbol: str, order_type: str = 'MARKET') -> float:
        """Get trading fee for a specific symbol and order type"""
        try:
            # Check if we have cached fees for this symbol
            if symbol in self.symbol_fees:
                return self.symbol_fees[symbol].get('taker' if order_type == 'MARKET' else 'maker', self.default_fees['taker'])
            
            # Get symbol info from Binance
            symbol_info = self.binance_client.get_symbol_info(symbol)
            if symbol_info:
                # Extract fees from symbol info
                filters = {f['filterType']: f for f in symbol_info.get('filters', [])}
                
                # Get commission info
                commission_info = symbol_info.get('commission', {})
                if commission_info:
                    maker_fee = float(commission_info.get('makerCommission', self.default_fees['maker'] * 10000)) / 10000
                    taker_fee = float(commission_info.get('takerCommission', self.default_fees['taker'] * 10000)) / 10000
                    
                    self.symbol_fees[symbol] = {
                        'maker': maker_fee,
                        'taker': taker_fee
                    }
                    
                    return taker_fee if order_type == 'MARKET' else maker_fee
            
            # Return default fee if symbol info not available
            return self.default_fees['taker'] if order_type == 'MARKET' else self.default_fees['maker']
            
        except Exception as e:
            self.logger.error(f"Error getting trading fee for {symbol}: {e}")
            return self.default_fees['taker'] if order_type == 'MARKET' else self.default_fees['maker']
    
    def calculate_fee_amount(self, trade_value: float, symbol: str, order_type: str = 'MARKET') -> float:
        """Calculate the actual fee amount for a trade"""
        fee_rate = self.get_trading_fee(symbol, order_type)
        fee_amount = trade_value * fee_rate
        
        # Apply minimum fee if applicable
        min_fee = self._get_min_fee(symbol)
        if fee_amount < min_fee:
            fee_amount = min_fee
        
        return fee_amount
    
    def _get_min_fee(self, symbol: str) -> float:
        """Get minimum fee for a symbol"""
        try:
            symbol_info = self.binance_client.get_symbol_info(symbol)
            if symbol_info:
                filters = {f['filterType']: f for f in symbol_info.get('filters', [])}
                
                # Check for minimum notional filter
                if 'MIN_NOTIONAL' in filters:
                    min_notional = float(filters['MIN_NOTIONAL']['minNotional'])
                    # Estimate minimum fee as 0.1% of minimum notional
                    return min_notional * 0.001
            
            return self.default_fees['min_fee']
            
        except Exception as e:
            self.logger.error(f"Error getting minimum fee for {symbol}: {e}")
            return self.default_fees['min_fee']
    
    def calculate_net_quantity(self, gross_quantity: float, symbol: str, order_type: str = 'MARKET') -> float:
        """Calculate net quantity after fees for a buy order"""
        try:
            # Get current price to calculate trade value
            ticker = self.binance_client.get_ticker_price(symbol)
            price = float(ticker['price'])
            
            trade_value = gross_quantity * price
            fee_amount = self.calculate_fee_amount(trade_value, symbol, order_type)
            
            # For buy orders, fees reduce the quantity we can buy
            net_value = trade_value - fee_amount
            net_quantity = net_value / price
            
            return net_quantity
            
        except Exception as e:
            self.logger.error(f"Error calculating net quantity: {e}")
            return gross_quantity
    
    def calculate_required_quantity(self, desired_net_quantity: float, symbol: str, order_type: str = 'MARKET') -> float:
        """Calculate required gross quantity to achieve desired net quantity after fees"""
        try:
            # Get current price
            ticker = self.binance_client.get_ticker_price(symbol)
            price = float(ticker['price'])
            
            # Estimate fee rate
            fee_rate = self.get_trading_fee(symbol, order_type)
            
            # Calculate required gross quantity
            # desired_net = gross_quantity * (1 - fee_rate)
            # gross_quantity = desired_net / (1 - fee_rate)
            gross_quantity = desired_net_quantity / (1 - fee_rate)
            
            return gross_quantity
            
        except Exception as e:
            self.logger.error(f"Error calculating required quantity: {e}")
            return desired_net_quantity
    
    def calculate_sell_proceeds(self, quantity: float, symbol: str, order_type: str = 'MARKET') -> float:
        """Calculate net proceeds from a sell order after fees"""
        try:
            # Get current price
            ticker = self.binance_client.get_ticker_price(symbol)
            price = float(ticker['price'])
            
            gross_proceeds = quantity * price
            fee_amount = self.calculate_fee_amount(gross_proceeds, symbol, order_type)
            
            net_proceeds = gross_proceeds - fee_amount
            
            return net_proceeds
            
        except Exception as e:
            self.logger.error(f"Error calculating sell proceeds: {e}")
            return quantity * price
    
    def get_fee_summary(self, symbol: str) -> Dict[str, float]:
        """Get a summary of fees for a symbol"""
        try:
            maker_fee = self.get_trading_fee(symbol, 'LIMIT')
            taker_fee = self.get_trading_fee(symbol, 'MARKET')
            min_fee = self._get_min_fee(symbol)
            
            return {
                'maker_fee_rate': maker_fee,
                'taker_fee_rate': taker_fee,
                'min_fee': min_fee,
                'maker_fee_percent': maker_fee * 100,
                'taker_fee_percent': taker_fee * 100
            }
            
        except Exception as e:
            self.logger.error(f"Error getting fee summary for {symbol}: {e}")
            return {
                'maker_fee_rate': self.default_fees['maker'],
                'taker_fee_rate': self.default_fees['taker'],
                'min_fee': self.default_fees['min_fee'],
                'maker_fee_percent': self.default_fees['maker'] * 100,
                'taker_fee_percent': self.default_fees['taker'] * 100
            }
    
    def get_symbol_filters(self, symbol: str) -> Dict[str, Dict]:
        """Get trading filters for a symbol"""
        try:
            symbol_info = self.binance_client.get_symbol_info(symbol)
            if symbol_info:
                filters = {f['filterType']: f for f in symbol_info.get('filters', [])}
                return filters
            return {}
        except Exception as e:
            self.logger.error(f"Error getting symbol filters for {symbol}: {e}")
            return {}
    
    def round_quantity(self, quantity: float, symbol: str, available_balance: float = None, is_sell_order: bool = False) -> float:
        """Round quantity to meet symbol's step size requirements with smart rounding"""
        try:
            filters = self.get_symbol_filters(symbol)
            
            if 'LOT_SIZE' in filters:
                step_size = float(filters['LOT_SIZE']['stepSize'])
                min_qty = float(filters['LOT_SIZE']['minQty'])
                
                # Calculate steps
                steps = quantity / step_size
                
                # Smart rounding logic
                if is_sell_order and available_balance is not None:
                    # For sell orders: round down to ensure we don't exceed available balance
                    steps = int(steps)  # Floor division
                    rounded_quantity = steps * step_size
                    
                    # If we have more than the rounded quantity, try to round up
                    if available_balance >= (steps + 1) * step_size:
                        # Check if rounding up would still be within our balance
                        potential_quantity = (steps + 1) * step_size
                        if potential_quantity <= available_balance:
                            rounded_quantity = potential_quantity
                            self.logger.debug(f"Rounded UP for sell: {quantity:.8f} -> {rounded_quantity:.8f} (available: {available_balance:.8f})")
                        else:
                            self.logger.debug(f"Rounded DOWN for sell: {quantity:.8f} -> {rounded_quantity:.8f} (insufficient balance)")
                    else:
                        self.logger.debug(f"Rounded DOWN for sell: {quantity:.8f} -> {rounded_quantity:.8f} (insufficient balance)")
                else:
                    # For buy orders or when balance is not provided: round to nearest
                    steps = round(steps)
                    rounded_quantity = steps * step_size
                    self.logger.debug(f"Rounded to nearest: {quantity:.8f} -> {rounded_quantity:.8f}")
                
                # Ensure minimum quantity
                if rounded_quantity < min_qty:
                    rounded_quantity = min_qty
                    self.logger.debug(f"Adjusted to minimum: {rounded_quantity:.8f}")
                
                # Additional check for floating point precision issues
                if abs(rounded_quantity) < 0.0000000001:
                    rounded_quantity = 0.0
                
                self.logger.debug(f"Final rounded quantity: {quantity:.8f} -> {rounded_quantity:.8f} (step: {step_size:.8f})")
                return rounded_quantity
            
            return quantity
            
        except Exception as e:
            self.logger.error(f"Error rounding quantity for {symbol}: {e}")
            return quantity
    
    def validate_order_parameters(self, symbol: str, quantity: float, price: float = None) -> Dict[str, bool]:
        """Validate order parameters against symbol filters"""
        try:
            filters = self.get_symbol_filters(symbol)
            validation = {
                'valid': True,
                'errors': []
            }
            
            # Check LOT_SIZE filter
            if 'LOT_SIZE' in filters:
                min_qty = float(filters['LOT_SIZE']['minQty'])
                max_qty = float(filters['LOT_SIZE']['maxQty'])
                step_size = float(filters['LOT_SIZE']['stepSize'])
                
                if quantity < min_qty:
                    validation['valid'] = False
                    validation['errors'].append(f"Quantity {quantity:.8f} below minimum {min_qty:.8f}")
                
                if quantity > max_qty:
                    validation['valid'] = False
                    validation['errors'].append(f"Quantity {quantity:.8f} above maximum {max_qty:.8f}")
                
                # Check if quantity aligns with step size using smart rounding logic
                steps = quantity / step_size
                # Round to nearest for validation (same as buy orders)
                rounded_steps = round(steps)
                expected_quantity = rounded_steps * step_size
                if abs(quantity - expected_quantity) > 0.00000001:  # Small tolerance for floating point
                    validation['valid'] = False
                    validation['errors'].append(f"Quantity {quantity:.8f} not aligned with step size {step_size:.8f} (should be {expected_quantity:.8f})")
            
            # Check NOTIONAL filter
            if 'NOTIONAL' in filters and price:
                min_notional = float(filters['NOTIONAL']['minNotional'])
                order_value = quantity * price
                
                if order_value < min_notional:
                    validation['valid'] = False
                    validation['errors'].append(f"Order value {order_value:.2f} below minimum notional {min_notional:.2f}")
            
            return validation
            
        except Exception as e:
            self.logger.error(f"Error validating order parameters for {symbol}: {e}")
            return {'valid': False, 'errors': [str(e)]} 