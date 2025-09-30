const express = require('express');
const cors = require('cors');
const { WebSocketServer } = require('ws');
const http = require('http');
const TransactionInterceptor = require('./transaction-interceptor');
const { spawn } = require('child_process');
const path = require('path');

/**
 * Quantum-Safe Blockchain Guardrail Main Application
 * Orchestrates transaction interception, PQC signature upgrades, and anomaly detection
 */

class QuantumSafeGuardrail {
    constructor(config = {}) {
        this.config = {
            port: config.port || 3000,
            backendPort: config.backendPort || 5000,
            rpcUrl: config.rpcUrl || 'http://localhost:8545',
            wsUrl: config.wsUrl || 'ws://localhost:8546',
            ...config
        };
        
        this.app = express();
        this.server = http.createServer(this.app);
        this.wss = new WebSocketServer({ server: this.server });
        this.transactionInterceptor = null;
        this.backendProcess = null;
        this.connectedClients = new Set();
        this.transactionQueue = [];
        this.stats = {
            totalTransactions: 0,
            quantumSafeUpgrades: 0,
            anomaliesDetected: 0,
            startTime: Date.now()
        };
        
        this.setupMiddleware();
        this.setupRoutes();
        this.setupWebSocket();
    }

    setupMiddleware() {
        this.app.use(cors());
        this.app.use(express.json());
        this.app.use(express.static(path.join(__dirname, '../frontend/build')));
    }

    setupRoutes() {
        // Health check
        this.app.get('/api/health', (req, res) => {
            res.json({
                status: 'healthy',
                uptime: Date.now() - this.stats.startTime,
                ...this.stats
            });
        });

        // Get current statistics
        this.app.get('/api/stats', (req, res) => {
            res.json(this.stats);
        });

        // Get pending transactions
        this.app.get('/api/transactions/pending', (req, res) => {
            if (this.transactionInterceptor) {
                res.json(this.transactionInterceptor.getPendingTransactions());
            } else {
                res.json([]);
            }
        });

        // Get transaction queue
        this.app.get('/api/transactions/queue', (req, res) => {
            res.json(this.transactionQueue);
        });

        // Process transaction upgrade
        this.app.post('/api/transactions/:txHash/upgrade', async (req, res) => {
            try {
                const { txHash } = req.params;
                const result = await this.upgradeTransaction(txHash);
                res.json(result);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Get anomaly detection results
        this.app.get('/api/anomalies', (req, res) => {
            // This would typically fetch from the backend
            res.json({ anomalies: [], total: 0 });
        });

        // Serve React app
        this.app.get('*', (req, res) => {
            res.sendFile(path.join(__dirname, '../frontend/build/index.html'));
        });
    }

    setupWebSocket() {
        this.wss.on('connection', (ws) => {
            console.log('Client connected to WebSocket');
            this.connectedClients.add(ws);

            // Send current stats to new client
            ws.send(JSON.stringify({
                type: 'stats',
                data: this.stats
            }));

            ws.on('close', () => {
                console.log('Client disconnected from WebSocket');
                this.connectedClients.delete(ws);
            });

            ws.on('error', (error) => {
                console.error('WebSocket error:', error);
                this.connectedClients.delete(ws);
            });
        });
    }

    async startBackend() {
        return new Promise((resolve, reject) => {
            console.log('Starting Python backend...');
            
            const backendPath = path.join(__dirname, '../backend');
            this.backendProcess = spawn('python', ['app.py'], {
                cwd: backendPath,
                stdio: ['pipe', 'pipe', 'pipe']
            });

            this.backendProcess.stdout.on('data', (data) => {
                console.log(`Backend: ${data}`);
            });

            this.backendProcess.stderr.on('data', (data) => {
                console.error(`Backend error: ${data}`);
            });

            this.backendProcess.on('close', (code) => {
                console.log(`Backend process exited with code ${code}`);
            });

            // Wait a moment for backend to start
            setTimeout(() => {
                resolve();
            }, 2000);
        });
    }

    async initialize() {
        try {
            console.log('Initializing Quantum-Safe Blockchain Guardrail...');

            // Start backend process
            await this.startBackend();

            // Initialize transaction interceptor
            this.transactionInterceptor = new TransactionInterceptor({
                rpcUrl: this.config.rpcUrl,
                wsUrl: this.config.wsUrl
            });

            // Set up event listeners
            this.setupTransactionInterceptorEvents();

            // Initialize the interceptor
            const initialized = await this.transactionInterceptor.initialize();
            if (!initialized) {
                throw new Error('Failed to initialize transaction interceptor');
            }

            console.log('Quantum-Safe Blockchain Guardrail initialized successfully');
            return true;

        } catch (error) {
            console.error('Failed to initialize:', error);
            return false;
        }
    }

    setupTransactionInterceptorEvents() {
        if (!this.transactionInterceptor) return;

        // Handle captured transactions
        this.transactionInterceptor.on('transactionCaptured', (data) => {
            console.log(`Transaction captured: ${data.transaction.hash}`);
            this.stats.totalTransactions++;
            
            // Add to processing queue
            this.transactionQueue.push({
                ...data.transaction,
                capturedAt: Date.now(),
                status: 'pending_upgrade'
            });

            // Broadcast to connected clients
            this.broadcastToClients({
                type: 'transaction_captured',
                data: data.transaction
            });

            // Process transaction for quantum-safe upgrade
            this.processTransaction(data.transaction);
        });

        // Handle confirmed transactions
        this.transactionInterceptor.on('transactionConfirmed', (data) => {
            console.log(`Transaction confirmed: ${data.transaction.hash}`);
            
            // Update queue
            const queueItem = this.transactionQueue.find(
                item => item.hash === data.transaction.hash
            );
            if (queueItem) {
                queueItem.status = 'confirmed';
                queueItem.confirmedAt = Date.now();
            }

            this.broadcastToClients({
                type: 'transaction_confirmed',
                data: data.transaction
            });
        });

        // Handle errors
        this.transactionInterceptor.on('error', (error) => {
            console.error('Transaction interceptor error:', error);
        });
    }

    async processTransaction(transaction) {
        try {
            console.log(`Processing transaction ${transaction.hash} for quantum-safe upgrade...`);
            
            // Send to backend for PQC signature upgrade
            const upgradeResult = await this.upgradeTransaction(transaction.hash);
            
            if (upgradeResult.success) {
                this.stats.quantumSafeUpgrades++;
                console.log(`Transaction ${transaction.hash} upgraded with quantum-safe signature`);
                
                this.broadcastToClients({
                    type: 'transaction_upgraded',
                    data: {
                        originalTx: transaction,
                        upgradedTx: upgradeResult.transaction
                    }
                });
            } else {
                console.error(`Failed to upgrade transaction ${transaction.hash}:`, upgradeResult.error);
            }

        } catch (error) {
            console.error(`Error processing transaction ${transaction.hash}:`, error);
        }
    }

    async upgradeTransaction(txHash) {
        try {
            // This would typically make an HTTP request to the Python backend
            // For now, we'll simulate the upgrade process
            const transaction = this.transactionQueue.find(item => item.hash === txHash);
            if (!transaction) {
                throw new Error('Transaction not found');
            }

            // Simulate PQC signature upgrade
            const upgradedTransaction = {
                ...transaction,
                quantumSafe: true,
                pqcSignature: {
                    algorithm: 'dilithium2',
                    signature: 'simulated_pqc_signature_' + Date.now(),
                    publicKey: 'simulated_pqc_public_key_' + Date.now(),
                    timestamp: Date.now()
                },
                upgradedAt: Date.now()
            };

            return {
                success: true,
                transaction: upgradedTransaction
            };

        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    broadcastToClients(message) {
        const messageStr = JSON.stringify(message);
        this.connectedClients.forEach(client => {
            if (client.readyState === client.OPEN) {
                client.send(messageStr);
            }
        });
    }

    start() {
        this.server.listen(this.config.port, () => {
            console.log(`Quantum-Safe Blockchain Guardrail running on port ${this.config.port}`);
            console.log(`WebSocket server running on port ${this.config.port}`);
            console.log(`Backend API running on port ${this.config.backendPort}`);
        });
    }

    async startListening() {
        if (this.transactionInterceptor) {
            this.transactionInterceptor.startListening();
            console.log('Started listening for blockchain transactions');
        }
    }

    async stop() {
        console.log('Shutting down Quantum-Safe Blockchain Guardrail...');
        
        if (this.transactionInterceptor) {
            await this.transactionInterceptor.cleanup();
        }

        if (this.backendProcess) {
            this.backendProcess.kill();
        }

        this.server.close();
        console.log('Shutdown complete');
    }
}

// Start the application
async function main() {
    const guardrail = new QuantumSafeGuardrail({
        port: process.env.PORT || 3000,
        backendPort: process.env.BACKEND_PORT || 5000,
        rpcUrl: process.env.RPC_URL || 'http://localhost:8545',
        wsUrl: process.env.WS_URL || 'ws://localhost:8546'
    });

    // Initialize and start
    const initialized = await guardrail.initialize();
    if (initialized) {
        guardrail.start();
        
        // Start listening for transactions after a short delay
        setTimeout(() => {
            guardrail.startListening();
        }, 3000);

        // Graceful shutdown
        process.on('SIGINT', async () => {
            await guardrail.stop();
            process.exit(0);
        });

        process.on('SIGTERM', async () => {
            await guardrail.stop();
            process.exit(0);
        });
    } else {
        console.error('Failed to initialize application');
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = QuantumSafeGuardrail;
