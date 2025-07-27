"""
Backtesting engine for trading strategies
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from src.models.trade import Trade, OrderSide, MarketData
from src.strategies.base_strategy import BaseStrategy


@dataclass
class BacktestResult:
    """Results from a backtest run"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    total_return: float
    trades: List[Trade]
    equity_curve: List[Tuple[datetime, float]]
    initial_balance: float
    final_balance: float


class BacktestEngine:
    """Backtesting engine for trading strategies"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Trading state
        self.positions: Dict[str, float] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[Tuple[datetime, float]] = []
        
        # Performance tracking
        self.peak_balance = initial_balance
        self.max_drawdown = 0.0
        self.returns: List[float] = []
    
    def run_backtest(self, strategy: BaseStrategy, historical_data: List[MarketData], 
                    symbol: str = "BTCUSDT") -> BacktestResult:
        """
        Run backtest on historical data
        
        Args:
            strategy: Trading strategy to test
            historical_data: List of historical market data points
            symbol: Trading symbol
            
        Returns:
            BacktestResult with performance metrics
        """
        self.logger.info(f"Starting backtest with {len(historical_data)} data points")
        self.logger.info(f"Initial balance: ${self.initial_balance:.2f}")
        
        # Reset state
        self.current_balance = self.initial_balance
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.peak_balance = self.initial_balance
        self.max_drawdown = 0.0
        self.returns = []
        
        # Track equity curve
        self.equity_curve.append((historical_data[0].timestamp, self.current_balance))
        
        for i, market_data in enumerate(historical_data):
            # Update strategy with current market data
            self._update_strategy_data(strategy, market_data)
            
            # Check for trading signals
            self._process_signals(strategy, market_data, symbol)
            
            # Update equity curve
            current_equity = self._calculate_current_equity(market_data)
            self.equity_curve.append((market_data.timestamp, current_equity))
            
            # Update drawdown
            self._update_drawdown(current_equity)
            
            # Log progress
            if i % 100 == 0:
                self.logger.info(f"Processed {i}/{len(historical_data)} data points")
        
        # Calculate final results
        final_balance = self._calculate_current_equity(historical_data[-1])
        result = self._calculate_results(final_balance)
        
        self.logger.info("Backtest completed")
        self.logger.info(f"Final balance: ${final_balance:.2f}")
        self.logger.info(f"Total return: {result.total_return:.2f}%")
        self.logger.info(f"Win rate: {result.win_rate:.1f}%")
        
        return result
    
    def _update_strategy_data(self, strategy: BaseStrategy, market_data: MarketData):
        """Update strategy with current market data"""
        # For SMA strategy, we need to update price history
        if hasattr(strategy, 'price_history'):
            strategy.price_history.append(market_data.price)
            # Keep only the last long_period + 1 prices (need extra for crossover detection)
            if hasattr(strategy, 'long_period'):
                if len(strategy.price_history) > strategy.long_period + 1:
                    strategy.price_history = strategy.price_history[-(strategy.long_period + 1):]
    
    def _process_signals(self, strategy: BaseStrategy, market_data: MarketData, symbol: str):
        """Process trading signals"""
        try:
            # Check buy signal
            if strategy.should_buy(market_data):
                self._execute_buy_signal(strategy, market_data, symbol)
            
            # Check sell signal
            elif strategy.should_sell(market_data):
                self._execute_sell_signal(strategy, market_data, symbol)
                
        except Exception as e:
            self.logger.error(f"Error processing signals: {e}")
    
    def _execute_buy_signal(self, strategy: BaseStrategy, market_data: MarketData, symbol: str):
        """Execute a buy signal in backtest"""
        try:
            # Calculate position size
            quantity = strategy.calculate_position_size(market_data)
            
            if quantity <= 0:
                return
            
            # Check if we already have a position
            current_position = self.positions.get(symbol, 0)
            if current_position > 0:
                return
            
            # Check if we have enough balance
            required_balance = quantity * market_data.price
            if self.current_balance < required_balance:
                return
            
            # Execute the buy
            self.current_balance -= required_balance
            self.positions[symbol] = quantity
            
            # Create trade record
            trade = Trade(
                symbol=symbol,
                side=OrderSide.BUY,
                quantity=quantity,
                price=market_data.price,
                timestamp=market_data.timestamp
            )
            
            self.trades.append(trade)
            self.logger.debug(f"BUY: {quantity} {symbol} @ ${market_data.price:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error executing buy signal: {e}")
    
    def _execute_sell_signal(self, strategy: BaseStrategy, market_data: MarketData, symbol: str):
        """Execute a sell signal in backtest"""
        try:
            # Check if we have a position to sell
            current_position = self.positions.get(symbol, 0)
            
            if current_position <= 0:
                return
            
            # Execute the sell
            sell_value = current_position * market_data.price
            self.current_balance += sell_value
            self.positions[symbol] = 0
            
            # Create trade record
            trade = Trade(
                symbol=symbol,
                side=OrderSide.SELL,
                quantity=current_position,
                price=market_data.price,
                timestamp=market_data.timestamp
            )
            
            self.trades.append(trade)
            
            # Calculate P&L for this trade
            pnl = self._calculate_trade_pnl(trade)
            self.returns.append(pnl)
            
            self.logger.debug(f"SELL: {current_position} {symbol} @ ${market_data.price:.2f} (P&L: ${pnl:.2f})")
            
        except Exception as e:
            self.logger.error(f"Error executing sell signal: {e}")
    
    def _calculate_trade_pnl(self, sell_trade: Trade) -> float:
        """Calculate P&L for a completed trade"""
        # Find the corresponding buy trade
        buy_trade = None
        for trade in reversed(self.trades):
            if trade.symbol == sell_trade.symbol and trade.side == OrderSide.BUY:
                buy_trade = trade
                break
        
        if not buy_trade:
            return 0.0
        
        # Calculate P&L
        buy_value = buy_trade.quantity * buy_trade.price
        sell_value = sell_trade.quantity * sell_trade.price
        pnl = sell_value - buy_value
        
        return pnl
    
    def _calculate_current_equity(self, market_data: MarketData) -> float:
        """Calculate current equity including unrealized P&L"""
        equity = self.current_balance
        
        for symbol, quantity in self.positions.items():
            if quantity > 0:
                # Use current market price for unrealized P&L
                current_price = market_data.price if market_data.symbol == symbol else 0
                if current_price > 0:
                    equity += quantity * current_price
        
        return equity
    
    def _update_drawdown(self, current_equity: float):
        """Update maximum drawdown"""
        if current_equity > self.peak_balance:
            self.peak_balance = current_equity
        
        drawdown = (self.peak_balance - current_equity) / self.peak_balance
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
    
    def _calculate_results(self, final_balance: float) -> BacktestResult:
        """Calculate final backtest results"""
        # Count winning and losing trades
        winning_trades = sum(1 for pnl in self.returns if pnl > 0)
        losing_trades = sum(1 for pnl in self.returns if pnl < 0)
        total_trades = len(self.returns)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_pnl = sum(self.returns)
        total_return = ((final_balance - self.initial_balance) / self.initial_balance) * 100
        
        # Calculate Sharpe ratio (simplified)
        sharpe_ratio = 0.0
        if self.returns:
            avg_return = sum(self.returns) / len(self.returns)
            if len(self.returns) > 1:
                variance = sum((r - avg_return) ** 2 for r in self.returns) / (len(self.returns) - 1)
                sharpe_ratio = avg_return / (variance ** 0.5) if variance > 0 else 0
        
        return BacktestResult(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            max_drawdown=self.max_drawdown * 100,  # Convert to percentage
            sharpe_ratio=sharpe_ratio,
            total_return=total_return,
            trades=self.trades.copy(),
            equity_curve=self.equity_curve.copy(),
            initial_balance=self.initial_balance,
            final_balance=final_balance
        ) 