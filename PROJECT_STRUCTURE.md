# 📁 Project Structure

```
crypto-trading/
├── 📄 main.py                    # 🚀 Live trading entry point
├── 📊 backtest.py               # 📊 Backtesting utility
├── 📋 requirements.txt          # 📦 Python dependencies
├── ⚙️ env.example              # 🔧 Environment template
├── 📖 README.md                 # 📚 Main documentation
├── 📄 LICENSE                   # 📜 MIT License
├── 📁 docs/                     # 📚 Documentation
│   ├── DOCUMENTATION.md         # 📖 Complete documentation
│   ├── EXECUTIVE_SUMMARY.md     # 📋 Executive overview
│   ├── TECHNICAL_IMPLEMENTATION.md # 🔧 Technical details
│   ├── TRADING_STRATEGIES.md    # 📈 Strategy documentation
│   └── DEPLOYMENT.md            # 🚀 Deployment guide
├── 📁 validation/              # 🧪 Test and validation scripts
│   ├── README.md               # 📖 Validation documentation
│   ├── test_api_connection.py  # 🔌 API connection test
│   ├── test_mongo_auth.py      # 🗄️ MongoDB authentication test
│   ├── test_sell_order.py      # 📈 Sell order test
│   └── test_buy_order.py    # 📊 Simple order test
├── 📁 src/                      # 🔧 Source code
│   ├── 📁 api/                  # 🔌 API clients
│   │   ├── __init__.py
│   │   └── binance_client.py    # 🏦 Binance API client
│   ├── 📁 backtesting/          # 🧪 Backtesting engine
│   │   ├── __init__.py
│   │   ├── backtest_engine.py   # 🧪 Backtesting core
│   │   └── data_loader.py       # 📊 Data loading utilities
│   ├── 📁 config/               # ⚙️ Configuration
│   │   ├── __init__.py
│   │   └── config.py            # ⚙️ Configuration management
│   ├── 📁 models/               # 📋 Data models
│   │   ├── __init__.py
│   │   └── trade.py             # 📋 Trade data models
│   ├── 📁 strategies/           # 📈 Trading strategies
│   │   ├── __init__.py
│   │   ├── base_strategy.py     # 🏗️ Base strategy class
│   │   ├── simple_moving_average.py # 📊 SMA strategy
│   │   ├── rsi_volume_strategy.py   # 📈 RSI + Volume strategy
│   │   └── trading_bot.py       # 🤖 Main trading bot
│   ├── 📁 utils/                # 🛠️ Utilities
│   │   ├── __init__.py
│   │   ├── binance_logger.py    # 📝 Binance API logging
│   │   ├── fee_manager.py       # 💰 Fee management
│   │   ├── indicators.py        # 📊 Technical indicators
│   │   ├── logger.py            # 📝 Logging utilities
│   │   ├── mongo_service.py     # 🗄️ MongoDB service
│   │   └── signal_builder.py    # 📊 Signal formatting
│   └── __init__.py
├── 📁 kubernetes/               # ☸️ Kubernetes deployment
│   ├── configmap.yaml           # ⚙️ Configuration
│   ├── deployment.yaml          # 🚀 Deployment
│   └── namespace.yaml           # 📁 Namespace
├── 📁 logs/                     # 📝 Log files
├── 📄 docker-compose.yml        # 🐳 Docker compose
├── 📄 Dockerfile                # 🐳 Docker configuration
├── 📄 deploy.sh                 # 🚀 Deployment script
├── 📄 .gitignore                # 🚫 Git ignore rules
└── 📄 .dockerignore             # 🐳 Docker ignore rules
```

## 🔧 Key Components

### **Core Trading Engine**
- **`main.py`**: Entry point for live trading
- **`backtest.py`**: Historical strategy testing
- **`src/strategies/trading_bot.py`**: Main trading logic

### **Trading Strategies**
- **`src/strategies/simple_moving_average.py`**: SMA crossover strategy
- **`src/strategies/rsi_volume_strategy.py`**: RSI + Volume filters
- **`src/strategies/base_strategy.py`**: Abstract base class

### **API Integration**
- **`src/api/binance_client.py`**: Binance API client
- **`src/utils/binance_logger.py`**: API call logging

### **Data Management**
- **`src/utils/mongo_service.py`**: MongoDB signal storage
- **`src/utils/signal_builder.py`**: Signal formatting
- **`src/models/trade.py`**: Data models

### **Utilities**
- **`src/utils/fee_manager.py`**: Fee calculation and validation
- **`src/utils/indicators.py`**: Technical indicators (RSI, Volume)
- **`src/utils/logger.py`**: Logging setup

### **Configuration**
- **`src/config/config.py`**: Environment-based configuration
- **`env.example`**: Environment template

## 📊 Data Flow

```
Market Data → Strategies → Signal Evaluation → MongoDB Storage
     ↓              ↓              ↓              ↓
Binance API → Dual Strategy → Decision Logic → Signal Logging
```

## 🚀 Deployment Options

1. **Local Development**: `python3 main.py`
2. **Docker**: `docker-compose up`
3. **Kubernetes**: `kubectl apply -f kubernetes/`
4. **Cloud**: Use deployment scripts

## 📝 Logging Structure

```
logs/
├── trading_bot.log          # Main application logs
└── binance/
    ├── binance_api.log      # API call logs
    ├── binance_errors.log   # Error logs
    └── error_*.log          # Detailed error files
``` 