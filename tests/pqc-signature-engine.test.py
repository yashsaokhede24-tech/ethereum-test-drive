"""
Unit tests for PQC Signature Engine
"""

import unittest
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from pqc_signature_engine import PQCSignatureEngine, SignatureResult

class TestPQCSignatureEngine(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            self.engine = PQCSignatureEngine('dilithium2')
        except Exception as e:
            self.skipTest(f"PQC engine not available: {e}")
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'engine'):
            self.engine.cleanup()
    
    def test_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.default_algorithm, 'dilithium2')
        self.assertIn('dilithium2', self.engine.SUPPORTED_ALGORITHMS)
    
    def test_supported_algorithms(self):
        """Test supported algorithms list"""
        algorithms = self.engine.get_supported_algorithms()
        self.assertIsInstance(algorithms, dict)
        self.assertIn('dilithium2', algorithms)
        self.assertIn('dilithium3', algorithms)
        self.assertIn('falcon512', algorithms)
    
    def test_generate_keypair(self):
        """Test key pair generation"""
        address = '0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4'
        public_key, private_key = self.engine.generate_keypair(address)
        
        self.assertIsInstance(public_key, bytes)
        self.assertIsInstance(private_key, bytes)
        self.assertGreater(len(public_key), 0)
        self.assertGreater(len(private_key), 0)
        
        # Check if key pair is stored
        key_info = self.engine.get_key_info(address)
        self.assertIsNotNone(key_info)
        self.assertEqual(key_info['algorithm'], 'dilithium2')
    
    def test_sign_transaction(self):
        """Test transaction signing"""
        address = '0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4'
        
        # Generate key pair first
        self.engine.generate_keypair(address)
        
        transaction = {
            'from': address,
            'to': '0x8ba1f109551bD432803012645Hac136c4c4C4C4C4',
            'value': '1000000000000000000',
            'gasPrice': '20000000000',
            'gasLimit': '21000',
            'nonce': 42,
            'data': '0x'
        }
        
        result = self.engine.sign_transaction(transaction, address)
        
        self.assertIsInstance(result, SignatureResult)
        self.assertTrue(result.success)
        self.assertIsInstance(result.signature, bytes)
        self.assertIsInstance(result.public_key, bytes)
        self.assertEqual(result.algorithm, 'dilithium2')
        self.assertIsNone(result.error)
    
    def test_verify_signature(self):
        """Test signature verification"""
        address = '0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4'
        
        # Generate key pair
        self.engine.generate_keypair(address)
        
        transaction = {
            'from': address,
            'to': '0x8ba1f109551bD432803012645Hac136c4c4C4C4C4',
            'value': '1000000000000000000',
            'gasPrice': '20000000000',
            'gasLimit': '21000',
            'nonce': 42,
            'data': '0x'
        }
        
        # Sign the transaction
        sign_result = self.engine.sign_transaction(transaction, address)
        self.assertTrue(sign_result.success)
        
        # Verify the signature
        is_valid = self.engine.verify_signature(
            transaction,
            sign_result.signature,
            sign_result.public_key,
            sign_result.algorithm
        )
        
        self.assertTrue(is_valid)
    
    def test_upgrade_transaction_signature(self):
        """Test transaction upgrade with PQC signature"""
        address = '0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4'
        
        transaction = {
            'from': address,
            'to': '0x8ba1f109551bD432803012645Hac136c4c4C4C4C4',
            'value': '1000000000000000000',
            'gasPrice': '20000000000',
            'gasLimit': '21000',
            'nonce': 42,
            'data': '0x'
        }
        
        upgraded_tx = self.engine.upgrade_transaction_signature(transaction, address)
        
        # Check that the transaction was enhanced
        self.assertIn('pqc_signature', upgraded_tx)
        self.assertTrue(upgraded_tx['quantum_safe'])
        self.assertIn('signature', upgraded_tx['pqc_signature'])
        self.assertIn('public_key', upgraded_tx['pqc_signature'])
        self.assertIn('algorithm', upgraded_tx['pqc_signature'])
        self.assertEqual(upgraded_tx['pqc_signature']['algorithm'], 'dilithium2')
    
    def test_serialize_transaction(self):
        """Test transaction serialization"""
        transaction = {
            'from': '0xabc',
            'to': '0xdef',
            'value': '1000',
            'gasPrice': '20',
            'gasLimit': '21000',
            'nonce': 1,
            'data': '0x'
        }
        
        serialized = self.engine._serialize_transaction(transaction)
        
        self.assertIsInstance(serialized, str)
        # Should be valid JSON
        parsed = json.loads(serialized)
        self.assertEqual(parsed['from'], '0xabc')
        self.assertEqual(parsed['value'], '1000')
    
    def test_unsupported_algorithm(self):
        """Test error handling for unsupported algorithm"""
        with self.assertRaises(ValueError):
            PQCSignatureEngine('unsupported_algorithm')
    
    def test_sign_without_keypair(self):
        """Test signing without existing key pair"""
        address = '0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4'
        
        transaction = {
            'from': address,
            'to': '0x8ba1f109551bD432803012645Hac136c4c4C4C4C4',
            'value': '1000000000000000000',
            'gasPrice': '20000000000',
            'gasLimit': '21000',
            'nonce': 42,
            'data': '0x'
        }
        
        # Should automatically generate key pair
        result = self.engine.sign_transaction(transaction, address)
        self.assertTrue(result.success)
        
        # Check that key pair was created
        key_info = self.engine.get_key_info(address)
        self.assertIsNotNone(key_info)

if __name__ == '__main__':
    unittest.main()
