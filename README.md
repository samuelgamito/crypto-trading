# 🚀 Crypto Trading Bot

A sophisticated Python-based cryptocurrency trading bot with dual strategy system, intelligent position sizing, and MongoDB signal logging for automated trading on Binance.

## ✨ Features

- **🤖 Automated Trading**: Real-time trading via Binance API with testnet support
- **📊 Dual Strategy System**: SMA Crossover + RSI + Volume Filters
- **💰 Smart Position Sizing**: Percentage-based trading with balance validation
- **📈 MongoDB Signal Logging**: Complete signal history with detailed analytics
- **🛡️ Risk Management**: Stop-loss, take-profit, and daily trade limits
- **🔍 Performance Analytics**: Comprehensive metrics and trade logging

## 🎯 Trading Strategies

### Dual Strategy System

#### 1. Simple Moving Average (SMA) Crossover
- **Short SMA (12-period)**: Faster moving average
- **Long SMA (15-period)**: Slower moving average
- **Golden Cross (Buy)**: Short SMA crosses above Long SMA
- **Death Cross (Sell)**: Short SMA crosses below Long SMA

#### 2. RSI + Volume Filters
- **RSI (14-period)**: Relative Strength Index for momentum
- **Volume Confirmation**: Volume must be above moving average
- **Buy Signal**: RSI < 70 (not overbought) AND Volume > Average
- **Sell Signal**: RSI > 30 (not oversold) AND Volume > Average

#### Smart Signal Combination
- **STRONG**: Both strategies agree
- **MODERATE**: SMA signals, RSI neutral
- **CONSERVATIVE**: RSI extreme with volume confirmation

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

### 2. Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env with your settings
nano .env
```

### 3. Run Trading Bot
```bash
# Start live trading
python3 main.py

# Run backtest
python3 backtest.py
```

## 📁 Project Structure

```
crypto-trading/
├── main.py                    # Live trading entry point
├── backtest.py               # Backtesting utility
├── requirements.txt          # Python dependencies
├── env.example              # Environment template
├── validation/              # Test and validation scripts
│   ├── test_api_connection.py
│   ├── test_mongo_auth.py
│   ├── test_sell_order.py
│   └── test_buy_order.py
├── src/
│   ├── config/              # Configuration management
│   ├── api/                 # Binance API client
│   ├── models/              # Data models
│   ├── strategies/          # Trading strategies
│   ├── utils/               # Utilities (indicators, logging, etc.)
│   └── backtesting/         # Backtesting engine
└── docs/                    # Documentation
```

## 📊 MongoDB Signal Structure

Every trading signal is logged to MongoDB with this structure:

```json
{
  "signals": [
    {
      "signal": "SMA_BUY|SMA_SELL|RSI_BUY|RSI_SELL|VOLUME_BUY|VOLUME_SELL",
      "result": "true|false",
      "value": "Signal Value",
      "threshold": "Signal Threshold"
    }
  ],
  "decision": "BUY|SELL|KEEP",
  "strength": "CONSERVATIVE|MODERATE|STRONG",
  "reason": "Signal reasoning",
  "executed": true|false,
  "failure_reason": "Reason if execution failed",
  "created_at": "2025-01-01T00:00:00.000Z"
}
```

## 🗄️ MongoDB Authentication

The bot supports MongoDB authentication with username and password:

### Local MongoDB (No Auth)
```bash
MONGO_CONNECTION_STRING=mongodb://localhost:27017/
MONGO_USERNAME=
MONGO_PASSWORD=
```

### MongoDB with Authentication
```bash
MONGO_CONNECTION_STRING=mongodb://localhost:27017/
MONGO_USERNAME=your_username
MONGO_PASSWORD=your_password
```

### MongoDB Atlas (Cloud)
```bash
MONGO_CONNECTION_STRING=mongodb+srv://cluster.mongodb.net/
MONGO_USERNAME=your_atlas_username
MONGO_PASSWORD=your_atlas_password
```

### Test MongoDB Connection
```bash
python3 validation/test_mongo_auth.py
```

## 📚 Documentation

- [📖 Complete Documentation](docs/DOCUMENTATION.md)
- [⚡ Quick Reference](docs/QUICK_REFERENCE.md)
- [🎯 Trading Decisions](docs/TRADING_DECISIONS.md)
- [🔧 Technical Implementation](docs/TECHNICAL_IMPLEMENTATION.md)
- [📋 Executive Summary](docs/EXECUTIVE_SUMMARY.md)

## ⚙️ Configuration

Key environment variables:

```bash
# Binance API
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
BINANCE_TESTNET=true

# Trading Settings
TRADE_PERCENTAGE=5.0
MAX_DAILY_TRADES=10
DEFAULT_SYMBOL=BTCBRL

# MongoDB
MONGO_CONNECTION_STRING=mongodb://localhost:27017/
MONGO_DATABASE=crypto_trading
MONGO_USERNAME=your_mongo_username
MONGO_PASSWORD=your_mongo_password
ENABLE_MONGO_LOGGING=true
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.