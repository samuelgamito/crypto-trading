# 🧪 Validation Scripts

This folder contains test and validation scripts for the crypto trading bot.

## 📋 Available Tests

### `test_api_connection.py`
- **Purpose**: Test Binance API connection and basic functionality
- **Usage**: `python3 validation/test_api_connection.py`
- **What it tests**:
  - API key validation
  - Server connectivity
  - Account information retrieval
  - Balance checking

### `test_mongo_auth.py`
- **Purpose**: Test MongoDB connection with authentication
- **Usage**: `python3 validation/test_mongo_auth.py`
- **What it tests**:
  - MongoDB connection with/without authentication
  - Signal storage and retrieval
  - Configuration validation

### `test_sell_order.py`
- **Purpose**: Test sell order functionality
- **Usage**: `python3 validation/test_sell_order.py`
- **What it tests**:
  - Sell order placement
  - Quantity validation
  - Fee calculations
  - Order execution

### `test_buy_order.py`
- **Purpose**: Test basic order placement
- **Usage**: `python3 validation/test_buy_order.py`
- **What it tests**:
  - Simple buy order placement
  - Market data retrieval
  - Order confirmation
  - Balance updates

## 🚀 Running Tests

```bash
# Test API connection
python3 validation/test_api_connection.py

# Test MongoDB authentication
python3 validation/test_mongo_auth.py

# Test sell orders
python3 validation/test_sell_order.py

# Test simple orders
python3 validation/test_buy_order.py
```

## ⚠️ Important Notes

- **Production Mode**: Some tests execute real trades with real money
- **Environment**: Make sure your `.env` file is properly configured
- **Testnet**: Use `BINANCE_TESTNET=true` for safe testing
- **MongoDB**: Ensure MongoDB is running for authentication tests

## 🔧 Configuration

All tests use the same environment variables as the main application:
- `BINANCE_API_KEY` and `BINANCE_SECRET_KEY`
- `MONGO_CONNECTION_STRING`, `MONGO_USERNAME`, `MONGO_PASSWORD`
- Other trading configuration variables 