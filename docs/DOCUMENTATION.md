# Crypto Trading Bot - Complete Documentation

## 📚 Documentation Index

### 🎯 Overview
- **[Executive Summary](EXECUTIVE_SUMMARY.md)** - Resumo executivo do projeto
- **[README](README.md)** - Guia principal de uso e instalação

### 🔧 Technical Documentation
- **[Trading Strategies](TRADING_STRATEGIES.md)** - Detalhes das estratégias implementadas
- **[Technical Implementation](TECHNICAL_IMPLEMENTATION.md)** - Arquitetura técnica detalhada
- **[Deployment Guide](DEPLOYMENT.md)** - Guia de deploy e configuração

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone repository
git clone <repository-url>
cd crypto-trading

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env with your Binance API keys
nano .env
```

### 3. Run Trading Bot
```bash
# Start the enhanced trading bot
python3 main.py
```

## 🎯 System Overview

### Dual Strategy Architecture
O sistema implementa **duas estratégias complementares**:

1. **SMA Crossover Strategy** (12/15 períodos)
2. **RSI + Volume Filters Strategy** (14/20 períodos)

### Smart Signal Combination
- **STRONG SIGNALS**: Ambas estratégias concordam
- **MODERATE SIGNALS**: SMA sinaliza, RSI neutro
- **CONSERVATIVE SIGNALS**: RSI extremo com confirmação

### Real-time Monitoring
```
🚀 Enhanced trading bot started! Using SMA + RSI + Volume strategies...
📊 Monitoring BTCBRL with dual strategy analysis...
💰 Wallet: BRL 1,913.48 | BTC 0.000130 (R$ 86.27) | Total: 1,999.75
📊 BTCBRL: 664,870.00
   📈 SMA: 662,884.92/662,385.93 | RSI: 64.5 | Vol: 0.0x
   🎯 Trades: 0/10
```

## 📁 Project Structure

```
crypto-trading/
├── src/
│   ├── strategies/
│   │   ├── base_strategy.py          # Interface comum
│   │   ├── simple_moving_average.py  # Estratégia SMA
│   │   ├── rsi_volume_strategy.py    # Estratégia RSI + Volume
│   │   └── trading_bot.py           # Bot principal
│   ├── utils/
│   │   ├── indicators.py            # Indicadores técnicos
│   │   ├── fee_manager.py          # Gerenciamento de taxas
│   │   └── binance_logger.py       # Sistema de logging
│   ├── models/
│   │   └── trade.py                # Modelos de dados
│   ├── api/
│   │   └── binance_client.py       # Cliente Binance API
│   └── config/
│       └── config.py               # Configurações
├── main.py                         # Entry point
├── backtest.py                     # Backtesting engine
├── requirements.txt                # Dependencies
├── env.example                     # Environment template
├── Dockerfile                      # Docker configuration
└── docker-compose.yml             # Docker compose
```

## 🔧 Configuration

### Environment Variables
```bash
# Binance API Configuration
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
BINANCE_TESTNET=true

# Trading Configuration
TRADING_SYMBOL=BTCBRL
TRADE_PERCENTAGE=5.0
MAX_DAILY_TRADES=10

# Strategy Parameters
SMA_SHORT_PERIOD=12
SMA_LONG_PERIOD=15
RSI_PERIOD=14
VOLUME_PERIOD=20
```

### Strategy Parameters
```python
# SMA Strategy
short_period = 12  # Fast SMA
long_period = 15   # Slow SMA

# RSI + Volume Strategy
rsi_period = 14      # RSI calculation period
volume_period = 20   # Volume SMA period
```

## 📊 Performance Tracking

### Strategy Metrics
- **SMA Signals**: Contador de sinais da estratégia SMA
- **RSI Signals**: Contador de sinais da estratégia RSI+Volume
- **Combined Signals**: Contador de sinais onde ambas concordam

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

## 🛡️ Risk Management

### Position Sizing
- **Trade Size**: 5% do wallet total por trade
- **Daily Limit**: Máximo 10 trades por dia
- **Balance Checks**: Validação antes de cada trade

### Filters
- **Volume Filters**: Evita trades em baixa liquidez
- **RSI Filters**: Evita condições extremas de mercado
- **Signal Quality**: Diferentes níveis de confiança

## 🔍 Monitoring and Logging

### Real-time Display
- Preços atuais e indicadores técnicos
- Status das estratégias em tempo real
- Informações de wallet e posições

### Enhanced Logging
- Logs detalhados de todas as operações
- Performance tracking por estratégia
- Error handling e debugging

### Log Files
```
logs/
├── binance/           # Binance API logs
├── trading_bot.log    # Trading bot logs
└── errors.log         # Error logs
```

## 🧪 Testing

### Backtesting
```bash
# Run backtest with default parameters
python3 backtest.py

# Custom backtest parameters
python3 backtest.py --symbol BTCBRL --days 90 --short-period 12 --long-period 15
```

### API Connection Test
```bash
# Test Binance API connection
python3 validation/test_api_connection.py
```

## 🚀 Deployment

### Local Development
```bash
# Run locally
python3 main.py
```

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up -d
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f kubernetes/
```

## 🔮 Future Enhancements

### Planned Features
1. **Dynamic Parameters**: Ajuste automático baseado em performance
2. **Weighted Signals**: Peso diferente para cada estratégia
3. **More Indicators**: MACD, Bollinger Bands, etc.
4. **Machine Learning**: Otimização baseada em dados históricos

### Monitoring Goals
- Acompanhar performance de cada estratégia individualmente
- Analisar taxa de sinais combinados vs. individuais
- Ajustar parâmetros baseado em resultados reais

## 🚨 Important Notes

### Risk Considerations
- **Market Volatility**: Criptomoedas são altamente voláteis
- **API Dependencies**: Dependência da conectividade com Binance
- **Parameter Sensitivity**: Sensível a parâmetros de configuração

### Best Practices
- **Testnet First**: Sempre teste em testnet antes de produção
- **Monitor Performance**: Acompanhe métricas regularmente
- **Adjust Parameters**: Ajuste parâmetros baseado em resultados
- **Backup Configuration**: Mantenha backup das configurações

## 📞 Support

### Documentation
- **Technical Issues**: Consulte `TECHNICAL_IMPLEMENTATION.md`
- **Strategy Details**: Consulte `TRADING_STRATEGIES.md`
- **Deployment Issues**: Consulte `DEPLOYMENT.md`

### Logs and Debugging
- Verifique logs em `logs/` directory
- Use `validation/test_api_connection.py` para testar conectividade
- Monitore performance em tempo real

---

**⚠️ Disclaimer**: Este sistema é para fins educacionais. Trading de criptomoedas envolve riscos significativos. Sempre teste em testnet antes de usar em produção. 