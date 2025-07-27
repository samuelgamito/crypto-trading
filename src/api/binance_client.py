"""
Binance API client for cryptocurrency trading
"""

import time
import hmac
import hashlib
import requests
import logging
from urllib.parse import urlencode
from typing import Dict, List, Optional, Any


class BinanceClient:
    """Binance API client for trading operations"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = config.get_binance_url()
        self.api_key = config.api_key
        self.secret_key = config.secret_key
        self.logger = logging.getLogger(__name__)
        
        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate HMAC SHA256 signature for authenticated requests"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, 
                     signed: bool = False) -> Dict:
        """Make HTTP request to Binance API"""
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        return self._make_request('GET', '/api/v3/account', signed=True)
    
    def get_balance(self, asset: str = 'USDT') -> float:
        """Get balance for a specific asset"""
        account_info = self.get_account_info()
        for balance in account_info['balances']:
            if balance['asset'] == asset:
                return float(balance['free'])
        return 0.0
    
    def get_ticker_price(self, symbol: str) -> Dict:
        """Get current price for a symbol"""
        return self._make_request('GET', '/api/v3/ticker/price', {'symbol': symbol})
    
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> List:
        """Get kline/candlestick data"""
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        return self._make_request('GET', '/api/v3/klines', params)
    
    def place_order(self, symbol: str, side: str, quantity: float, 
                   order_type: str = 'MARKET') -> Dict:
        """Place a new order"""
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity
        }
        return self._make_request('POST', '/api/v3/order', params, signed=True)
    
    def get_open_orders(self, symbol: str = None) -> List:
        """Get open orders"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._make_request('GET', '/api/v3/openOrders', params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancel an order"""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('DELETE', '/api/v3/order', params, signed=True)
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """Get order status"""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('GET', '/api/v3/order', params, signed=True)
    
    def get_exchange_info(self) -> Dict:
        """Get exchange information"""
        return self._make_request('GET', '/api/v3/exchangeInfo')
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get information about a specific symbol"""
        exchange_info = self.get_exchange_info()
        for symbol_info in exchange_info['symbols']:
            if symbol_info['symbol'] == symbol:
                return symbol_info
        return None 