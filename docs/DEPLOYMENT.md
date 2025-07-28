# 🚀 Deployment Guide

This guide covers all deployment options for the Crypto Trading Bot, from local development to production Kubernetes clusters.

## 📋 Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [GitHub Actions CI/CD](#github-actions-cicd)
5. [Monitoring & Logging](#monitoring--logging)
6. [Troubleshooting](#troubleshooting)

## 🏠 Local Development

### Prerequisites
- Python 3.11+
- pip
- Git

### Setup
```bash
# Clone repository
git clone <your-repo-url>
cd crypto-trading

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your API keys

# Run locally
python main.py
```

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t crypto-trading-bot .

# Run container
docker run -d \
  --name crypto-trading-bot \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  crypto-trading-bot
```

### Using the Deployment Script

```bash
# Make script executable
chmod +x deploy.sh

# Deploy to production
./deploy.sh production deploy

# Show logs
./deploy.sh production logs

# Update to latest version
./deploy.sh production update

# Stop services
./deploy.sh production stop
```

## ☸️ Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (1.20+)
- kubectl configured
- Docker registry access

### Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f kubernetes/namespace.yaml

# Create ConfigMap
kubectl apply -f kubernetes/configmap.yaml

# Create secrets (replace with your values)
kubectl create secret generic crypto-trading-secrets \
  --from-literal=binance-api-key=your-api-key \
  --from-literal=binance-secret-key=your-secret-key \
  -n crypto-trading

# Deploy application
kubectl apply -f kubernetes/deployment.yaml

# Check status
kubectl get pods -n crypto-trading
kubectl logs -f deployment/crypto-trading-bot -n crypto-trading
```

### Scaling and Updates

```bash
# Scale to multiple replicas
kubectl scale deployment crypto-trading-bot --replicas=3 -n crypto-trading

# Update image
kubectl set image deployment/crypto-trading-bot \
  crypto-trading-bot=ghcr.io/your-username/crypto-trading:latest \
  -n crypto-trading

# Rollback if needed
kubectl rollout undo deployment/crypto-trading-bot -n crypto-trading
```

## 🔄 GitHub Actions CI/CD

### Pipeline Overview

The CI/CD pipeline includes:

1. **Testing**: Lint, unit tests, security scans
2. **Building**: Multi-platform Docker images
3. **Publishing**: Push to GitHub Container Registry
4. **Deployment**: Auto-deploy on releases

### Triggering Deployments

#### Automatic (on push to main)
```bash
git push origin main
```

#### Manual (on release)
```bash
# Create a new release on GitHub
# This will trigger production deployment
```

#### Manual backtesting
```bash
# Go to Actions tab in GitHub
# Run "Automated Backtesting" workflow
# Configure parameters as needed
```

### Environment Variables

Set these in your GitHub repository settings:

#### Secrets (Settings > Secrets and variables > Actions)
- `BINANCE_API_KEY`: Your Binance API key
- `BINANCE_SECRET_KEY`: Your Binance secret key
- `DOCKER_REGISTRY_TOKEN`: GitHub token for container registry

#### Variables (Settings > Secrets and variables > Actions)
- `DEFAULT_SYMBOL`: BTCUSDT
- `TRADE_PERCENTAGE`: 5.0
- `MAX_DAILY_TRADES`: 10

## 📊 Monitoring & Logging

### Log Management

```bash
# View real-time logs
docker-compose logs -f crypto-trading-bot

# View logs in Kubernetes
kubectl logs -f deployment/crypto-trading-bot -n crypto-trading

# Download logs
docker cp crypto-trading-bot:/app/logs ./backup-logs
```

### Health Checks

The application includes health checks:

```bash
# Docker health check
docker inspect crypto-trading-bot | grep Health -A 10

# Kubernetes health check
kubectl describe pod -l app=crypto-trading-bot -n crypto-trading
```

### Monitoring with Grafana

```bash
# Start monitoring stack
docker-compose up -d monitoring

# Access Grafana
# URL: http://localhost:3000
# Username: admin
# Password: admin
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BINANCE_API_KEY` | Binance API key | - | Yes |
| `BINANCE_SECRET_KEY` | Binance secret key | - | Yes |
| `BINANCE_TESTNET` | Use testnet | true | No |
| `DEFAULT_SYMBOL` | Trading symbol | BTCUSDT | No |
| `TRADE_PERCENTAGE` | Trade size % | 5.0 | No |
| `MAX_DAILY_TRADES` | Daily trade limit | 10 | No |
| `STOP_LOSS_PERCENTAGE` | Stop loss % | 2.0 | No |
| `TAKE_PROFIT_PERCENTAGE` | Take profit % | 5.0 | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `LOG_FILE` | Log file path | logs/trading_bot.log | No |

### Configuration Examples

#### Production (.env)
```bash
BINANCE_API_KEY=your-production-api-key
BINANCE_SECRET_KEY=your-production-secret-key
BINANCE_TESTNET=false
DEFAULT_SYMBOL=BTCUSDT
TRADE_PERCENTAGE=5.0
MAX_DAILY_TRADES=10
STOP_LOSS_PERCENTAGE=2.0
TAKE_PROFIT_PERCENTAGE=5.0
LOG_LEVEL=INFO
```

#### Staging (.env)
```bash
BINANCE_API_KEY=your-staging-api-key
BINANCE_SECRET_KEY=your-staging-secret-key
BINANCE_TESTNET=true
DEFAULT_SYMBOL=BTCUSDT
TRADE_PERCENTAGE=2.0
MAX_DAILY_TRADES=5
LOG_LEVEL=DEBUG
```

## 🚨 Troubleshooting

### Common Issues

#### Container won't start
```bash
# Check logs
docker-compose logs crypto-trading-bot

# Check environment variables
docker-compose config

# Verify .env file
cat .env
```

#### API connection issues
```bash
# Test API connection
python -c "
from src.config.config import Config
from src.api.binance_client import BinanceClient
config = Config()
client = BinanceClient(config)
print('API connection test:', client.get_account_info())
"
```

#### Kubernetes pod issues
```bash
# Check pod status
kubectl get pods -n crypto-trading

# Check pod events
kubectl describe pod <pod-name> -n crypto-trading

# Check logs
kubectl logs <pod-name> -n crypto-trading
```

#### Performance issues
```bash
# Check resource usage
docker stats crypto-trading-bot

# Check Kubernetes resource usage
kubectl top pods -n crypto-trading
```

### Debug Commands

```bash
# Enter running container
docker exec -it crypto-trading-bot bash

# Check configuration
docker exec crypto-trading-bot python -c "
from src.config.config import Config
config = Config()
print('Config loaded successfully')
"

# Test strategy
docker exec crypto-trading-bot python backtest.py --days 1
```

### Emergency Procedures

#### Stop all trading
```bash
# Docker
docker-compose down

# Kubernetes
kubectl scale deployment crypto-trading-bot --replicas=0 -n crypto-trading

# Local
pkill -f "python main.py"
```

#### Rollback deployment
```bash
# Docker
docker-compose down
git checkout HEAD~1
docker-compose up -d

# Kubernetes
kubectl rollout undo deployment/crypto-trading-bot -n crypto-trading
```

## 📈 Performance Optimization

### Resource Recommendations

#### Docker
- **CPU**: 0.5 cores minimum, 1 core recommended
- **Memory**: 512MB minimum, 1GB recommended
- **Storage**: 1GB for logs

#### Kubernetes
- **CPU Request**: 250m, Limit: 500m
- **Memory Request**: 256Mi, Limit: 512Mi
- **Storage**: 1Gi persistent volume

### Scaling Strategies

#### Horizontal Scaling
```bash
# Scale to multiple instances
kubectl scale deployment crypto-trading-bot --replicas=3 -n crypto-trading
```

#### Vertical Scaling
```bash
# Increase resource limits
kubectl patch deployment crypto-trading-bot \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"crypto-trading-bot","resources":{"limits":{"cpu":"1000m","memory":"1Gi"}}}]}}}}' \
  -n crypto-trading
```

## 🔐 Security Considerations

### API Key Management
- Use environment variables or secrets
- Rotate keys regularly
- Use testnet for development
- Limit API key permissions

### Network Security
- Use private networks in production
- Implement proper firewall rules
- Use HTTPS for all external communications

### Container Security
- Run as non-root user
- Use minimal base images
- Regular security updates
- Scan for vulnerabilities

---

## 📞 Support

For deployment issues:
1. Check the troubleshooting section
2. Review logs and error messages
3. Verify configuration settings
4. Test with minimal configuration
5. Check GitHub Issues for known problems

---

**🚀 Ready to deploy? Start with the [Quick Start](#quick-start-with-docker-compose) section!** 