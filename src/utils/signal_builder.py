"""
Signal builder utility for formatting trading signals
"""

import logging
from datetime import datetime
from typing import Dict, List, Tuple
from src.models.trade import MarketData


class SignalBuilder:
    """Utility for building trading signal documents"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def build_signal_document(
        self,
        market_data: MarketData,
        sma_signals: Tuple[bool, bool],
        rsi_signals: Tuple[bool, bool],
        volume_signals: Tuple[bool, bool],
        decision: str,
        strength: str,
        reason: str
    ) -> Dict:
        """
        Build a trading signal document for MongoDB storage
        
        Args:
            market_data: Current market data
            sma_signals: Tuple of (sma_buy, sma_sell)
            rsi_signals: Tuple of (rsi_buy, rsi_sell)
            volume_signals: Tuple of (volume_buy, volume_sell)
            decision: BUY, SELL, or KEEP
            strength: CONSERVATIVE, MODERATE, or STRONG
            reason: Human-readable reason for the decision
        """
        
        # Build signals array
        signals = []
        
        # SMA signals
        sma_buy, sma_sell = sma_signals
        signals.append({
            "signal": "SMA_BUY",
            "result": str(sma_buy).lower(),
            "value": f"{market_data.price:.2f}",
            "threshold": "SMA Crossover"
        })
        signals.append({
            "signal": "SMA_SELL", 
            "result": str(sma_sell).lower(),
            "value": f"{market_data.price:.2f}",
            "threshold": "SMA Crossover"
        })
        
        # RSI signals
        rsi_buy, rsi_sell = rsi_signals
        signals.append({
            "signal": "RSI_BUY",
            "result": str(rsi_buy).lower(),
            "value": "RSI Value",  # Will be updated with actual RSI value
            "threshold": "RSI < 70"
        })
        signals.append({
            "signal": "RSI_SELL",
            "result": str(rsi_sell).lower(), 
            "value": "RSI Value",  # Will be updated with actual RSI value
            "threshold": "RSI > 30"
        })
        
        # Volume signals
        volume_buy, volume_sell = volume_signals
        signals.append({
            "signal": "VOLUME_BUY",
            "result": str(volume_buy).lower(),
            "value": f"{market_data.volume:.2f}",
            "threshold": "Volume > Average"
        })
        signals.append({
            "signal": "VOLUME_SELL",
            "result": str(volume_sell).lower(),
            "value": f"{market_data.volume:.2f}", 
            "threshold": "Volume > Average"
        })
        
        # Build the complete document
        signal_document = {
            "signals": signals,
            "decision": decision,
            "strength": strength,
            "reason": reason,
            "created_at": datetime.utcnow().isoformat() + 'Z',
            "market_data": {
                "symbol": market_data.symbol,
                "price": market_data.price,
                "volume": market_data.volume,
                "timestamp": market_data.timestamp.isoformat() if market_data.timestamp else None
            }
        }
        
        return signal_document
    
    def build_enhanced_signal_document(
        self,
        market_data: MarketData,
        sma_buy: bool,
        sma_sell: bool,
        rsi_buy: bool,
        rsi_sell: bool,
        rsi_value: float,
        volume_ratio: float,
        decision: str,
        strength: str,
        reason: str,
        executed: bool = False,
        failure_reason: str = None
    ) -> Dict:
        """
        Build an enhanced trading signal document with actual indicator values and execution status
        """
        
        # Build signals array with actual values
        signals = []
        
        # SMA signals
        signals.append({
            "signal": "SMA_BUY",
            "result": str(sma_buy).lower(),
            "value": f"{market_data.price:.2f}",
            "threshold": "SMA Crossover"
        })
        signals.append({
            "signal": "SMA_SELL", 
            "result": str(sma_sell).lower(),
            "value": f"{market_data.price:.2f}",
            "threshold": "SMA Crossover"
        })
        
        # RSI signals with actual RSI value
        signals.append({
            "signal": "RSI_BUY",
            "result": str(rsi_buy).lower(),
            "value": f"{rsi_value:.1f}",
            "threshold": "RSI < 70"
        })
        signals.append({
            "signal": "RSI_SELL",
            "result": str(rsi_sell).lower(), 
            "value": f"{rsi_value:.1f}",
            "threshold": "RSI > 30"
        })
        
        # Volume signals with actual volume ratio
        volume_buy = volume_ratio > 1.0
        volume_sell = volume_ratio > 1.0
        signals.append({
            "signal": "VOLUME_BUY",
            "result": str(volume_buy).lower(),
            "value": f"{volume_ratio:.2f}x",
            "threshold": "Volume > 1.0x Average"
        })
        signals.append({
            "signal": "VOLUME_SELL",
            "result": str(volume_sell).lower(),
            "value": f"{volume_ratio:.2f}x", 
            "threshold": "Volume > 1.0x Average"
        })
        
        # Build the complete document with execution status
        signal_document = {
            "signals": signals,
            "decision": decision,
            "strength": strength,
            "reason": reason,
            "executed": executed,
            "created_at": datetime.utcnow().isoformat() + 'Z',
            "market_data": {
                "symbol": market_data.symbol,
                "price": market_data.price,
                "volume": market_data.volume,
                "quote_volume": market_data.quote_volume,
                "timestamp": market_data.timestamp.isoformat() if market_data.timestamp else None
            },
            "indicators": {
                "rsi_value": rsi_value,
                "volume_ratio": volume_ratio
            }
        }
        
        # Add failure reason if execution failed
        if not executed and failure_reason:
            signal_document["failure_reason"] = failure_reason
        
        return signal_document 