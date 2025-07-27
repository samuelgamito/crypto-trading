# 🚀 Crypto Trading Bot

A sophisticated Python-based cryptocurrency trading bot with intelligent percentage-based position sizing, real-time portfolio tracking, and advanced risk management for automated trading on Binance.

## ✨ Features

- **🤖 Automated Trading**: Real-time trading via Binance API with testnet support
- **💰 Smart Position Sizing**: Percentage-based trading (5% of total wallet per trade)
- **📊 Portfolio Tracking**: Real-time USDT and BTC balance monitoring
- **🛡️ Risk Management**: Built-in stop-loss, take-profit, and daily limits
- **📈 SMA Crossover Strategy**: Golden cross/death cross signals
- **🔍 Performance Analytics**: Comprehensive metrics and detailed trade logging
- **📚 Complete Documentation**: Extensive guides and quick references

## 🎯 Trading Strategy

### Simple Moving Average (SMA) Crossover
- **Short SMA (12-period)**: Faster moving average
- **Long SMA (15-period)**: Slower moving average
- **Golden Cross (Buy)**: Short SMA crosses above Long SMA
- **Death Cross (Sell)**: Short SMA crosses below Long SMA

### Smart Position Sizing
- **Percentage-based**: 5% of total wallet balance per trade
- **Dynamic calculation**: Adapts to your current portfolio value
- **Risk management**: Ensures controlled exposure
- **Balance validation**: Checks sufficient USDT before trading

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone repository
git clone <repository-url>
cd crypto-trading

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Copy environment template
cp env.example .env

# Edit .env with your Binance API keys and preferences
nano .env
```

### 3. Run Backtest (Optional)
```bash
# Test strategy performance
.venv/bin/python backtest.py

# Custom parameters
.venv/bin/python backtest.py --symbol BTCUSDT --days 90 --short-period 12 --long-period 15
```

### 4. Start Live Trading
```bash
# Start trading (testnet mode by default)
.venv/bin/python main.py
```

## 📁 Project Structure

```
crypto-trading/
├── 📄 main.py                     # 🚀 Live trading entry point
├── 📊 backtest.py                 # 📊 Backtesting utility
├── 📚 DOCUMENTATION.md            # 📖 Complete documentation
├── ⚡ QUICK_REFERENCE.md          # ⚡ Quick reference guide
├── 🎯 TRADING_DECISIONS.md        # 🎯 Decision logic guide
├── src/
│   ├── config/                    # ⚙️ Configuration management
│   ├── api/                       # 🔌 Binance API client
│   ├── models/                    # 📋 Data models
│   ├── strategies/                # 📈 Trading strategies
│   ├── backtesting/               # 🧪 Backtesting framework
│   └── utils/                     # 🛠️ Utilities and logging
├── tests/                         # 🧪 Test files
└── logs/                          # 📝 Log files
```

## 🔧 Key Components

### Trading Strategy
- **Simple Moving Average (SMA) Crossover**: Golden cross/death cross signals
- **Extensible Architecture**: Easy to add new strategies
- **Risk Management**: Position sizing and stop-loss

### Backtesting Framework
- **Historical Data**: Real Binance market data
- **Performance Metrics**: Return, win rate, drawdown, Sharpe ratio
- **Trade Analysis**: Detailed trade history and equity curves

### Live Trading Features
- **Real-time monitoring**: Every 30 seconds
- **Portfolio tracking**: USDT and BTC balances
- **Detailed logging**: Trade amounts, percentages, and decisions
- **Balance validation**: Ensures sufficient funds before trading

## 📊 Example Output

### Live Trading Display
```
🚀 Trading bot started! Monitoring BTCUSDT...
💰 Wallet: USDT $98,607.66 | BTC 0.184650 ($21,786.34) | Total: $120,394.00
📊 BTCUSDT: $117,987.23 | Trades: 0/10

🟢 BUYING 0.051019 BTC
   💰 Trade Value: $6,019.71
   📊 Price: $117,987.23
   📈 Percentage: 5.0% of total wallet
   💼 Total Wallet: $120,394.00
   💵 USDT Balance: $98,607.66
   🪙 BTC Balance: 0.184650 BTC
   ✅ BUY ORDER EXECUTED!
```

### Backtest Results
```
============================================================
BACKTEST RESULTS
============================================================
Symbol: BTCUSDT
Period: 30 days (1h intervals)
Strategy: Simple Moving Average

PERFORMANCE METRICS:
  Initial Balance: $10,000.00
  Final Balance:   $10,150.00
  Total Return:    +1.50%
  Total P&L:       $+150.00

TRADING STATISTICS:
  Total Trades:    15
  Winning Trades:  9
  Losing Trades:   6
  Win Rate:        60.0%

RISK METRICS:
  Max Drawdown:    0.45%
  Sharpe Ratio:    0.85
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Binance API Configuration
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
BINANCE_TESTNET=true  # Set to false for live trading

# Trading Configuration
DEFAULT_SYMBOL=BTCUSDT
TRADE_PERCENTAGE=5.0  # Percentage of total wallet per trade
MAX_DAILY_TRADES=10
STOP_LOSS_PERCENTAGE=2.0
TAKE_PROFIT_PERCENTAGE=5.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/trading_bot.log
```

### Strategy Parameters
```python
# In src/strategies/simple_moving_average.py
short_period = 12    # Short SMA period
long_period = 15     # Long SMA period
```

## 🛠️ Usage Examples

### Basic Backtesting
```bash
# Default backtest
.venv/bin/python backtest.py

# Custom parameters
.venv/bin/python backtest.py --symbol BTCUSDT --days 180 --short-period 12 --long-period 15

# Different timeframe
.venv/bin/python backtest.py --interval 4h --days 90
```

### Live Trading
```bash
# Start live trading (ensure API keys are configured)
.venv/bin/python main.py

# Stop trading: Ctrl+C
```

### Configuration Check
```bash
# Check configuration
.venv/bin/python -c "
from src.config.config import Config
config = Config()
print(f'Testnet: {config.testnet}')
print(f'Trade Percentage: {config.trade_percentage}%')
print(f'Default Symbol: {config.default_symbol}')
"
```

## 🛡️ Risk Management

### Built-in Safety Features
- **Percentage-based trading**: 5% of total wallet per trade
- **Daily Trade Limits**: Maximum 10 trades per day
- **Stop Loss**: 2.0% automatic loss protection
- **Take Profit**: 5.0% automatic profit taking
- **Balance Validation**: Ensures sufficient USDT before trading
- **Testnet Mode**: Safe testing with no real money

### Risk Guidelines
- **Conservative**: Lower trade percentage (2-3%)
- **Balanced**: Default 5% trade percentage
- **Active**: Higher trade percentage (7-10%)

## 📚 Documentation

- **[Complete Documentation](DOCUMENTATION.md)**: Comprehensive guide with all details
- **[Quick Reference](QUICK_REFERENCE.md)**: Essential commands and examples
- **[Trading Decisions](TRADING_DECISIONS.md)**: Detailed decision-making logic
- **[API Reference](DOCUMENTATION.md#api-reference)**: Technical API documentation

## 🛠️ Troubleshooting

### Common Issues

#### API Connection Problems
```bash
# Check API configuration
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

## 📈 Performance Metrics

### Key Metrics Explained
- **Total Return**: Overall percentage gain/loss
- **Win Rate**: Percentage of profitable trades
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return measure
- **Total Trades**: Number of executed trades
- **Trade Percentage**: Percentage of wallet used per trade

### Performance Targets
- **Win Rate**: >50%
- **Sharpe Ratio**: >0.2
- **Max Drawdown**: <1%
- **Total Return**: >0% (positive)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes. Cryptocurrency trading involves substantial risk of loss. Use at your own risk and never invest more than you can afford to lose.

## 📞 Support

For support and questions:
1. Check the [documentation](DOCUMENTATION.md)
2. Review the [troubleshooting section](DOCUMENTATION.md#troubleshooting)
3. Test with the provided backtesting tools
4. Ensure your environment is properly configured

---

**🚀 Ready to start trading? Follow the [Quick Start Guide](#-quick-start) above!**