"""
Quantum-Safe Blockchain Guardrail Backend
Flask API for PQC signature processing and anomaly detection
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
import threading
from typing import Dict, List, Any
import logging

# Import our custom modules
from pqc_signature_engine import PQCSignatureEngine
from anomaly_detector import TransactionAnomalyDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global instances
pqc_engine = None
anomaly_detector = None
transaction_cache = {}
stats = {
    'total_processed': 0,
    'quantum_safe_upgrades': 0,
    'anomalies_detected': 0,
    'start_time': time.time()
}

def initialize_services():
    """Initialize PQC engine and anomaly detector"""
    global pqc_engine, anomaly_detector
    
    try:
        # Initialize PQC signature engine
        pqc_engine = PQCSignatureEngine('dilithium2')
        logger.info("PQC Signature Engine initialized")
        
        # Initialize anomaly detector
        anomaly_detector = TransactionAnomalyDetector()
        logger.info("Anomaly Detector initialized")
        
        # Train anomaly detector with sample data if not already trained
        if not anomaly_detector.is_trained:
            train_anomaly_detector()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        return False

def train_anomaly_detector():
    """Train the anomaly detector with sample data"""
    try:
        # Generate sample training data
        sample_transactions = generate_sample_training_data()
        
        # Train the model
        success = anomaly_detector.train_model(sample_transactions)
        if success:
            logger.info("Anomaly detector trained successfully")
        else:
            logger.warning("Failed to train anomaly detector")
            
    except Exception as e:
        logger.error(f"Error training anomaly detector: {e}")

def generate_sample_training_data() -> List[Dict[str, Any]]:
    """Generate sample transaction data for training"""
    import random
    
    transactions = []
    
    # Generate normal transactions
    for i in range(500):
        tx = {
            'from': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
            'to': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
            'value': str(random.randint(100000000000000000, 1000000000000000000)),  # 0.1-1 ETH
            'gasPrice': str(random.randint(1000000000, 50000000000)),  # 1-50 gwei
            'gasLimit': str(random.randint(21000, 100000)),
            'nonce': random.randint(0, 100),
            'data': f"0x{''.join(random.choices('0123456789abcdef', k=random.randint(0, 100)))}"
        }
        transactions.append(tx)
    
    # Generate some anomalous transactions
    for i in range(50):
        tx = {
            'from': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
            'to': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
            'value': str(random.randint(10000000000000000000, 100000000000000000000)),  # 10-100 ETH
            'gasPrice': str(random.randint(100000000000, 1000000000000)),  # 100-1000 gwei
            'gasLimit': str(random.randint(500000, 2000000)),
            'nonce': random.randint(0, 100),
            'data': f"0x{''.join(random.choices('0123456789abcdef', k=random.randint(500, 2000)))}"
        }
        transactions.append(tx)
    
    return transactions

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'pqc_engine': pqc_engine is not None,
            'anomaly_detector': anomaly_detector is not None
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
        
        if not pqc_engine:
            return jsonify({'error': 'PQC engine not initialized'}), 500
        
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
        
        if not anomaly_detector:
            return jsonify({'error': 'Anomaly detector not initialized'}), 500
        
        # Detect anomalies
        result = anomaly_detector.detect_anomaly(transaction)
        
        # Update stats if anomaly detected
        if result.is_anomaly:
            stats['anomalies_detected'] += 1
        
        return jsonify({
            'success': True,
            'result': {
                'is_anomaly': result.is_anomaly,
                'anomaly_score': result.anomaly_score,
                'risk_level': result.risk_level,
                'explanation': result.explanation,
                'features': result.features,
                'timestamp': result.timestamp
            }
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
        if pqc_engine:
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
        if anomaly_detector:
            try:
                anomaly_result = anomaly_detector.detect_anomaly(transaction)
                results['anomaly'] = {
                    'success': True,
                    'result': {
                        'is_anomaly': anomaly_result.is_anomaly,
                        'anomaly_score': anomaly_result.anomaly_score,
                        'risk_level': anomaly_result.risk_level,
                        'explanation': anomaly_result.explanation
                    }
                }
                if anomaly_result.is_anomaly:
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
    if pqc_engine:
        return jsonify({
            'success': True,
            'algorithms': pqc_engine.get_supported_algorithms()
        })
    else:
        return jsonify({'error': 'PQC engine not initialized'}), 500

@app.route('/api/feature-importance', methods=['GET'])
def get_feature_importance():
    """Get anomaly detection feature importance"""
    if anomaly_detector:
        return jsonify({
            'success': True,
            'feature_importance': anomaly_detector.get_feature_importance()
        })
    else:
        return jsonify({'error': 'Anomaly detector not initialized'}), 500

@app.route('/api/retrain-model', methods=['POST'])
def retrain_model():
    """Retrain the anomaly detection model"""
    try:
        if not anomaly_detector:
            return jsonify({'error': 'Anomaly detector not initialized'}), 500
        
        # Generate new training data
        training_data = generate_sample_training_data()
        
        # Retrain the model
        success = anomaly_detector.train_model(training_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Model retrained successfully'
            })
        else:
            return jsonify({'error': 'Failed to retrain model'}), 500
            
    except Exception as e:
        logger.error(f"Error retraining model: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize services
    if initialize_services():
        logger.info("Starting Quantum-Safe Blockchain Guardrail Backend...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        logger.error("Failed to initialize services. Exiting.")
        exit(1)
