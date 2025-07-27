# Technical Implementation Guide

## Architecture Overview

O sistema de trading implementa uma arquitetura modular com duas estratégias complementares que trabalham em conjunto para melhorar a precisão dos sinais de trading.

## Core Components

### 1. Base Strategy (`src/strategies/base_strategy.py`)

Classe abstrata que define a interface comum para todas as estratégias de trading.

#### Key Methods
```python
@abstractmethod
def should_buy(self, market_data: MarketData) -> bool:
    """Determine if we should buy based on market data"""

@abstractmethod
def should_sell(self, market_data: MarketData) -> bool:
    """Determine if we should sell based on market data"""

@abstractmethod
def calculate_position_size(self, market_data: MarketData) -> float:
    """Calculate the position size for the trade"""

def has_position(self) -> bool:
    """Check if we have any open positions"""
```

#### Position Management
- Tracks positions in `self.positions` dictionary
- Syncs with actual wallet balances via `sync_positions_with_wallet()`
- Manages trade execution and P&L calculation

### 2. SMA Strategy (`src/strategies/simple_moving_average.py`)

Implementa a estratégia de crossover de médias móveis simples.

#### Configuration
```python
short_period = 12  # Fast SMA
long_period = 15   # Slow SMA
interval = '1h'    # Data interval
```

#### Signal Logic
```python
def should_buy(self, market_data: MarketData) -> bool:
    # Golden Cross: short SMA crosses above long SMA
    prev_short_sma <= prev_long_sma and short_sma > long_sma

def should_sell(self, market_data: MarketData) -> bool:
    # Death Cross: short SMA crosses below long SMA
    prev_short_sma >= prev_long_sma and short_sma < long_sma
```

#### Data Management
- Maintains price history in `self.price_history`
- Initializes with historical data from Binance API
- Updates with live market data

### 3. RSI + Volume Strategy (`src/strategies/rsi_volume_strategy.py`)

Implementa estratégia baseada em RSI e confirmação de volume.

#### Configuration
```python
rsi_period = 14      # RSI calculation period
volume_period = 20   # Volume SMA period
```

#### Signal Logic
```python
def should_buy(self, market_data: MarketData) -> bool:
    # RSI not overbought AND volume above average
    rsi < 70 and volume > volume_sma

def should_sell(self, market_data: MarketData) -> bool:
    # RSI not oversold AND volume above average
    rsi > 30 and volume > volume_sma
```

#### Indicators
- **RSI Indicator**: Calculates 14-period RSI
- **Volume Indicator**: Calculates volume SMA and ratios

### 4. Enhanced Trading Bot (`src/strategies/trading_bot.py`)

Orquestra ambas as estratégias e implementa a lógica de combinação de sinais.

#### Dual Strategy Architecture
```python
class TradingBot:
    def __init__(self, config, binance_client):
        # Initialize both strategies
        self.sma_strategy = SimpleMovingAverageStrategy(config, binance_client)
        self.rsi_volume_strategy = RSIVolumeStrategy(config, binance_client)
        
        # Use SMA strategy as primary (for position management)
        self.strategy = self.sma_strategy
```

#### Signal Combination Logic

**Buy Signal Evaluation**
```python
def _evaluate_buy_signals(self, sma_buy: bool, rsi_buy: bool, market_data: MarketData) -> bool:
    # Strong buy: Both strategies agree
    if sma_buy and rsi_buy:
        return True
    
    # Moderate buy: SMA signals but RSI is neutral
    elif sma_buy and not self.rsi_volume_strategy.rsi_indicator.is_overbought():
        return True
    
    # Conservative buy: RSI oversold with volume confirmation
    elif rsi_buy and self.rsi_volume_strategy.rsi_indicator.is_oversold():
        return True
    
    return False
```

**Sell Signal Evaluation**
```python
def _evaluate_sell_signals(self, sma_sell: bool, rsi_sell: bool, market_data: MarketData) -> bool:
    # Strong sell: Both strategies agree
    if sma_sell and rsi_sell:
        return True
    
    # Moderate sell: SMA signals but RSI is neutral
    elif sma_sell and not self.rsi_volume_strategy.rsi_indicator.is_oversold():
        return True
    
    # Conservative sell: RSI overbought with volume confirmation
    elif rsi_sell and self.rsi_volume_strategy.rsi_indicator.is_overbought():
        return True
    
    return False
```

### 5. Technical Indicators (`src/utils/indicators.py`)

Implementa os indicadores técnicos utilizados pelas estratégias.

#### RSI Indicator
```python
class RSIIndicator:
    def __init__(self, period: int = 14):
        self.period = period
        self.price_history: List[float] = []
    
    def calculate_rsi(self) -> float:
        # Standard RSI calculation
        # RSI = 100 - (100 / (1 + RS))
        # RS = Average Gain / Average Loss
```

#### Volume Indicator
```python
class VolumeIndicator:
    def __init__(self, period: int = 20):
        self.period = period
        self.volume_history: List[float] = []
    
    def calculate_volume_sma(self) -> float:
        # Calculate volume SMA
    
    def is_volume_above_average(self, current_volume: float) -> bool:
        # Check if current volume > average volume
```

## Data Flow

### 1. Market Data Collection
```python
market_data = self.strategy.get_market_data(self.config.default_symbol)
```

### 2. Strategy Updates
```python
def _update_strategies(self, market_data: MarketData):
    # Update RSI strategy with market data
    self.rsi_volume_strategy.rsi_indicator.add_price(market_data.price)
    self.rsi_volume_strategy.volume_indicator.add_volume(market_data.quote_volume)
```

### 3. Signal Generation
```python
def _get_strategy_signals(self, market_data: MarketData) -> Tuple[bool, bool, bool, bool]:
    # SMA signals
    sma_buy = self.sma_strategy.should_buy(market_data)
    sma_sell = self.sma_strategy.should_sell(market_data)
    
    # RSI + Volume signals
    rsi_buy = self.rsi_volume_strategy.should_buy(market_data)
    rsi_sell = self.rsi_volume_strategy.should_sell(market_data)
    
    return sma_buy, sma_sell, rsi_buy, rsi_sell
```

### 4. Signal Evaluation
```python
def _process_enhanced_trading_signals(self, market_data: MarketData):
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
```

## Performance Tracking

### Strategy Metrics
```python
# Strategy performance tracking
self.sma_signals = 0
self.rsi_signals = 0
self.combined_signals = 0
```

### Enhanced Logging
```python
def _log_market_conditions(self, market_data: MarketData):
    # Log SMA conditions
    short_sma = self.sma_strategy._calculate_sma(self.sma_strategy.short_period)
    long_sma = self.sma_strategy._calculate_sma(self.sma_strategy.long_period)
    
    # Log RSI and Volume conditions
    rsi_value = self.rsi_volume_strategy.rsi_indicator.calculate_rsi()
    volume_ratio = self.rsi_volume_strategy.volume_indicator.get_volume_ratio(market_data.quote_volume)
```

## Configuration

### Environment Variables
```bash
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
BINANCE_TESTNET=true
TRADING_SYMBOL=BTCBRL
TRADE_PERCENTAGE=5.0
MAX_DAILY_TRADES=10
```

### Strategy Parameters
```python
# SMA Strategy
short_period = 12
long_period = 15

# RSI + Volume Strategy
rsi_period = 14
volume_period = 20
```

## Error Handling

### API Error Handling
- Automatic retry mechanism for API calls
- Graceful degradation when API is unavailable
- Detailed error logging for debugging

### Data Validation
- Validation of order parameters before execution
- Balance checks before placing orders
- Position synchronization with wallet

### Strategy Error Handling
- Fallback to single strategy if one fails
- Data validation for indicators
- Graceful handling of insufficient historical data

## Monitoring and Logging

### Real-time Display
```
📊 BTCBRL: 664,870.00
   📈 SMA: 662,884.92/662,385.93 | RSI: 64.5 | Vol: 0.0x
   🎯 Trades: 0/10
```

### Performance Summary
```
📊 ENHANCED TRADING BOT PERFORMANCE SUMMARY
Total Trades: 5
Win Rate: 60.0%
Total P&L: +125.50

📈 STRATEGY PERFORMANCE BREAKDOWN
SMA Signals: 3
RSI+Volume Signals: 2
Combined Signals: 1
```

## Extensibility

### Adding New Strategies
1. Extend `BaseStrategy` class
2. Implement required abstract methods
3. Add strategy to `TradingBot` initialization
4. Update signal combination logic

### Adding New Indicators
1. Create indicator class in `src/utils/indicators.py`
2. Implement calculation methods
3. Integrate with existing strategies

### Configuration Management
- Environment-based configuration
- Strategy parameter customization
- Runtime parameter adjustment 