#!/bin/bash

# Quantum-Safe Blockchain Guardrail Setup Script
# This script sets up the development environment

echo "🚀 Setting up Quantum-Safe Blockchain Guardrail..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip3 install -r requirements.txt
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/models
mkdir -p logs
mkdir -p data

# Set up environment variables
echo "⚙️ Setting up environment variables..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Quantum-Safe Blockchain Guardrail Configuration
NODE_ENV=development
PORT=3000
BACKEND_PORT=5000
RPC_URL=http://localhost:8545
WS_URL=ws://localhost:8546

# Database configuration (if needed)
DATABASE_URL=sqlite:///data/guardrail.db

# Logging
LOG_LEVEL=info
LOG_FILE=logs/guardrail.log
EOF
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

# Create a simple Ganache setup script
echo "🔧 Creating Ganache setup script..."
cat > start-ganache.sh << 'EOF'
#!/bin/bash
echo "Starting Ganache local blockchain..."
npx ganache-cli \
  --host 0.0.0.0 \
  --port 8545 \
  --ws \
  --wsHost 0.0.0.0 \
  --wsPort 8546 \
  --accounts 10 \
  --defaultBalanceEther 100 \
  --gasLimit 0x1fffffffffffff \
  --gasPrice 0x01 \
  --unlock 0,1,2,3,4,5,6,7,8,9
EOF

chmod +x start-ganache.sh

# Create start script
echo "🔧 Creating start script..."
cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Quantum-Safe Blockchain Guardrail..."

# Start Ganache in background
echo "Starting local blockchain..."
./start-ganache.sh &
GANACHE_PID=$!

# Wait for Ganache to start
sleep 5

# Start backend
echo "Starting Python backend..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Start main application
echo "Starting main application..."
npm start &
MAIN_PID=$!

echo "🎉 All services started!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo "⛓️  Ganache: http://localhost:8545"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping all services..."
    kill $GANACHE_PID $BACKEND_PID $FRONTEND_PID $MAIN_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for any process to exit
wait
EOF

chmod +x start.sh

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Run './start.sh' to start all services"
echo "2. Open http://localhost:3000 in your browser"
echo "3. The system will automatically detect and upgrade transactions"
echo ""
echo "📚 For more information, see README.md"
