# Trading Bot Decision Logic

## Overview
Your crypto trading bot uses a **Simple Moving Average (SMA) Crossover Strategy** with **risk management rules** to make trading decisions.

## Strategy Parameters
- **Short SMA Period**: 12 (faster moving average)
- **Long SMA Period**: 15 (slower moving average)
- **Trade Percentage**: 5.0% of total wallet balance per trade
- **Max Daily Trades**: 10
- **Stop Loss**: 2.0% loss
- **Take Profit**: 5.0% gain

## Decision-Making Process

### 1. BUY Decision (Golden Cross) 🟢
**When to BUY:**
- **Short SMA (12-period) crosses ABOVE Long SMA (15-period)**
- **Previous**: Short SMA ≤ Long SMA
- **Current**: Short SMA > Long SMA

**Example:**
```
Previous: Short SMA = $118,000, Long SMA = $118,100
Current:  Short SMA = $118,200, Long SMA = $118,100
Result:   GOLDEN CROSS → BUY SIGNAL
```

**How much to buy:**
- **Percentage-based**: 5% of total wallet balance
- **Dynamic calculation**: Adapts to current portfolio value
- **Minimum trade**: $10 USD
- **Maximum**: Respects daily trade limits and USDT balance

### 2. SELL Decision (Death Cross) 🔴
**When to SELL:**
- **Short SMA (12-period) crosses BELOW Long SMA (15-period)**
- **Previous**: Short SMA ≥ Long SMA  
- **Current**: Short SMA < Long SMA

**Example:**
```
Previous: Short SMA = $118,200, Long SMA = $118,100
Current:  Short SMA = $118,000, Long SMA = $118,100
Result:   DEATH CROSS → SELL SIGNAL
```

### 3. HOLD Decision (No Signal) ⏸️
**When to HOLD:**
- **No crossover detected**
- **Short SMA and Long SMA are moving in the same direction**
- **Waiting for next signal**

### 4. Risk Management Rules 🛡️

#### Stop Loss (Emergency Sell)
- **Trigger**: Price drops 2.0% below entry price
- **Action**: Sell immediately to limit losses
- **Example**: Buy at $118,000 → Sell at $115,640 (-2%)

#### Take Profit (Secure Gains)
- **Trigger**: Price rises 5.0% above entry price
- **Action**: Sell to secure profits
- **Example**: Buy at $118,000 → Sell at $123,900 (+5%)

#### Daily Limits
- **Maximum trades per day**: 10
- **Prevents overtrading**
- **Resets at midnight**

## Real-Time Decision Flow

### Every 30 seconds, the bot:

1. **📊 Gets current BTC price** from Binance
2. **📈 Calculates SMAs**:
   - Short SMA (12-period average)
   - Long SMA (15-period average)
3. **🔍 Checks for signals**:
   - Golden Cross → BUY
   - Death Cross → SELL
   - Stop Loss → SELL
   - Take Profit → SELL
4. **💰 Calculates position size** (0.001 BTC)
5. **📝 Logs decision** and executes trade

## Example Scenario

```
Time: 18:30:00
Price: $118,000
Short SMA: $117,950
Long SMA: $118,100
Decision: HOLD (Short SMA < Long SMA)

Time: 18:30:30  
Price: $118,200
Short SMA: $118,150
Long SMA: $118,100
Decision: BUY (Golden Cross detected!)

Time: 18:31:00
Price: $118,500
Short SMA: $118,450
Long SMA: $118,100
Decision: HOLD (Both SMAs rising)

Time: 18:31:30
Price: $123,900
Short SMA: $123,850
Long SMA: $118,100
Decision: SELL (Take Profit triggered! +5%)
```

## Position Management

### Buy Signal Execution:
1. **Check if already have position** → Skip if yes
2. **Calculate quantity**: 5% of total wallet balance
3. **Validate USDT balance** → Ensure sufficient funds
4. **Execute market buy order**
5. **Record trade** and entry price
6. **Start monitoring** for sell signals

### Sell Signal Execution:
1. **Check if have position** → Skip if no
2. **Execute market sell order**
3. **Calculate P&L**: (Sell Price - Buy Price) × Quantity
4. **Update performance metrics**
5. **Reset** for next buy signal

## Safety Features

✅ **Testnet Mode**: No real money at risk  
✅ **Daily Trade Limits**: Max 10 trades per day  
✅ **Stop Loss**: Automatic loss protection  
✅ **Take Profit**: Secure gains automatically  
✅ **Position Size Limits**: Small, controlled trades  
✅ **Error Handling**: Graceful failure recovery  

## Current Bot Status

Your bot is currently:
- **Monitoring**: BTCUSDT every 30 seconds
- **Strategy**: SMA 12/15 Crossover
- **Risk Management**: 2% Stop Loss, 5% Take Profit
- **Trade Size**: 5% of total wallet balance per trade
- **Portfolio**: $120,387 total value
- **Dynamic Sizing**: Trade amount adapts to portfolio value 