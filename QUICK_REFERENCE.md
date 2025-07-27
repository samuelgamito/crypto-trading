# Crypto Trading Bot - Quick Reference Guide

## 🚀 Quick Start Commands

### Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Setup environment
cp env.example .env
# Edit .env with your API keys and preferences
```

### Basic Usage

#### Run Backtest
```bash
# Quick backtest with defaults
.venv/bin/python backtest.py

# Custom parameters
.venv/bin/python backtest.py --symbol BTCUSDT --days 90 --short-period 12 --long-period 15

# Different timeframe
.venv/bin/python backtest.py --interval 4h --days 180
```

#### Live Trading
```bash
# Start live trading
.venv/bin/python main.py

# Stop trading: Ctrl+C
```

## 🎯 Current Strategy

### SMA Crossover Settings
- **Short SMA**: 12 periods
- **Long SMA**: 15 periods
- **Trade Percentage**: 5% of total wallet
- **Stop Loss**: 2.0%
- **Take Profit**: 5.0%
- **Max Daily Trades**: 10

### Recommended Trade Percentages
- **Conservative**: 2-3% of wallet
- **Balanced**: 5% of wallet (default)
- **Active**: 7-10% of wallet

## 🔧 Configuration

### Environment Variables (.env)
```bash
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
BINANCE_TESTNET=true  # Set to false for live trading
DEFAULT_SYMBOL=BTCUSDT
TRADE_PERCENTAGE=5.0  # Percentage of total wallet
MAX_DAILY_TRADES=10
STOP_LOSS_PERCENTAGE=2.0
TAKE_PROFIT_PERCENTAGE=5.0
```

### Strategy Parameters
```python
# In src/strategies/simple_moving_average.py
short_period = 12    # Short SMA period
long_period = 15     # Long SMA period
```

## 📊 Performance Metrics

### Key Metrics Explained
- **Total Return**: Overall percentage gain/loss
- **Win Rate**: Percentage of profitable trades
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return measure
- **Total Trades**: Number of executed trades
- **Trade Percentage**: Percentage of wallet used per trade

### Good Performance Targets
- **Win Rate**: >50%
- **Sharpe Ratio**: >0.2
- **Max Drawdown**: <1%
- **Total Return**: >0% (positive)

## 🛠️ Troubleshooting

### Common Issues

#### API Connection Error
```bash
# Check API keys
.venv/bin/python -c "
from src.config.config import Config
config = Config()
print(f'API Key: {config.api_key[:10]}...')
print(f'Testnet: {config.testnet}')
"
```

#### No Trading Signals
```bash
# Check current market conditions
.venv/bin/python -c "
from src.config.config import Config
from src.api.binance_client import BinanceClient
from src.strategies.trading_bot import TradingBot
config = Config()
client = BinanceClient(config)
bot = TradingBot(config, client)
market_data = bot.strategy.get_market_data('BTCUSDT')
print(f'Current price: ${market_data.price}')
print(f'Price history length: {len(bot.strategy.price_history)}')
"
```

#### Import Errors
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Check Python path
python -c "import sys; print(sys.path)"
```

## 📈 Live Trading Checklist

### Before Starting
- [ ] API keys configured in .env
- [ ] Testnet mode disabled (BINANCE_TESTNET=false) for live trading
- [ ] Strategy parameters set (SMA 12,15)
- [ ] Risk management limits configured
- [ ] Sufficient USDT balance available

### During Trading
- [ ] Monitor console output for real-time updates
- [ ] Check logs: `tail -f logs/trading_bot.log`
- [ ] Monitor portfolio balances
- [ ] Verify trade execution and amounts

### Emergency Stop
```bash
# Stop trading immediately
pkill -f "python main.py"

# Or use Ctrl+C in terminal
```

## 🎯 Strategy Selection Guide

### Conservative Investor
- **Trade Percentage**: 2-3% of wallet
- **Risk**: Very Low
- **Activity**: Low
- **Best For**: Capital preservation

### Balanced Trader
- **Trade Percentage**: 5% of wallet (default)
- **Risk**: Low
- **Activity**: Medium
- **Best For**: Steady growth

### Active Trader
- **Trade Percentage**: 7-10% of wallet
- **Risk**: Medium
- **Activity**: High
- **Best For**: Maximum returns

## 📝 Useful Commands

### Check Balance
```bash
.venv/bin/python -c "
from src.config.config import Config
from src.api.binance_client import BinanceClient
config = Config()
client = BinanceClient(config)
usdt = client.get_balance('USDT')
btc = client.get_balance('BTC')
print(f'USDT: ${usdt:,.2f}')
print(f'BTC: {btc:.6f}')
"
```

### Get Current Price
```bash
.venv/bin/python -c "
from src.config.config import Config
from src.api.binance_client import BinanceClient
config = Config()
client = BinanceClient(config)
ticker = client.get_ticker_price('BTCUSDT')
print(f'BTC Price: ${ticker[\"price\"]}')
"
```

### Check Configuration
```bash
.venv/bin/python -c "
from src.config.config import Config
config = Config()
print(f'Testnet: {config.testnet}')
print(f'Trade Percentage: {config.trade_percentage}%')
print(f'Default Symbol: {config.default_symbol}')
"
```

## 📊 Performance Monitoring

### Daily Performance Check
```bash
# Run daily backtest
.venv/bin/python backtest.py --days 1

# Check live performance
# Monitor console output and logs
```

### Weekly Strategy Review
```bash
# Run backtest with recent data
.venv/bin/python backtest.py --days 30

# Update strategy parameters if needed
# Edit src/strategies/simple_moving_average.py
```

## 🚨 Risk Management

### Daily Limits
```bash
# In .env file
MAX_DAILY_TRADES=10
TRADE_PERCENTAGE=5.0
```

### Stop Loss & Take Profit
```bash
# In .env file
STOP_LOSS_PERCENTAGE=2.0
TAKE_PROFIT_PERCENTAGE=5.0
```

### Balance Validation
- Bot automatically checks USDT balance before trading
- Ensures sufficient funds for trade amount
- Prevents over-leveraging

---

## 📞 Need Help?

1. Check the full documentation: `DOCUMENTATION.md`
2. Review trading decisions: `TRADING_DECISIONS.md`
3. Check troubleshooting section
4. Verify configuration settings

---

*This quick reference covers the most important commands and information. For detailed explanations, see the full documentation.* 