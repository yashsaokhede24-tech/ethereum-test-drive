# Quantum-Safe Blockchain Guardrail

A comprehensive system that intercepts blockchain transactions and upgrades them with post-quantum cryptography (PQC) signatures, ensuring quantum-safe security for blockchain operations.

## 🚀 Features

- **Transaction Interception**: Real-time monitoring of blockchain transactions via JSON-RPC and WebSocket
- **Post-Quantum Cryptography**: Integration with liboqs for quantum-safe signature algorithms (CRYSTALS-Dilithium, Falcon)
- **AI-Powered Anomaly Detection**: Machine learning-based detection of suspicious transaction patterns
- **Real-time Dashboard**: React-based UI for monitoring and managing the system
- **Multi-Algorithm Support**: Support for multiple PQC signature schemes
- **Blockchain Testnet Integration**: Works with Ethereum testnets (Goerli, Sepolia) and local development (Ganache)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Blockchain    │───▶│  Transaction     │───▶│  PQC Signature  │
│   (Ethereum)    │    │  Interceptor     │    │  Engine         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Anomaly         │    │  Enhanced       │
                       │  Detector        │    │  Transaction    │
                       │  (ML/AI)         │    │  (Quantum-Safe) │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────────────────────────────┐
                       │           React Dashboard              │
                       │     (Real-time Monitoring & Control)   │
                       └─────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern UI framework
- **Ant Design** - Component library
- **Socket.io** - Real-time communication
- **Recharts** - Data visualization

### Backend
- **Node.js** - Main application server
- **Express.js** - Web framework
- **WebSocket** - Real-time transaction monitoring
- **ethers.js** - Blockchain interaction

### Python Services
- **Flask** - API server for PQC operations
- **liboqs-python** - Post-quantum cryptography library
- **scikit-learn** - Machine learning for anomaly detection
- **pandas/numpy** - Data processing

### Blockchain
- **Ethereum** - Target blockchain
- **Ganache** - Local development blockchain
- **JSON-RPC** - Blockchain communication protocol

## 📋 Prerequisites

- **Node.js** 16+ and npm
- **Python** 3.8+ and pip3
- **Git** for cloning the repository

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ethereum-test-drive
chmod +x setup.sh
./setup.sh
```

### 2. Start All Services

```bash
./start.sh
```

This will start:
- Ganache local blockchain (port 8545)
- Python backend API (port 5000)
- React frontend (port 3000)
- Main Node.js application (port 3000)

### 3. Access the Dashboard

Open your browser and navigate to:
- **Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Ganache**: http://localhost:8545

## 🔧 Manual Setup

If you prefer to set up manually:

### 1. Install Dependencies

```bash
# Node.js dependencies
npm install

# Frontend dependencies
cd frontend && npm install && cd ..

# Python dependencies
cd backend && pip3 install -r requirements.txt && cd ..
```

### 2. Start Ganache

```bash
npx ganache-cli --host 0.0.0.0 --port 8545 --ws --wsHost 0.0.0.0 --wsPort 8546
```

### 3. Start Backend

```bash
cd backend
python3 app.py
```

### 4. Start Frontend

```bash
cd frontend
npm start
```

### 5. Start Main Application

```bash
npm start
```

## 🔐 Post-Quantum Cryptography

The system supports multiple quantum-safe signature algorithms:

- **CRYSTALS-Dilithium2** (Default) - Fast and secure
- **CRYSTALS-Dilithium3** - Higher security level
- **CRYSTALS-Dilithium5** - Highest security level
- **Falcon-512** - Compact signatures
- **Falcon-1024** - Higher security Falcon variant

### Algorithm Selection

You can change the default algorithm in `backend/pqc_signature_engine.py`:

```python
engine = PQCSignatureEngine('dilithium3')  # Change to preferred algorithm
```

## 🤖 Anomaly Detection

The system uses machine learning to detect suspicious transaction patterns:

### Features Analyzed
- Transaction value and gas parameters
- Address entropy and similarity
- Data complexity and size
- Time-based patterns
- Gas efficiency metrics

### Training Data
The anomaly detector is pre-trained with sample data but can be retrained with real transaction data:

```bash
curl -X POST http://localhost:5000/api/retrain-model
```

## 📊 API Endpoints

### Main Application (Port 3000)
- `GET /api/health` - Health check
- `GET /api/stats` - System statistics
- `GET /api/transactions/pending` - Pending transactions
- `POST /api/transactions/:txHash/upgrade` - Upgrade transaction

### Backend API (Port 5000)
- `POST /api/upgrade-transaction` - Add PQC signature
- `POST /api/detect-anomaly` - Analyze transaction
- `POST /api/process-transaction` - Full processing pipeline
- `GET /api/algorithms` - Supported PQC algorithms
- `GET /api/feature-importance` - ML model features

## 🔍 Monitoring

The dashboard provides real-time monitoring of:

- **Transaction Flow**: Live view of captured and processed transactions
- **Quantum-Safe Upgrades**: Count of transactions upgraded with PQC signatures
- **Anomaly Detection**: Suspicious transactions flagged by ML algorithms
- **System Health**: Uptime, connection status, and performance metrics

## 🧪 Testing

### Test with Sample Transactions

1. Start the system
2. Send a test transaction to the Ganache network
3. Watch it appear in the dashboard
4. Verify it gets upgraded with quantum-safe signatures

### Example Test Transaction

```javascript
// Using ethers.js
const provider = new ethers.JsonRpcProvider('http://localhost:8545');
const wallet = new ethers.Wallet('0x...', provider);
const tx = await wallet.sendTransaction({
  to: '0x...',
  value: ethers.parseEther('1.0')
});
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
NODE_ENV=development
PORT=3000
BACKEND_PORT=5000
RPC_URL=http://localhost:8545
WS_URL=ws://localhost:8546
LOG_LEVEL=info
```

### Blockchain Configuration

To use a different blockchain network, update the RPC URLs:

```env
# For Goerli testnet
RPC_URL=https://goerli.infura.io/v3/YOUR_PROJECT_ID
WS_URL=wss://goerli.infura.io/ws/v3/YOUR_PROJECT_ID

# For Sepolia testnet
RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
WS_URL=wss://sepolia.infura.io/ws/v3/YOUR_PROJECT_ID
```

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000, 5000, and 8545 are available
2. **Python dependencies**: Make sure liboqs is properly installed
3. **Node.js version**: Use Node.js 16 or higher
4. **WebSocket connection**: Check firewall settings for WebSocket connections

### Logs

Check the console output for detailed error messages. Logs are also written to:
- `logs/guardrail.log` - Main application logs
- Console output for each service

### Reset Everything

```bash
# Stop all processes
pkill -f "node\|python\|ganache"

# Clean install
rm -rf node_modules frontend/node_modules
npm install
cd frontend && npm install && cd ..
cd backend && pip3 install -r requirements.txt && cd ..

# Restart
./start.sh
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **liboqs** - Post-quantum cryptography library
- **ethers.js** - Ethereum JavaScript library
- **Ant Design** - React component library
- **scikit-learn** - Machine learning library

## 📞 Support

For questions, issues, or contributions, please:
1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information

---

**⚠️ Security Notice**: This is a demonstration system. For production use, ensure proper security audits and key management practices.