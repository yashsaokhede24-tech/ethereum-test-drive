# Heroku Deployment Guide

## Prerequisites
- Heroku CLI installed
- Git repository
- Heroku account

## Deployment Steps

### 1. Create Heroku Apps
```bash
# Create main application
heroku create quantum-safe-guardrail

# Create backend API (separate app)
heroku create quantum-safe-guardrail-api
```

### 2. Configure Environment Variables
```bash
# Main app environment variables
heroku config:set NODE_ENV=production -a quantum-safe-guardrail
heroku config:set RPC_URL=https://your-ethereum-node.com -a quantum-safe-guardrail
heroku config:set WS_URL=wss://your-ethereum-node.com -a quantum-safe-guardrail

# Backend API environment variables
heroku config:set FLASK_ENV=production -a quantum-safe-guardrail-api
heroku config:set PYTHONPATH=/app/backend -a quantum-safe-guardrail-api
```

### 3. Deploy Applications
```bash
# Deploy main app
git subtree push --prefix=. heroku main

# Deploy backend API
git subtree push --prefix=backend heroku-api main
```

### 4. Scale Applications
```bash
# Scale main app
heroku ps:scale web=1 -a quantum-safe-guardrail

# Scale backend API
heroku ps:scale web=1 -a quantum-safe-guardrail-api
```

## Access URLs
- Main Dashboard: https://quantum-safe-guardrail.herokuapp.com
- Backend API: https://quantum-safe-guardrail-api.herokuapp.com
