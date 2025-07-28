# Trading Strategies Documentation

## Overview

O sistema de trading implementa **duas estratégias complementares** que trabalham em conjunto para melhorar a precisão dos sinais de trading:

1. **Simple Moving Average (SMA) Strategy**
2. **RSI + Volume Filters Strategy**

## 1. Simple Moving Average (SMA) Strategy

### Implementação: `src/strategies/simple_moving_average.py`

#### Características
- **Short SMA**: 12 períodos (padrão)
- **Long SMA**: 15 períodos (padrão)
- **Intervalo**: 1 hora
- **Símbolo**: BTCBRL

#### Sinais de Trading

**🟢 Buy Signal (Golden Cross)**
- Short SMA cruza acima da Long SMA
- Condição: `prev_short_sma <= prev_long_sma AND short_sma > long_sma`

**🔴 Sell Signal (Death Cross)**
- Short SMA cruza abaixo da Long SMA
- Condição: `prev_short_sma >= prev_long_sma AND short_sma < long_sma`

#### Cálculo SMA
```python
def _calculate_sma(self, period: int, offset: int = 0) -> float:
    """Calculate Simple Moving Average"""
    start_idx = -(period + offset)
    end_idx = -offset if offset > 0 else None
    prices = self.price_history[start_idx:end_idx]
    return sum(prices) / len(prices)
```

## 2. RSI + Volume Filters Strategy

### Implementação: `src/strategies/rsi_volume_strategy.py`

#### Características
- **RSI Period**: 14 períodos (padrão)
- **Volume Period**: 20 períodos (padrão)
- **Intervalo**: 1 hora
- **Símbolo**: BTCBRL

#### Indicadores

**RSI Indicator** (`src/utils/indicators.py`)
- Cálculo padrão de 14 períodos
- Overbought: > 70
- Oversold: < 30

**Volume Indicator** (`src/utils/indicators.py`)
- Média móvel do volume em quote currency (BRL)
- Comparação com volume atual

#### Sinais de Trading

**🟢 Buy Signal**
- RSI < 70 (não sobrecomprado)
- Volume atual > Média móvel do volume
- Condição: `rsi_condition AND volume_condition`

**🔴 Sell Signal**
- RSI > 30 (não sobrevendido)
- Volume atual > Média móvel do volume
- Condição: `rsi_condition AND volume_condition`

## 3. Enhanced Trading Bot

### Implementação: `src/strategies/trading_bot.py`

#### Arquitetura Dual Strategy
```python
class TradingBot:
    def __init__(self, config, binance_client):
        # Initialize both strategies
        self.sma_strategy = SimpleMovingAverageStrategy(config, binance_client)
        self.rsi_volume_strategy = RSIVolumeStrategy(config, binance_client)
        
        # Use SMA strategy as primary (for position management)
        self.strategy = self.sma_strategy
```

#### Lógica de Combinação de Sinais

**🟢 Buy Signal Evaluation**
1. **STRONG BUY**: Ambas as estratégias concordam
2. **MODERATE BUY**: SMA sinaliza, RSI neutro (não overbought)
3. **CONSERVATIVE BUY**: RSI oversold com confirmação de volume

**🔴 Sell Signal Evaluation**
1. **STRONG SELL**: Ambas as estratégias concordam
2. **MODERATE SELL**: SMA sinaliza, RSI neutro (não oversold)
3. **CONSERVATIVE SELL**: RSI overbought com confirmação de volume

#### Performance Tracking
- **SMA Signals**: Contador de sinais da estratégia SMA
- **RSI Signals**: Contador de sinais da estratégia RSI+Volume
- **Combined Signals**: Contador de sinais onde ambas concordam

## 4. Estrutura de Arquivos

```
src/
├── strategies/
│   ├── base_strategy.py          # Classe base para estratégias
│   ├── simple_moving_average.py  # Estratégia SMA
│   ├── rsi_volume_strategy.py    # Estratégia RSI + Volume
│   └── trading_bot.py           # Bot principal com dual strategy
├── utils/
│   ├── indicators.py            # Indicadores RSI e Volume
│   ├── fee_manager.py          # Gerenciamento de taxas
│   └── binance_logger.py       # Sistema de logging
└── models/
    └── trade.py                # Modelos de dados
```

## 5. Configuração

### Parâmetros Padrão
```python
# SMA Strategy
short_period = 12
long_period = 15

# RSI + Volume Strategy
rsi_period = 14
volume_period = 20

# Trading
symbol = "BTCBRL"
trade_percentage = 5.0  # % do wallet por trade
max_daily_trades = 10
```

## 6. Execução

### Comando Principal
```bash
python3 main.py
```

### Saída em Tempo Real
```
🚀 Enhanced trading bot started! Using SMA + RSI + Volume strategies...
📊 Monitoring BTCBRL with dual strategy analysis...
💰 Wallet: BRL 1,913.48 | BTC 0.000130 (R$ 86.27) | Total: 1,999.75
📊 BTCBRL: 664,870.00
   📈 SMA: 662,884.92/662,385.93 | RSI: 64.5 | Vol: 0.0x
   🎯 Trades: 0/10
```

## 7. Benefícios da Implementação

### Redução de Falsos Sinais
- Confirmação dupla entre estratégias
- Filtros de volume para liquidez
- Condições RSI para evitar extremos

### Melhor Risk Management
- Sinais com diferentes níveis de confiança
- Volume confirmation para evitar baixa liquidez
- RSI filters para condições extremas

### Enhanced Monitoring
- Tracking separado por estratégia
- Métricas de performance detalhadas
- Logs aprimorados com insights de mercado

## 8. Limitações e Considerações

### Dependências
- Requer dados históricos suficientes para inicialização
- Depende da conectividade com Binance API
- Sensível a parâmetros de configuração

### Performance
- Processamento adicional para dual strategy
- Mais chamadas de API para dados de volume
- Logs mais detalhados podem impactar performance

## 9. Próximos Passos

### Melhorias Possíveis
1. **Dynamic Parameters**: Ajuste automático baseado em performance
2. **Weighted Signals**: Peso diferente para cada estratégia
3. **More Indicators**: Adição de MACD, Bollinger Bands, etc.
4. **Machine Learning**: Otimização baseada em dados históricos

### Monitoramento
- Acompanhar performance de cada estratégia individualmente
- Analisar taxa de sinais combinados vs. individuais
- Ajustar parâmetros baseado em resultados reais 