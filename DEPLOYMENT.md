# 🚀 Quantum-Safe Blockchain Guardrail - Deployment Guide

This guide covers multiple deployment options for the Quantum-Safe Blockchain Guardrail system.

## 📋 Prerequisites

Before deploying, ensure you have:
- **Node.js 16+** and npm
- **Python 3.8+** and pip3
- **Docker** and Docker Compose (for containerized deployment)
- **Git** for cloning the repository

## 🏠 **Option 1: Local Development (Recommended for Testing)**

### Quick Start
```bash
# Clone and setup
git clone <your-repo-url>
cd ethereum-test-drive
chmod +x setup.sh start.sh
./setup.sh
./start.sh
```

### Access
- **Dashboard**: http://localhost:3000
- **API**: http://localhost:5000
- **Ganache**: http://localhost:8545

### Requirements
- Local machine with Node.js, Python, Docker
- 4GB RAM minimum
- 10GB free disk space

---

## 🐳 **Option 2: Docker Deployment (Easiest)**

### Single Command Deployment
```bash
# Build and run everything
docker-compose up --build
```

### Manual Docker Build
```bash
# Build the image
docker build -t quantum-safe-guardrail .

# Run the container
docker run -p 3000:3000 -p 5000:5000 quantum-safe-guardrail
```

### Access
- **Dashboard**: http://localhost:3000
- **API**: http://localhost:5000

### Requirements
- Docker and Docker Compose
- 2GB RAM minimum
- 5GB free disk space

---

## ☁️ **Option 3: Cloud Deployment**

### AWS (Amazon Web Services)

#### Using ECS (Elastic Container Service)
```bash
# 1. Build and push to ECR
aws ecr create-repository --repository-name quantum-safe-guardrail
docker build -t quantum-safe-guardrail .
docker tag quantum-safe-guardrail:latest <account-id>.dkr.ecr.<region>.amazonaws.com/quantum-safe-guardrail:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/quantum-safe-guardrail:latest

# 2. Deploy using ECS
aws ecs create-cluster --cluster-name quantum-safe-guardrail-cluster
# Use deploy/aws-deploy.yml for task definition
```

#### Using EC2
```bash
# 1. Launch EC2 instance (Ubuntu 20.04, t3.medium)
# 2. Install Docker
sudo apt update && sudo apt install docker.io docker-compose -y

# 3. Clone and deploy
git clone <your-repo-url>
cd ethereum-test-drive
docker-compose up -d
```

### Azure

#### Using Container Instances
```bash
# 1. Build and push to Azure Container Registry
az acr create --resource-group myResourceGroup --name quantumSafeGuardrail
az acr build --registry quantumSafeGuardrail --image quantum-safe-guardrail .

# 2. Deploy using Azure CLI
az container create --resource-group myResourceGroup --name quantum-safe-guardrail --image quantumSafeGuardrail.azurecr.io/quantum-safe-guardrail:latest --ports 3000 5000 --dns-name-label quantum-safe-guardrail
```

### Google Cloud Platform

#### Using Cloud Run
```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT-ID/quantum-safe-guardrail

# 2. Deploy to Cloud Run
gcloud run deploy quantum-safe-guardrail --image gcr.io/PROJECT-ID/quantum-safe-guardrail --platform managed --region us-central1 --allow-unauthenticated
```

### DigitalOcean

#### Using Droplets
```bash
# 1. Create droplet
doctl compute droplet create quantum-safe-guardrail --size s-2vcpu-4gb --image docker-20-04 --region nyc3

# 2. Deploy using the script
chmod +x deploy/digitalocean-deploy.sh
./deploy/digitalocean-deploy.sh
```

---

## 🎯 **Option 4: Platform-Specific Deployment**

### Heroku

```bash
# 1. Install Heroku CLI
# 2. Login to Heroku
heroku login

# 3. Create apps
heroku create quantum-safe-guardrail
heroku create quantum-safe-guardrail-api

# 4. Deploy
git subtree push --prefix=. heroku main
git subtree push --prefix=backend heroku-api main
```

### Vercel (Frontend Only)

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy frontend
cd frontend
vercel --prod
```

### Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and deploy
railway login
railway init
railway up
```

---

## 🔧 **Option 5: Kubernetes Deployment**

### Prerequisites
- Kubernetes cluster (local or cloud)
- kubectl configured

### Deploy
```bash
# 1. Create secrets
kubectl create secret generic guardrail-secrets \
  --from-literal=rpc-url="https://your-ethereum-node.com" \
  --from-literal=ws-url="wss://your-ethereum-node.com"

# 2. Deploy application
kubectl apply -f deploy/kubernetes-deploy.yml

# 3. Check status
kubectl get pods
kubectl get services
```

---

## 🌐 **Option 6: VPS/Server Deployment**

### Ubuntu/Debian Server
```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install nodejs npm python3 python3-pip docker.io docker-compose git -y

# 3. Clone and setup
git clone <your-repo-url>
cd ethereum-test-drive
chmod +x setup.sh
./setup.sh

# 4. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 5. Start services
./start.sh

# 6. Setup reverse proxy (optional)
sudo apt install nginx -y
# Configure nginx for your domain
```

---

## 🔐 **Environment Configuration**

### Required Environment Variables
```env
NODE_ENV=production
PORT=3000
BACKEND_PORT=5000
RPC_URL=https://your-ethereum-node.com
WS_URL=wss://your-ethereum-node.com
LOG_LEVEL=info
```

### Optional Environment Variables
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/guardrail
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-jwt-secret
ENCRYPTION_KEY=your-encryption-key
```

---

## 📊 **Monitoring and Maintenance**

### Health Checks
- **Application**: `GET /api/health`
- **Backend API**: `GET /api/health`
- **Database**: Check connection status

### Logs
```bash
# Docker logs
docker-compose logs -f

# Kubernetes logs
kubectl logs -f deployment/quantum-safe-guardrail

# System logs
journalctl -u quantum-safe-guardrail -f
```

### Backup
```bash
# Backup data directory
tar -czf guardrail-backup-$(date +%Y%m%d).tar.gz data/

# Backup database (if using external DB)
pg_dump $DATABASE_URL > guardrail-db-backup.sql
```

---

## 🚨 **Troubleshooting**

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :3000
   # Kill process using port
   sudo kill -9 $(lsof -t -i:3000)
   ```

2. **Docker Issues**
   ```bash
   # Clean up Docker
   docker system prune -a
   # Rebuild containers
   docker-compose down && docker-compose up --build
   ```

3. **Python Dependencies**
   ```bash
   # Reinstall Python dependencies
   cd backend
   pip3 install -r requirements.txt --force-reinstall
   ```

4. **Node.js Issues**
   ```bash
   # Clear npm cache
   npm cache clean --force
   # Reinstall dependencies
   rm -rf node_modules package-lock.json
   npm install
   ```

### Performance Optimization

1. **Resource Limits**
   - Minimum: 2GB RAM, 1 CPU core
   - Recommended: 4GB RAM, 2 CPU cores
   - Production: 8GB RAM, 4 CPU cores

2. **Database Optimization**
   - Use connection pooling
   - Enable query caching
   - Regular maintenance

3. **Caching**
   - Enable Redis for session storage
   - Use CDN for static assets
   - Implement application-level caching

---

## 📞 **Support**

For deployment issues:
1. Check the logs first
2. Verify environment variables
3. Ensure all dependencies are installed
4. Check firewall and network settings
5. Create an issue with detailed error information

---

## 🎯 **Recommended Deployment Strategy**

### For Development/Testing
- **Local Docker**: `docker-compose up --build`
- **Quick and easy setup**
- **Full feature testing**

### For Production
- **AWS ECS** or **Google Cloud Run**
- **Kubernetes** for complex setups
- **Load balancer** for high availability
- **Monitoring** and **logging** setup

### For Demo/Presentation
- **Heroku** or **Railway**
- **Quick deployment**
- **Public access**

Choose the deployment option that best fits your needs, budget, and technical requirements!
