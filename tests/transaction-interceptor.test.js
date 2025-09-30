const TransactionInterceptor = require('../src/transaction-interceptor');

describe('TransactionInterceptor', () => {
    let interceptor;

    beforeEach(() => {
        interceptor = new TransactionInterceptor({
            rpcUrl: 'http://localhost:8545',
            wsUrl: 'ws://localhost:8546'
        });
    });

    afterEach(async () => {
        if (interceptor) {
            await interceptor.cleanup();
        }
    });

    test('should initialize with correct configuration', () => {
        expect(interceptor.config.rpcUrl).toBe('http://localhost:8545');
        expect(interceptor.config.wsUrl).toBe('ws://localhost:8546');
        expect(interceptor.isListening).toBe(false);
    });

    test('should handle pending transactions', async () => {
        const mockTx = {
            hash: '0x123',
            from: '0xabc',
            to: '0xdef',
            value: '1000000000000000000',
            gasPrice: '20000000000',
            gasLimit: '21000',
            data: '0x',
            nonce: 1
        };

        // Mock the provider
        interceptor.provider = {
            getTransaction: jest.fn().mockResolvedValue(mockTx)
        };

        await interceptor.handlePendingTransaction('0x123');

        const pendingTxs = interceptor.getPendingTransactions();
        expect(pendingTxs).toHaveLength(1);
        expect(pendingTxs[0].hash).toBe('0x123');
        expect(pendingTxs[0].status).toBe('pending');
    });

    test('should emit transaction captured event', (done) => {
        const mockTx = {
            hash: '0x123',
            from: '0xabc',
            to: '0xdef',
            value: '1000000000000000000',
            gasPrice: '20000000000',
            gasLimit: '21000',
            data: '0x',
            nonce: 1
        };

        interceptor.provider = {
            getTransaction: jest.fn().mockResolvedValue(mockTx)
        };

        interceptor.on('transactionCaptured', (data) => {
            expect(data.transaction.hash).toBe('0x123');
            done();
        });

        interceptor.handlePendingTransaction('0x123');
    });

    test('should start and stop listening', () => {
        expect(interceptor.isListening).toBe(false);
        
        interceptor.startListening();
        expect(interceptor.isListening).toBe(true);
        
        interceptor.stopListening();
        expect(interceptor.isListening).toBe(false);
    });
});
