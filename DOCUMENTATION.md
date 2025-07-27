# Crypto Trading Bot - Complete Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Core Components](#core-components)
6. [Trading Strategies](#trading-strategies)
7. [Backtesting Framework](#backtesting-framework)
8. [Optimization Tools](#optimization-tools)
9. [Running Examples](#running-examples)
10. [Retraining & Optimization](#retraining--optimization)
11. [Live Trading](#live-trading)
12. [Troubleshooting](#troubleshooting)
13. [API Reference](#api-reference)

---

## 🎯 Project Overview

This is a comprehensive crypto trading bot built with Python that includes:
- **Real-time trading** via Binance API
- **Advanced backtesting** framework
- **Strategy optimization** tools
- **Risk management** features
- **Multiple trading strategies** support

The bot uses Simple Moving Average (SMA) crossover strategies and can be easily extended with new strategies.

---

## 📁 Project Structure

```
crypto-trading/
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── README.md                   # Basic project overview
├── main.py                     # Main entry point for live trading
├── backtest.py                 # Backtesting CLI tool
├── optimize_strategy.py        # Strategy optimization tool
├── comprehensive_optimization.py # Advanced optimization
├── run_best_strategies.py      # Run best strategies comparison
├── debug_backtest.py           # Debug backtesting issues
├── test_strategy.py            # Strategy testing tool
├── src/                        # Source code directory
│   ├── config/
│   │   └── config.py           # Configuration management
│   ├── api/
│   │   └── binance_client.py   # Binance API client
│   ├── models/
│   │   └── trade.py            # Data models and enums
│   ├── strategies/
│   │   ├── base_strategy.py    # Abstract strategy base class
│   │   ├── simple_moving_average.py # SMA crossover strategy
│   │   └── trading_bot.py      # Trading bot orchestrator
│   ├── backtesting/
│   │   ├── backtest_engine.py  # Backtesting engine
│   │   └── data_loader.py      # Historical data loader
│   └── utils/
│       └── logger.py           # Logging utilities
└── tests/                      # Test directory (placeholder)
    └── __init__.py
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Binance account with API keys
- Virtual environment (recommended)

### Step-by-Step Installation

1. **Clone and navigate to project:**
   ```bash
   cd crypto-trading
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your Binance API keys
   ```

5. **Verify installation:**
   ```bash
   .venv/bin/python -c "import src; print('Installation successful!')"
   ```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Binance API Configuration
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
BINANCE_TESTNET=true

# Trading Configuration
TRADE_AMOUNT=0.001
MAX_DAILY_TRADES=5
SYMBOL=BTCUSDT

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=trading_bot.log
```

### Configuration Class (src/config/config.py)

The `Config` class manages all configuration settings:

```python
from src.config.config import Config

config = Config()
print(f"Testnet mode: {config.testnet}")
print(f"Trade amount: {config.trade_amount}")
print(f"API URL: {config.binance_api_url}")
```

---

## 🔧 Core Components

### 1. Binance API Client (src/api/binance_client.py)

Handles all Binance API interactions with HMAC SHA256 authentication.

**Key Features:**
- Authenticated API requests
- Market data retrieval
- Order management
- Balance checking

**Usage Example:**
```python
from src.api.binance_client import BinanceClient
from src.config.config import Config

config = Config()
client = BinanceClient(config)

# Get current price
price = client.get_current_price('BTCUSDT')
print(f"BTC Price: ${price}")

# Get account balance
balance = client.get_balance('USDT')
print(f"USDT Balance: ${balance}")
```

### 2. Data Models (src/models/trade.py)

Defines data structures for trades, market data, and enums.

**Key Classes:**
- `Trade`: Individual trade records
- `MarketData`: Market price and volume data
- `OrderSide`: BUY/SELL enum
- `OrderType`: MARKET/LIMIT enum
- `OrderStatus`: PENDING/FILLED/CANCELLED enum

**Usage Example:**
```python
from src.models.trade import Trade, MarketData, OrderSide
from datetime import datetime

# Create a trade record
trade = Trade(
    symbol="BTCUSDT",
    side=OrderSide.BUY,
    quantity=0.001,
    price=50000.0,
    timestamp=datetime.now()
)

# Create market data
market_data = MarketData(
    symbol="BTCUSDT",
    price=50000.0,
    volume=1000.0,
    timestamp=datetime.now()
)
```

### 3. Logging Utilities (src/utils/logger.py)

Provides comprehensive logging with file and console output.

**Usage Example:**
```python
from src.utils.logger import setup_logger

logger = setup_logger(log_level='DEBUG')
logger.info("Starting trading bot...")
logger.debug("Processing market data...")
logger.error("API connection failed")
```

---

## 📈 Trading Strategies

### Base Strategy (src/strategies/base_strategy.py)

Abstract base class that all trading strategies must inherit from.

**Key Methods:**
- `should_buy(market_data)`: Returns True if buy signal detected
- `should_sell(market_data)`: Returns True if sell signal detected
- `calculate_position_size(market_data)`: Calculates trade quantity
- `execute_trade(signal, market_data)`: Executes the trade

### Simple Moving Average Strategy (src/strategies/simple_moving_average.py)

Implements SMA crossover strategy with golden cross (buy) and death cross (sell) signals.

**Strategy Logic:**
- **Buy Signal**: Short SMA crosses above Long SMA (Golden Cross)
- **Sell Signal**: Short SMA crosses below Long SMA (Death Cross)
- **Position Sizing**: Based on configured trade amount
- **Risk Management**: Take profit and stop loss support

**Usage Example:**
```python
from src.strategies.simple_moving_average import SimpleMovingAverageStrategy
from src.config.config import Config
from src.api.binance_client import BinanceClient

config = Config()
client = BinanceClient(config)

# Create strategy with custom parameters
strategy = SimpleMovingAverageStrategy(
    config=config,
    binance_client=client,
    short_period=5,    # 5-period SMA
    long_period=10     # 10-period SMA
)

# Check for signals
if strategy.should_buy(market_data):
    print("BUY signal detected!")
elif strategy.should_sell(market_data):
    print("SELL signal detected!")
```

### Trading Bot (src/strategies/trading_bot.py)

Orchestrates the trading process, manages daily limits, and tracks performance.

**Key Features:**
- Daily trade limit enforcement
- Performance tracking
- Signal processing
- Trade execution coordination

---

## 🔬 Backtesting Framework

### Backtest Engine (src/backtesting/backtest_engine.py)

Simulates trading on historical data and calculates performance metrics.

**Key Metrics Calculated:**
- Total return and P&L
- Win rate and trade count
- Maximum drawdown
- Sharpe ratio
- Equity curve

**Usage Example:**
```python
from src.backtesting.backtest_engine import BacktestEngine
from src.strategies.simple_moving_average import SimpleMovingAverageStrategy

# Initialize components
strategy = SimpleMovingAverageStrategy(config, client, 5, 10)
engine = BacktestEngine(initial_balance=10000.0)

# Run backtest
result = engine.run_backtest(strategy, historical_data, "BTCUSDT")

# Display results
print(f"Total Return: {result.total_return:.2f}%")
print(f"Win Rate: {result.win_rate:.1f}%")
print(f"Max Drawdown: {result.max_drawdown:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.3f}")
```

### Data Loader (src/backtesting/data_loader.py)

Fetches historical market data from Binance API.

**Supported Timeframes:**
- 1m, 3m, 5m, 15m, 30m
- 1h, 2h, 4h, 6h, 8h, 12h
- 1d, 3d, 1w, 1M

**Usage Example:**
```python
from src.backtesting.data_loader import HistoricalDataLoader
from src.api.binance_client import BinanceClient

client = BinanceClient(config)
loader = HistoricalDataLoader(client)

# Load 90 days of 1-hour data
data = loader.load_historical_data(
    symbol="BTCUSDT",
    interval="1h",
    days=90
)

print(f"Loaded {len(data)} data points")
```

---

## 🎯 Optimization Tools

### 1. Basic Optimization (optimize_strategy.py)

Tests various parameter combinations to find optimal settings.

**Features:**
- Multiple symbols and timeframes
- Parameter grid search
- Performance ranking
- CSV export of results

**Usage:**
```bash
.venv/bin/python optimize_strategy.py
```

### 2. Comprehensive Optimization (comprehensive_optimization.py)

Advanced optimization with detailed analysis and recommendations.

**Features:**
- Symbol-specific optimization
- Multiple performance metrics
- Strategy recommendations
- Risk-adjusted scoring

**Usage:**
```bash
.venv/bin/python comprehensive_optimization.py
```

### 3. Best Strategies Runner (run_best_strategies.py)

Runs and compares the top-performing strategies.

**Features:**
- Strategy comparison table
- Risk profile recommendations
- Live trading setup instructions

**Usage:**
```bash
.venv/bin/python run_best_strategies.py
```

---

## 🚀 Running Examples

### 1. Quick Backtest

Test a strategy with default parameters:

```bash
# Basic backtest
.venv/bin/python backtest.py

# Custom parameters
.venv/bin/python backtest.py --symbol BTCUSDT --days 90 --short-period 5 --long-period 10
```

**Output Example:**
```
============================================================
BACKTEST RESULTS
============================================================
Symbol: BTCUSDT
Period: 90 days (1h intervals)
Strategy: Simple Moving Average

PERFORMANCE METRICS:
  Initial Balance: $10,000.00
  Final Balance:   $9,989.00
  Total Return:    -0.11%
  Total P&L:       $-11.00

TRADING STATISTICS:
  Total Trades:    29
  Winning Trades:  13
  Losing Trades:   16
  Win Rate:        44.8%

RISK METRICS:
  Max Drawdown:    0.23%
  Sharpe Ratio:    -0.095
```

### 2. Strategy Optimization

Find the best parameters:

```bash
# Run optimization
.venv/bin/python optimize_strategy.py

# Run comprehensive optimization
.venv/bin/python comprehensive_optimization.py
```

**Output Example:**
```
====================================================================================================
TOP PERFORMING STRATEGY COMBINATIONS
====================================================================================================

 1. BTCUSDT 4h 180d SMA(5,10)
    Return: +0.06% | Win Rate: 66.7% | Trades: 6
    P&L: $+5.86 | Drawdown: 0.08% | Sharpe: 0.252
    Score: 16.742

 2. BTCUSDT 1h 60d SMA(12,15)
    Return: +0.10% | Win Rate: 60.0% | Trades: 20
    P&L: $+10.62 | Drawdown: 0.20% | Sharpe: 0.400
    Score: 15.166
```

### 3. Best Strategies Comparison

Compare top-performing strategies:

```bash
.venv/bin/python run_best_strategies.py
```

**Output Example:**
```
============================================================================================================
BEST STRATEGIES COMPARISON
============================================================================================================
Strategy                                 Return   Win Rate   Trades   Sharpe   Drawdown   P&L         
------------------------------------------------------------------------------------------------------------
BTCUSDT 4h - Best Overall (66.7% Win Rate) +0.06%    66.7%         6   0.252    0.08%    $   +5.86
BTCUSDT 1h - High Return (0.10%)         +0.10%    60.0%        20   0.400    0.20%    $  +10.62
BTCUSDT 1h - Best Sharpe Ratio (0.409)   +0.09%    50.0%         6   0.409    0.21%    $   +9.03
```

### 4. Debug Strategy Issues

Troubleshoot strategy problems:

```bash
.venv/bin/python debug_backtest.py
```

### 5. Test Strategy Logic

Verify strategy with synthetic data:

```bash
.venv/bin/python test_strategy.py
```

---

## 🔄 Retraining & Optimization

### When to Retrain

Retrain your strategy when:
- Market conditions change significantly
- Performance degrades over time
- New data becomes available
- Strategy parameters need adjustment

### Retraining Process

#### Step 1: Collect New Data

```bash
# Run optimization with recent data
.venv/bin/python comprehensive_optimization.py
```

#### Step 2: Analyze Results

Review the optimization results:
- Check if current parameters still perform well
- Identify new optimal parameter combinations
- Consider market regime changes

#### Step 3: Update Strategy Parameters

Edit `src/strategies/simple_moving_average.py`:

```python
class SimpleMovingAverageStrategy(BaseStrategy):
    def __init__(self, config, binance_client, short_period: int = 5, long_period: int = 10):
        # Update default parameters based on optimization results
        super().__init__(config, binance_client)
        self.short_period = short_period
        self.long_period = long_period
        self.price_history = []
```

#### Step 4: Validate Changes

```bash
# Test updated strategy
.venv/bin/python backtest.py --symbol BTCUSDT --days 180 --short-period 5 --long-period 10

# Compare with previous results
.venv/bin/python run_best_strategies.py
```

### Automated Retraining Script

Create a retraining script for regular updates:

```python
#!/usr/bin/env python3
"""
Automated retraining script
"""

import subprocess
import sys
from datetime import datetime

def run_retraining():
    """Run complete retraining process"""
    print(f"Starting retraining at {datetime.now()}")
    
    # Step 1: Run optimization
    print("Running optimization...")
    subprocess.run([sys.executable, "comprehensive_optimization.py"])
    
    # Step 2: Run best strategies comparison
    print("Comparing best strategies...")
    subprocess.run([sys.executable, "run_best_strategies.py"])
    
    # Step 3: Generate report
    print("Generating retraining report...")
    # Add report generation logic here
    
    print("Retraining completed!")

if __name__ == "__main__":
    run_retraining()
```

### Performance Monitoring

Monitor strategy performance over time:

```python
# Create performance tracking
from datetime import datetime, timedelta
import json

def track_performance():
    """Track daily performance"""
    performance_data = {
        'date': datetime.now().isoformat(),
        'strategy': 'SMA(5,10)',
        'symbol': 'BTCUSDT',
        'return': 0.06,
        'win_rate': 66.7,
        'trades': 6
    }
    
    # Save to file
    with open('performance_log.json', 'a') as f:
        f.write(json.dumps(performance_data) + '\n')
```

---

## 💰 Live Trading

### Prerequisites

1. **Binance Account Setup:**
   - Create Binance account
   - Enable API access
   - Generate API key and secret
   - Set appropriate permissions (spot trading)

2. **Environment Configuration:**
   ```bash
   # Edit .env file
   BINANCE_API_KEY=your_real_api_key
   BINANCE_SECRET_KEY=your_real_secret_key
   BINANCE_TESTNET=false  # Set to false for live trading
   ```

3. **Strategy Configuration:**
   ```python
   # Update strategy parameters in src/strategies/simple_moving_average.py
   short_period = 5   # Based on optimization results
   long_period = 10   # Based on optimization results
   ```

### Starting Live Trading

```bash
# Start live trading
.venv/bin/python main.py
```

**Live Trading Output:**
```
2025-07-20 18:30:00 - INFO - Starting crypto trading bot...
2025-07-20 18:30:00 - INFO - Configuration loaded. Testnet: False
2025-07-20 18:30:00 - INFO - Binance client initialized
2025-07-20 18:30:00 - INFO - Strategy initialized: SMA(5, 10)
2025-07-20 18:30:00 - INFO - Trading bot started
2025-07-20 18:30:00 - INFO - Current BTCUSDT price: $108,731.76
2025-07-20 18:30:00 - INFO - Checking for trading signals...
2025-07-20 18:30:00 - INFO - No signals detected
2025-07-20 18:30:00 - INFO - Waiting 60 seconds before next check...
```

### Monitoring Live Trading

1. **Check Logs:**
   ```bash
   tail -f trading_bot.log
   ```

2. **Monitor Performance:**
   ```bash
   # Check current balance
   .venv/bin/python -c "
   from src.config.config import Config
   from src.api.binance_client import BinanceClient
   config = Config()
   client = BinanceClient(config)
   print(f'USDT Balance: ${client.get_balance(\"USDT\")}')
   print(f'BTC Balance: {client.get_balance(\"BTC\")}')
   "
   ```

3. **Stop Trading:**
   ```bash
   # Use Ctrl+C to stop the bot
   # Or kill the process
   pkill -f "python main.py"
   ```

### Risk Management

1. **Set Daily Limits:**
   ```python
   # In .env file
   MAX_DAILY_TRADES=5
   TRADE_AMOUNT=0.001
   ```

2. **Monitor Drawdown:**
   - Set maximum acceptable drawdown
   - Implement automatic stop-loss
   - Monitor win rate

3. **Backup Strategies:**
   - Keep multiple strategy configurations
   - Have fallback parameters ready
   - Monitor market conditions

---

## 🔧 Troubleshooting

### Common Issues

#### 1. API Connection Errors

**Problem:** Cannot connect to Binance API
```
ERROR - Failed to connect to Binance API: HTTPSConnectionPool
```

**Solution:**
```bash
# Check internet connection
ping api.binance.com

# Verify API keys
.venv/bin/python -c "
from src.config.config import Config
config = Config()
print(f'API Key: {config.api_key[:10]}...')
print(f'Testnet: {config.testnet}')
"
```

#### 2. Insufficient Balance

**Problem:** Not enough balance for trades
```
ERROR - Insufficient balance for trade
```

**Solution:**
```bash
# Check current balance
.venv/bin/python -c "
from src.config.config import Config
from src.api.binance_client import BinanceClient
config = Config()
client = BinanceClient(config)
print(f'USDT: ${client.get_balance(\"USDT\")}')
print(f'BTC: {client.get_balance(\"BTC\")}')
"
```

#### 3. No Trading Signals

**Problem:** Strategy not generating signals
```
INFO - No signals detected
```

**Solution:**
```bash
# Debug strategy logic
.venv/bin/python debug_backtest.py

# Test with different parameters
.venv/bin/python backtest.py --short-period 3 --long-period 7
```

#### 4. Import Errors

**Problem:** Module not found errors
```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
# Ensure you're in the correct directory
pwd  # Should show /path/to/crypto-trading

# Activate virtual environment
source .venv/bin/activate

# Check Python path
python -c "import sys; print(sys.path)"
```

### Debug Tools

#### 1. Debug Backtest
```bash
.venv/bin/python debug_backtest.py
```

#### 2. Test Strategy Logic
```bash
.venv/bin/python test_strategy.py
```

#### 3. Check API Connection
```bash
.venv/bin/python -c "
from src.config.config import Config
from src.api.binance_client import BinanceClient
config = Config()
client = BinanceClient(config)
print('API connection test...')
price = client.get_current_price('BTCUSDT')
print(f'BTC Price: ${price}')
"
```

### Performance Issues

#### 1. Slow Backtesting
```bash
# Use smaller time periods for testing
.venv/bin/python backtest.py --days 30

# Use larger intervals
.venv/bin/python backtest.py --interval 4h
```

#### 2. Memory Issues
```bash
# Monitor memory usage
top -p $(pgrep python)

# Use smaller data sets
.venv/bin/python backtest.py --days 60
```

---

## 📚 API Reference

### Configuration API

#### Config Class
```python
class Config:
    def __init__(self)
    @property
    def api_key(self) -> str
    @property
    def secret_key(self) -> str
    @property
    def testnet(self) -> bool
    @property
    def trade_amount(self) -> float
    @property
    def max_daily_trades(self) -> int
    @property
    def symbol(self) -> str
    @property
    def binance_api_url(self) -> str
```

### Binance Client API

#### BinanceClient Class
```python
class BinanceClient:
    def __init__(self, config: Config)
    def get_current_price(self, symbol: str) -> float
    def get_balance(self, asset: str) -> float
    def place_order(self, symbol: str, side: OrderSide, 
                   quantity: float, price: float = None) -> dict
    def get_order_status(self, symbol: str, order_id: str) -> dict
    def cancel_order(self, symbol: str, order_id: str) -> dict
    def get_historical_data(self, symbol: str, interval: str, 
                          limit: int = 1000) -> List[dict]
```

### Strategy API

#### BaseStrategy Class
```python
class BaseStrategy(ABC):
    def __init__(self, config: Config, binance_client: BinanceClient)
    @abstractmethod
    def should_buy(self, market_data: MarketData) -> bool
    @abstractmethod
    def should_sell(self, market_data: MarketData) -> bool
    @abstractmethod
    def calculate_position_size(self, market_data: MarketData) -> float
    def execute_trade(self, signal: str, market_data: MarketData) -> bool
```

#### SimpleMovingAverageStrategy Class
```python
class SimpleMovingAverageStrategy(BaseStrategy):
    def __init__(self, config: Config, binance_client: BinanceClient, 
                 short_period: int = 10, long_period: int = 20)
    def should_buy(self, market_data: MarketData) -> bool
    def should_sell(self, market_data: MarketData) -> bool
    def calculate_position_size(self, market_data: MarketData) -> float
    def _calculate_sma(self, period: int, offset: int = 0) -> float
    def _check_take_profit_stop_loss(self, market_data: MarketData) -> bool
```

### Backtesting API

#### BacktestEngine Class
```python
class BacktestEngine:
    def __init__(self, initial_balance: float = 10000.0)
    def run_backtest(self, strategy: BaseStrategy, 
                    historical_data: List[MarketData], 
                    symbol: str = "BTCUSDT") -> BacktestResult
    def _update_strategy_data(self, strategy: BaseStrategy, 
                            market_data: MarketData)
    def _process_signals(self, strategy: BaseStrategy, 
                        market_data: MarketData, symbol: str)
    def _execute_buy_signal(self, strategy: BaseStrategy, 
                           market_data: MarketData, symbol: str)
    def _execute_sell_signal(self, strategy: BaseStrategy, 
                            market_data: MarketData, symbol: str)
```

#### BacktestResult Class
```python
@dataclass
class BacktestResult:
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
```

### Data Models API

#### Trade Class
```python
@dataclass
class Trade:
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime
    order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    net_value: Optional[float] = None
```

#### MarketData Class
```python
@dataclass
class MarketData:
    symbol: str
    price: float
    volume: float
    timestamp: datetime
```

#### Enums
```python
class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
```

---

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📞 Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Test with the debug tools provided
- Ensure your environment is properly configured

---

*This documentation covers all aspects of the crypto trading bot. For additional help, refer to the individual file comments and the Binance API documentation.* 