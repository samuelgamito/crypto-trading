#!/usr/bin/env python3
"""
Test quantity validation and rounding
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.binance_client import BinanceClient
from src.utils.fee_manager import FeeManager
from src.config.config import Config

def test_quantity_rounding():
    """Test the quantity rounding functionality"""
    print("Testing quantity rounding...")
    
    # Load configuration
    config = Config()
    
    # Initialize Binance client
    binance_client = BinanceClient(config)
    
    # Initialize fee manager
    fee_manager = FeeManager(binance_client)
    
    # Test with BTCUSDT (which has step size 1e-05)
    symbol = "BTCUSDT"
    
    # Test quantities that should be rounded
    test_quantities = [
        0.00015984,  # The problematic quantity from the error
        0.00016000,
        0.00015000,
        0.00014999,
        0.00016001
    ]
    
    print(f"\nTesting {symbol} with step size 1e-05:")
    for quantity in test_quantities:
        rounded = fee_manager.round_quantity(quantity, symbol)
        validation = fee_manager.validate_order_parameters(symbol, rounded)
        
        print(f"  {quantity:.8f} -> {rounded:.8f} (valid: {validation['valid']})")
        if not validation['valid']:
            print(f"    Errors: {validation['errors']}")

if __name__ == "__main__":
    test_quantity_rounding() 