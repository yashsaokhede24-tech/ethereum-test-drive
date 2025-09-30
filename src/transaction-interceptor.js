const { ethers } = require('ethers');
const EventEmitter = require('events');
const WebSocket = require('ws');

/**
 * Quantum-Safe Transaction Interceptor
 * Captures blockchain transactions and prepares them for quantum-safe upgrades
 */
class TransactionInterceptor extends EventEmitter {
    constructor(config = {}) {
        super();
        this.config = {
            rpcUrl: config.rpcUrl || 'http://localhost:8545',
            wsUrl: config.wsUrl || 'ws://localhost:8546',
            blockConfirmations: config.blockConfirmations || 1,
            ...config
        };
        
        this.provider = null;
        this.wsProvider = null;
        this.isListening = false;
        this.pendingTransactions = new Map();
    }

    /**
     * Initialize the interceptor with blockchain connection
     */
    async initialize() {
        try {
            // Initialize JSON-RPC provider
            this.provider = new ethers.JsonRpcProvider(this.config.rpcUrl);
            
            // Test connection
            const network = await this.provider.getNetwork();
            console.log(`Connected to network: ${network.name} (${network.chainId})`);
            
            // Initialize WebSocket provider for real-time monitoring
            if (this.config.wsUrl) {
                this.wsProvider = new ethers.WebSocketProvider(this.config.wsUrl);
                this.setupWebSocketListeners();
            }
            
            this.emit('initialized', { network: network.name, chainId: network.chainId });
            return true;
        } catch (error) {
            console.error('Failed to initialize transaction interceptor:', error);
            this.emit('error', error);
            return false;
        }
    }

    /**
     * Set up WebSocket listeners for real-time transaction monitoring
     */
    setupWebSocketListeners() {
        if (!this.wsProvider) return;

        // Listen for new pending transactions
        this.wsProvider.on('pending', (txHash) => {
            this.handlePendingTransaction(txHash);
        });

        // Listen for new blocks
        this.wsProvider.on('block', (blockNumber) => {
            this.handleNewBlock(blockNumber);
        });

        this.wsProvider.on('error', (error) => {
            console.error('WebSocket provider error:', error);
            this.emit('error', error);
        });
    }

    /**
     * Handle pending transaction
     */
    async handlePendingTransaction(txHash) {
        try {
            // Get transaction details
            const tx = await this.provider.getTransaction(txHash);
            if (!tx) return;

            // Store pending transaction
            this.pendingTransactions.set(txHash, {
                hash: txHash,
                from: tx.from,
                to: tx.to,
                value: tx.value.toString(),
                gasPrice: tx.gasPrice?.toString(),
                gasLimit: tx.gasLimit.toString(),
                data: tx.data,
                nonce: tx.nonce,
                timestamp: Date.now(),
                status: 'pending'
            });

            // Emit transaction captured event
            this.emit('transactionCaptured', {
                type: 'pending',
                transaction: this.pendingTransactions.get(txHash)
            });

            console.log(`Captured pending transaction: ${txHash}`);
        } catch (error) {
            console.error(`Error handling pending transaction ${txHash}:`, error);
        }
    }

    /**
     * Handle new block and check for confirmed transactions
     */
    async handleNewBlock(blockNumber) {
        try {
            const block = await this.provider.getBlock(blockNumber, true);
            if (!block || !block.transactions) return;

            // Check each transaction in the block
            for (const tx of block.transactions) {
                const txHash = typeof tx === 'string' ? tx : tx.hash;
                
                if (this.pendingTransactions.has(txHash)) {
                    // Transaction was confirmed
                    const pendingTx = this.pendingTransactions.get(txHash);
                    pendingTx.status = 'confirmed';
                    pendingTx.blockNumber = blockNumber;
                    pendingTx.confirmations = 1;

                    this.emit('transactionConfirmed', {
                        transaction: pendingTx,
                        blockNumber: blockNumber
                    });

                    // Remove from pending after some confirmations
                    setTimeout(() => {
                        this.pendingTransactions.delete(txHash);
                    }, this.config.blockConfirmations * 12000); // ~12 seconds per block
                }
            }

            this.emit('newBlock', { blockNumber, transactionCount: block.transactions.length });
        } catch (error) {
            console.error(`Error handling new block ${blockNumber}:`, error);
        }
    }

    /**
     * Start listening for transactions
     */
    startListening() {
        if (this.isListening) {
            console.log('Transaction interceptor is already listening');
            return;
        }

        this.isListening = true;
        console.log('Started listening for blockchain transactions...');
        this.emit('listeningStarted');
    }

    /**
     * Stop listening for transactions
     */
    stopListening() {
        this.isListening = false;
        if (this.wsProvider) {
            this.wsProvider.removeAllListeners();
        }
        console.log('Stopped listening for blockchain transactions');
        this.emit('listeningStopped');
    }

    /**
     * Get current pending transactions
     */
    getPendingTransactions() {
        return Array.from(this.pendingTransactions.values());
    }

    /**
     * Get transaction by hash
     */
    async getTransaction(txHash) {
        try {
            const tx = await this.provider.getTransaction(txHash);
            const receipt = await this.provider.getTransactionReceipt(txHash);
            
            return {
                transaction: tx,
                receipt: receipt,
                confirmations: receipt ? await this.provider.getTransactionCount(tx.from) - tx.nonce : 0
            };
        } catch (error) {
            console.error(`Error getting transaction ${txHash}:`, error);
            return null;
        }
    }

    /**
     * Cleanup resources
     */
    async cleanup() {
        this.stopListening();
        if (this.wsProvider) {
            await this.wsProvider.destroy();
        }
        console.log('Transaction interceptor cleaned up');
    }
}

module.exports = TransactionInterceptor;
