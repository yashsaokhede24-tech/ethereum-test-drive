#!/bin/bash

# DigitalOcean Droplet Deployment Script for Quantum-Safe Blockchain Guardrail

echo "🚀 Deploying Quantum-Safe Blockchain Guardrail to DigitalOcean..."

# Configuration
DROPLET_NAME="quantum-safe-guardrail"
DROPLET_SIZE="s-2vcpu-4gb"
DROPLET_REGION="nyc3"
DROPLET_IMAGE="docker-20-04"

# Create droplet
echo "📦 Creating DigitalOcean droplet..."
doctl compute droplet create $DROPLET_NAME \
  --size $DROPLET_SIZE \
  --image $DROPLET_IMAGE \
  --region $DROPLET_REGION \
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header | head -1)

# Wait for droplet to be ready
echo "⏳ Waiting for droplet to be ready..."
sleep 60

# Get droplet IP
DROPLET_IP=$(doctl compute droplet list --format PublicIPv4 --no-header --filter name=$DROPLET_NAME)

echo "🌐 Droplet created with IP: $DROPLET_IP"

# Setup deployment script
cat > deploy-to-droplet.sh << 'EOF'
#!/bin/bash

# Update system
apt-get update
apt-get upgrade -y

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/your-username/ethereum-test-drive.git
cd ethereum-test-drive

# Create environment file
cat > .env << 'ENVEOF'
NODE_ENV=production
PORT=3000
BACKEND_PORT=5000
RPC_URL=https://your-ethereum-node.com
WS_URL=wss://your-ethereum-node.com
ENVEOF

# Start services
docker-compose up -d

# Setup firewall
ufw allow 3000
ufw allow 5000
ufw allow 22
ufw --force enable

echo "✅ Deployment complete!"
echo "📊 Dashboard: http://$DROPLET_IP:3000"
echo "🔧 API: http://$DROPLET_IP:5000"
EOF

# Copy deployment script to droplet
scp deploy-to-droplet.sh root@$DROPLET_IP:/root/
ssh root@$DROPLET_IP "chmod +x deploy-to-droplet.sh && ./deploy-to-droplet.sh"

echo "🎉 Deployment completed!"
echo "📊 Access your application at: http://$DROPLET_IP:3000"
