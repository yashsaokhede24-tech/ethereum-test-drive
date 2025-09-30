import React, { useState, useEffect } from 'react';
import { Layout, Card, Statistic, Table, Alert, Button, Tabs, Progress, Tag, Space } from 'antd';
import { 
  ShieldOutlined, 
  WarningOutlined, 
  CheckCircleOutlined, 
  ClockCircleOutlined,
  ThunderboltOutlined,
  EyeOutlined
} from '@ant-design/icons';
import io from 'socket.io-client';
import './App.css';

const { Header, Content, Sider } = Layout;
const { TabPane } = Tabs;

function App() {
  const [stats, setStats] = useState({
    totalTransactions: 0,
    quantumSafeUpgrades: 0,
    anomaliesDetected: 0,
    uptime: 0
  });
  
  const [transactions, setTransactions] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Initialize WebSocket connection
    const newSocket = io('ws://localhost:3000');
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to WebSocket');
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from WebSocket');
      setIsConnected(false);
    });

    newSocket.on('stats', (data) => {
      setStats(data);
    });

    newSocket.on('transaction_captured', (data) => {
      console.log('Transaction captured:', data);
      setTransactions(prev => [data, ...prev.slice(0, 99)]); // Keep last 100
    });

    newSocket.on('transaction_upgraded', (data) => {
      console.log('Transaction upgraded:', data);
      // Update transaction in list
      setTransactions(prev => 
        prev.map(tx => 
          tx.hash === data.originalTx.hash 
            ? { ...tx, upgraded: true, upgradedTx: data.upgradedTx }
            : tx
        )
      );
    });

    newSocket.on('transaction_confirmed', (data) => {
      console.log('Transaction confirmed:', data);
      setTransactions(prev => 
        prev.map(tx => 
          tx.hash === data.hash 
            ? { ...tx, confirmed: true, confirmedAt: data.timestamp }
            : tx
        )
      );
    });

    // Fetch initial data
    fetchStats();
    fetchTransactions();

    return () => {
      newSocket.close();
    };
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchTransactions = async () => {
    try {
      const response = await fetch('/api/transactions/queue');
      const data = await response.json();
      setTransactions(data);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    }
  };

  const formatUptime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours}h ${minutes}m ${secs}s`;
  };

  const formatValue = (value) => {
    const eth = parseFloat(value) / 1e18;
    return `${eth.toFixed(4)} ETH`;
  };

  const formatGasPrice = (gasPrice) => {
    const gwei = parseFloat(gasPrice) / 1e9;
    return `${gwei.toFixed(2)} Gwei`;
  };

  const getStatusTag = (transaction) => {
    if (transaction.confirmed) {
      return <Tag color="green" icon={<CheckCircleOutlined />}>Confirmed</Tag>;
    } else if (transaction.upgraded) {
      return <Tag color="blue" icon={<ShieldOutlined />}>Quantum-Safe</Tag>;
    } else {
      return <Tag color="orange" icon={<ClockCircleOutlined />}>Pending</Tag>;
    }
  };

  const transactionColumns = [
    {
      title: 'Hash',
      dataIndex: 'hash',
      key: 'hash',
      render: (hash) => (
        <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
          {hash ? `${hash.slice(0, 10)}...${hash.slice(-8)}` : 'N/A'}
        </span>
      ),
    },
    {
      title: 'From',
      dataIndex: 'from',
      key: 'from',
      render: (from) => (
        <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
          {from ? `${from.slice(0, 6)}...${from.slice(-4)}` : 'N/A'}
        </span>
      ),
    },
    {
      title: 'To',
      dataIndex: 'to',
      key: 'to',
      render: (to) => (
        <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
          {to ? `${to.slice(0, 6)}...${to.slice(-4)}` : 'N/A'}
        </span>
      ),
    },
    {
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      render: (value) => formatValue(value || '0'),
    },
    {
      title: 'Gas Price',
      dataIndex: 'gasPrice',
      key: 'gasPrice',
      render: (gasPrice) => formatGasPrice(gasPrice || '0'),
    },
    {
      title: 'Status',
      key: 'status',
      render: (_, record) => getStatusTag(record),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button 
            size="small" 
            icon={<EyeOutlined />}
            onClick={() => console.log('View transaction:', record)}
          >
            View
          </Button>
          {!record.upgraded && (
            <Button 
              size="small" 
              type="primary"
              icon={<ShieldOutlined />}
              onClick={() => upgradeTransaction(record.hash)}
            >
              Upgrade
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const upgradeTransaction = async (txHash) => {
    try {
      const response = await fetch(`/api/transactions/${txHash}/upgrade`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        console.log(`Transaction ${txHash} upgraded successfully`);
        fetchTransactions(); // Refresh the list
      } else {
        console.error('Failed to upgrade transaction');
      }
    } catch (error) {
      console.error('Error upgrading transaction:', error);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          <ShieldOutlined style={{ marginRight: '8px' }} />
          Quantum-Safe Blockchain Guardrail
        </div>
        <div style={{ color: '#52c41a', fontSize: '12px' }}>
          {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
      </Header>
      
      <Layout>
        <Sider width={300} style={{ background: '#f0f2f5', padding: '16px' }}>
          <Card title="System Status" size="small">
            <Statistic
              title="Total Transactions"
              value={stats.totalTransactions}
              prefix={<ThunderboltOutlined />}
            />
            <Statistic
              title="Quantum-Safe Upgrades"
              value={stats.quantumSafeUpgrades}
              prefix={<ShieldOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <Statistic
              title="Anomalies Detected"
              value={stats.anomaliesDetected}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
            <Statistic
              title="Uptime"
              value={formatUptime(stats.uptime / 1000)}
              prefix={<ClockCircleOutlined />}
            />
          </Card>

          <Card title="Quick Actions" size="small" style={{ marginTop: '16px' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button 
                type="primary" 
                block 
                icon={<ShieldOutlined />}
                onClick={() => console.log('Manual upgrade all pending')}
              >
                Upgrade All Pending
              </Button>
              <Button 
                block 
                icon={<EyeOutlined />}
                onClick={() => console.log('View detailed logs')}
              >
                View Logs
              </Button>
              <Button 
                block 
                icon={<WarningOutlined />}
                onClick={() => console.log('View anomalies')}
              >
                View Anomalies
              </Button>
            </Space>
          </Card>
        </Sider>

        <Content style={{ padding: '24px' }}>
          <Tabs defaultActiveKey="transactions">
            <TabPane tab="Live Transactions" key="transactions">
              <Card>
                <Table
                  columns={transactionColumns}
                  dataSource={transactions}
                  rowKey="hash"
                  pagination={{ pageSize: 10 }}
                  size="small"
                />
              </Card>
            </TabPane>
            
            <TabPane tab="Anomaly Detection" key="anomalies">
              <Card>
                <Alert
                  message="Anomaly Detection Active"
                  description="The system is monitoring transactions for suspicious patterns using machine learning algorithms."
                  type="info"
                  showIcon
                  style={{ marginBottom: '16px' }}
                />
                <div style={{ textAlign: 'center', padding: '40px' }}>
                  <Progress
                    type="circle"
                    percent={75}
                    format={() => 'ML Model Active'}
                    strokeColor="#52c41a"
                  />
                  <p style={{ marginTop: '16px' }}>
                    Anomaly detection model is running and analyzing transaction patterns
                  </p>
                </div>
              </Card>
            </TabPane>
            
            <TabPane tab="Quantum-Safe Signatures" key="pqc">
              <Card>
                <Alert
                  message="Post-Quantum Cryptography Active"
                  description="Transactions are being upgraded with quantum-safe signature algorithms (CRYSTALS-Dilithium, Falcon)."
                  type="success"
                  showIcon
                  style={{ marginBottom: '16px' }}
                />
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <Card size="small" title="Supported Algorithms">
                    <Tag color="blue">Dilithium2</Tag>
                    <Tag color="green">Dilithium3</Tag>
                    <Tag color="orange">Dilithium5</Tag>
                    <Tag color="purple">Falcon-512</Tag>
                    <Tag color="red">Falcon-1024</Tag>
                  </Card>
                  <Card size="small" title="Current Algorithm">
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#52c41a' }}>
                      Dilithium2
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      Default quantum-safe signature algorithm
                    </div>
                  </Card>
                </div>
              </Card>
            </TabPane>
          </Tabs>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
