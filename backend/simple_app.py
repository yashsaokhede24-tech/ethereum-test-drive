"""
Simplified Quantum-Safe Blockchain Guardrail Backend
Works without liboqs for demonstration purposes
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
import threading
from typing import Dict, List, Any
import logging
import hashlib
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global instances
transaction_cache = {}
stats = {
    'total_processed': 0,
    'quantum_safe_upgrades': 0,
    'anomalies_detected': 0,
    'start_time': time.time()
}

class SimplePQCSignatureEngine:
    """Simplified PQC signature engine for demonstration"""
    
    def __init__(self):
        self.key_pairs = {}
    
    def generate_keypair(self, address: str):
        """Generate a simple key pair for demonstration"""
        # Simulate key generation
        public_key = f"pqc_pub_{address[-8:]}_{int(time.time())}"
        private_key = f"pqc_priv_{address[-8:]}_{int(time.time())}"
        
        self.key_pairs[address] = {
            'public_key': public_key,
            'private_key': private_key,
            'algorithm': 'dilithium2_simulated'
        }
        
        return public_key, private_key
    
    def sign_transaction(self, transaction_data: Dict[str, Any], address: str):
        """Sign transaction with simulated PQC signature"""
        if address not in self.key_pairs:
            self.generate_keypair(address)
        
        # Create a simple signature
        tx_string = json.dumps(transaction_data, sort_keys=True)
        tx_hash = hashlib.sha256(tx_string.encode()).hexdigest()
        signature = f"pqc_sig_{tx_hash[:16]}_{int(time.time())}"
        
        return {
            'signature': signature,
            'public_key': self.key_pairs[address]['public_key'],
            'algorithm': 'dilithium2_simulated',
            'success': True
        }
    
    def upgrade_transaction_signature(self, transaction_data: Dict[str, Any], address: str):
        """Upgrade transaction with simulated PQC signature"""
        signature_result = self.sign_transaction(transaction_data, address)
        
        enhanced_transaction = transaction_data.copy()
        enhanced_transaction['pqc_signature'] = {
            'signature': signature_result['signature'],
            'public_key': signature_result['public_key'],
            'algorithm': signature_result['algorithm'],
            'timestamp': int(time.time())
        }
        enhanced_transaction['quantum_safe'] = True
        enhanced_transaction['original_signature'] = transaction_data.get('signature', '')
        
        return enhanced_transaction

class SimpleAnomalyDetector:
    """Simplified anomaly detector for demonstration"""
    
    def __init__(self):
        self.is_trained = True
    
    def detect_anomaly(self, transaction: Dict[str, Any]):
        """Simple anomaly detection based on transaction value"""
        value = float(transaction.get('value', '0'))
        value_eth = value / 1e18
        
        # Simple rule: transactions over 10 ETH are suspicious
        is_anomaly = value_eth > 10
        risk_level = 'high' if value_eth > 100 else 'medium' if value_eth > 10 else 'low'
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': value_eth / 100,  # Simple score
            'risk_level': risk_level,
            'explanation': f'Transaction value: {value_eth:.2f} ETH',
            'features': {'value_eth': value_eth},
            'timestamp': int(time.time())
        }

# Initialize simplified services
pqc_engine = SimplePQCSignatureEngine()
anomaly_detector = SimpleAnomalyDetector()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'pqc_engine': True,
            'anomaly_detector': True
        },
        'uptime': time.time() - stats['start_time']
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get processing statistics"""
    return jsonify(stats)

@app.route('/api/upgrade-transaction', methods=['POST'])
def upgrade_transaction():
    """Upgrade a transaction with quantum-safe signature"""
    try:
        data = request.get_json()
        transaction = data.get('transaction')
        
        if not transaction:
            return jsonify({'error': 'No transaction data provided'}), 400
        
        # Extract address for signing
        address = transaction.get('from', '0x0000000000000000000000000000000000000000')
        
        # Upgrade transaction with PQC signature
        upgraded_tx = pqc_engine.upgrade_transaction_signature(transaction, address)
        
        # Update stats
        stats['total_processed'] += 1
        stats['quantum_safe_upgrades'] += 1
        
        # Cache the transaction
        tx_hash = transaction.get('hash', f"tx_{int(time.time())}")
        transaction_cache[tx_hash] = {
            'original': transaction,
            'upgraded': upgraded_tx,
            'timestamp': time.time()
        }
        
        return jsonify({
            'success': True,
            'transaction': upgraded_tx,
            'tx_hash': tx_hash
        })
        
    except Exception as e:
        logger.error(f"Error upgrading transaction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/detect-anomaly', methods=['POST'])
def detect_anomaly():
    """Detect anomalies in transaction data"""
    try:
        data = request.get_json()
        transaction = data.get('transaction')
        
        if not transaction:
            return jsonify({'error': 'No transaction data provided'}), 400
        
        # Detect anomalies
        result = anomaly_detector.detect_anomaly(transaction)
        
        # Update stats if anomaly detected
        if result['is_anomaly']:
            stats['anomalies_detected'] += 1
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error detecting anomaly: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-transaction', methods=['POST'])
def process_transaction():
    """Process a transaction (upgrade + anomaly detection)"""
    try:
        data = request.get_json()
        transaction = data.get('transaction')
        
        if not transaction:
            return jsonify({'error': 'No transaction data provided'}), 400
        
        results = {}
        
        # Upgrade with quantum-safe signature
        try:
            address = transaction.get('from', '0x0000000000000000000000000000000000000000')
            upgraded_tx = pqc_engine.upgrade_transaction_signature(transaction, address)
            results['upgrade'] = {
                'success': True,
                'transaction': upgraded_tx
            }
            stats['quantum_safe_upgrades'] += 1
        except Exception as e:
            results['upgrade'] = {
                'success': False,
                'error': str(e)
            }
        
        # Detect anomalies
        try:
            anomaly_result = anomaly_detector.detect_anomaly(transaction)
            results['anomaly'] = {
                'success': True,
                'result': anomaly_result
            }
            if anomaly_result['is_anomaly']:
                stats['anomalies_detected'] += 1
        except Exception as e:
            results['anomaly'] = {
                'success': False,
                'error': str(e)
            }
        
        stats['total_processed'] += 1
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error processing transaction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/<tx_hash>', methods=['GET'])
def get_transaction(tx_hash):
    """Get cached transaction data"""
    if tx_hash in transaction_cache:
        return jsonify({
            'success': True,
            'transaction': transaction_cache[tx_hash]
        })
    else:
        return jsonify({'error': 'Transaction not found'}), 404

@app.route('/api/transactions', methods=['GET'])
def list_transactions():
    """List all cached transactions"""
    return jsonify({
        'success': True,
        'transactions': list(transaction_cache.values()),
        'count': len(transaction_cache)
    })

@app.route('/api/algorithms', methods=['GET'])
def get_supported_algorithms():
    """Get supported PQC algorithms"""
    return jsonify({
        'success': True,
        'algorithms': {
            'dilithium2': 'Dilithium2 (Simulated)',
            'dilithium3': 'Dilithium3 (Simulated)',
            'falcon512': 'Falcon-512 (Simulated)'
        }
    })

if __name__ == '__main__':
    logger.info("Starting Quantum-Safe Blockchain Guardrail Backend (Simplified)...")
    logger.info("Note: Using simulated PQC signatures for demonstration")
    app.run(host='0.0.0.0', port=5000, debug=True)
