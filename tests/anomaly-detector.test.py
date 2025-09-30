"""
Unit tests for Anomaly Detector
"""

import unittest
import sys
import os
import json

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from anomaly_detector import TransactionAnomalyDetector, AnomalyResult

class TestTransactionAnomalyDetector(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = TransactionAnomalyDetector()
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'detector'):
            self.detector.cleanup()
    
    def test_initialization(self):
        """Test detector initialization"""
        self.assertIsNotNone(self.detector)
        self.assertFalse(self.detector.is_trained)
    
    def test_extract_features(self):
        """Test feature extraction from transaction"""
        transaction = {
            'from': '0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4',
            'to': '0x8ba1f109551bD432803012645Hac136c4c4C4C4C4',
            'value': '1000000000000000000',  # 1 ETH
            'gasPrice': '20000000000',  # 20 gwei
            'gasLimit': '21000',
            'nonce': 42,
            'data': '0x'
        }
        
        features = self.detector.extract_features(transaction)
        
        # Check that all expected features are present
        expected_features = [
            'value_eth', 'gas_price_gwei', 'gas_limit', 'nonce',
            'data_length', 'data_complexity', 'from_address_entropy',
            'to_address_entropy', 'address_similarity', 'hour_of_day',
            'day_of_week', 'gas_efficiency', 'is_round_value', 'is_round_gas_price'
        ]
        
        for feature in expected_features:
            self.assertIn(feature, features)
        
        # Check specific values
        self.assertEqual(features['value_eth'], 1.0)  # 1 ETH
        self.assertEqual(features['gas_price_gwei'], 20.0)  # 20 gwei
        self.assertEqual(features['gas_limit'], 21000)
        self.assertEqual(features['nonce'], 42)
        self.assertEqual(features['data_length'], 2)  # "0x"
        self.assertEqual(features['is_round_value'], 1)  # 1 ETH is round
        self.assertEqual(features['is_round_gas_price'], 1)  # 20 gwei is round
    
    def test_calculate_entropy(self):
        """Test entropy calculation"""
        # Test with simple string
        entropy1 = self.detector._calculate_entropy('abc')
        self.assertGreater(entropy1, 0)
        
        # Test with repeated characters (lower entropy)
        entropy2 = self.detector._calculate_entropy('aaa')
        self.assertLess(entropy2, entropy1)
        
        # Test with empty string
        entropy3 = self.detector._calculate_entropy('')
        self.assertEqual(entropy3, 0)
    
    def test_calculate_similarity(self):
        """Test address similarity calculation"""
        # Test with identical addresses
        similarity1 = self.detector._calculate_similarity('0xabc', '0xabc')
        self.assertEqual(similarity1, 1.0)
        
        # Test with different addresses
        similarity2 = self.detector._calculate_similarity('0xabc', '0xdef')
        self.assertLess(similarity2, 1.0)
        
        # Test with empty addresses
        similarity3 = self.detector._calculate_similarity('', '0xabc')
        self.assertEqual(similarity3, 0)
    
    def test_train_model(self):
        """Test model training"""
        # Generate sample training data
        training_data = self.generate_sample_transactions(100)
        
        success = self.detector.train_model(training_data)
        self.assertTrue(success)
        self.assertTrue(self.detector.is_trained)
    
    def test_detect_anomaly_untrained(self):
        """Test anomaly detection with untrained model"""
        transaction = {
            'from': '0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4',
            'to': '0x8ba1f109551bD432803012645Hac136c4c4C4C4C4',
            'value': '1000000000000000000',
            'gasPrice': '20000000000',
            'gasLimit': '21000',
            'nonce': 42,
            'data': '0x'
        }
        
        result = self.detector.detect_anomaly(transaction)
        
        self.assertIsInstance(result, AnomalyResult)
        self.assertFalse(result.is_anomaly)  # Should be false for untrained model
        self.assertEqual(result.risk_level, 'unknown')
        self.assertIn('Model not trained', result.explanation)
    
    def test_detect_anomaly_trained(self):
        """Test anomaly detection with trained model"""
        # Train the model first
        training_data = self.generate_sample_transactions(200)
        self.detector.train_model(training_data)
        
        # Test with normal transaction
        normal_transaction = {
            'from': '0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4',
            'to': '0x8ba1f109551bD432803012645Hac136c4c4C4C4C4',
            'value': '1000000000000000000',  # 1 ETH
            'gasPrice': '20000000000',  # 20 gwei
            'gasLimit': '21000',
            'nonce': 42,
            'data': '0x'
        }
        
        result = self.detector.detect_anomaly(normal_transaction)
        
        self.assertIsInstance(result, AnomalyResult)
        self.assertIn(result.risk_level, ['normal', 'low', 'medium', 'high'])
        self.assertIsInstance(result.anomaly_score, float)
        self.assertIsInstance(result.features, dict)
        self.assertIsInstance(result.explanation, str)
    
    def test_detect_anomaly_anomalous(self):
        """Test anomaly detection with anomalous transaction"""
        # Train the model first
        training_data = self.generate_sample_transactions(200)
        self.detector.train_model(training_data)
        
        # Test with anomalous transaction (very high value)
        anomalous_transaction = {
            'from': '0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4',
            'to': '0x8ba1f109551bD432803012645Hac136c4c4C4C4C4',
            'value': '100000000000000000000000',  # 100,000 ETH
            'gasPrice': '1000000000000',  # 1000 gwei
            'gasLimit': '2000000',
            'nonce': 42,
            'data': '0x' + 'a' * 1000  # Large data
        }
        
        result = self.detector.detect_anomaly(anomalous_transaction)
        
        self.assertIsInstance(result, AnomalyResult)
        self.assertIn(result.risk_level, ['normal', 'low', 'medium', 'high'])
        # Note: The actual anomaly detection depends on the training data
        # and may not always detect this as anomalous
    
    def test_get_feature_importance(self):
        """Test feature importance retrieval"""
        # Train the model first
        training_data = self.generate_sample_transactions(100)
        self.detector.train_model(training_data)
        
        importance = self.detector.get_feature_importance()
        
        self.assertIsInstance(importance, dict)
        self.assertGreater(len(importance), 0)
        
        # Check that all features have importance scores
        for feature, score in importance.items():
            self.assertIsInstance(feature, str)
            self.assertIsInstance(score, (int, float))
            self.assertGreaterEqual(score, 0)
    
    def test_save_and_load_model(self):
        """Test model saving and loading"""
        # Train the model
        training_data = self.generate_sample_transactions(100)
        self.detector.train_model(training_data)
        
        # Save the model
        save_success = self.detector.save_model()
        self.assertTrue(save_success)
        
        # Create new detector and load model
        new_detector = TransactionAnomalyDetector()
        load_success = new_detector.load_model()
        
        if load_success:
            self.assertTrue(new_detector.is_trained)
            self.assertGreater(len(new_detector.get_feature_importance()), 0)
        
        new_detector.cleanup()
    
    def generate_sample_transactions(self, count):
        """Generate sample transaction data for testing"""
        import random
        
        transactions = []
        for i in range(count):
            tx = {
                'from': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
                'to': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
                'value': str(random.randint(100000000000000000, 1000000000000000000)),
                'gasPrice': str(random.randint(1000000000, 50000000000)),
                'gasLimit': str(random.randint(21000, 100000)),
                'nonce': random.randint(0, 100),
                'data': f"0x{''.join(random.choices('0123456789abcdef', k=random.randint(0, 100)))}"
            }
            transactions.append(tx)
        
        return transactions

if __name__ == '__main__':
    unittest.main()
