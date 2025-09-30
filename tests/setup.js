// Jest setup file for Quantum-Safe Blockchain Guardrail tests

// Mock console methods to reduce noise during tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

// Mock WebSocket for tests
global.WebSocket = jest.fn().mockImplementation(() => ({
  on: jest.fn(),
  send: jest.fn(),
  close: jest.fn(),
  readyState: 1, // OPEN
}));

// Mock ethers.js for tests
jest.mock('ethers', () => ({
  ethers: {
    JsonRpcProvider: jest.fn().mockImplementation(() => ({
      getNetwork: jest.fn().mockResolvedValue({ name: 'localhost', chainId: 1337 }),
      getTransaction: jest.fn(),
      getTransactionReceipt: jest.fn(),
      getBlock: jest.fn(),
      getTransactionCount: jest.fn(),
    })),
    WebSocketProvider: jest.fn().mockImplementation(() => ({
      on: jest.fn(),
      removeAllListeners: jest.fn(),
      destroy: jest.fn(),
    })),
  },
}));

// Set test environment variables
process.env.NODE_ENV = 'test';
process.env.RPC_URL = 'http://localhost:8545';
process.env.WS_URL = 'ws://localhost:8546';
process.env.PORT = '3001';
process.env.BACKEND_PORT = '5001';
