"""
Post-Quantum Cryptography Signature Engine
Implements quantum-safe signature algorithms using liboqs
"""

import json
import base64
import hashlib
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import liboqs

@dataclass
class SignatureResult:
    """Result of quantum-safe signature operation"""
    signature: bytes
    public_key: bytes
    algorithm: str
    success: bool
    error: Optional[str] = None

class PQCSignatureEngine:
    """
    Post-Quantum Cryptography Signature Engine
    Supports CRYSTALS-Dilithium and Falcon algorithms
    """
    
    SUPPORTED_ALGORITHMS = {
        'dilithium2': 'Dilithium2',
        'dilithium3': 'Dilithium3', 
        'dilithium5': 'Dilithium5',
        'falcon512': 'Falcon-512',
        'falcon1024': 'Falcon-1024'
    }
    
    def __init__(self, default_algorithm: str = 'dilithium2'):
        """
        Initialize the PQC signature engine
        
        Args:
            default_algorithm: Default algorithm to use for signatures
        """
        self.default_algorithm = default_algorithm
        self.key_pairs = {}  # Store key pairs by address
        
        # Verify liboqs is available
        if not liboqs.is_enabled():
            raise RuntimeError("liboqs is not properly installed or enabled")
        
        # Check if default algorithm is supported
        if default_algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {default_algorithm}")
    
    def generate_keypair(self, address: str, algorithm: str = None) -> Tuple[bytes, bytes]:
        """
        Generate a new quantum-safe key pair
        
        Args:
            address: Ethereum address to associate with this key pair
            algorithm: PQC algorithm to use (defaults to instance default)
            
        Returns:
            Tuple of (public_key, private_key)
        """
        if algorithm is None:
            algorithm = self.default_algorithm
            
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        try:
            # Generate key pair using liboqs
            with liboqs.Signature(self.SUPPORTED_ALGORITHMS[algorithm]) as signer:
                public_key = signer.generate_keypair()
                private_key = signer.export_secret_key()
            
            # Store key pair
            self.key_pairs[address] = {
                'public_key': public_key,
                'private_key': private_key,
                'algorithm': algorithm
            }
            
            return public_key, private_key
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate key pair: {str(e)}")
    
    def sign_transaction(self, transaction_data: Dict[str, Any], address: str) -> SignatureResult:
        """
        Sign transaction data with quantum-safe signature
        
        Args:
            transaction_data: Transaction data to sign
            address: Address associated with the signing key
            
        Returns:
            SignatureResult object
        """
        try:
            # Get or generate key pair for address
            if address not in self.key_pairs:
                self.generate_keypair(address)
            
            key_info = self.key_pairs[address]
            algorithm = key_info['algorithm']
            
            # Serialize transaction data for signing
            tx_string = self._serialize_transaction(transaction_data)
            tx_hash = hashlib.sha256(tx_string.encode()).digest()
            
            # Sign with quantum-safe algorithm
            with liboqs.Signature(self.SUPPORTED_ALGORITHMS[algorithm]) as signer:
                signer.import_secret_key(key_info['private_key'])
                signature = signer.sign(tx_hash)
            
            return SignatureResult(
                signature=signature,
                public_key=key_info['public_key'],
                algorithm=algorithm,
                success=True
            )
            
        except Exception as e:
            return SignatureResult(
                signature=b'',
                public_key=b'',
                algorithm='',
                success=False,
                error=str(e)
            )
    
    def verify_signature(self, transaction_data: Dict[str, Any], signature: bytes, 
                        public_key: bytes, algorithm: str) -> bool:
        """
        Verify a quantum-safe signature
        
        Args:
            transaction_data: Original transaction data
            signature: Signature to verify
            public_key: Public key for verification
            algorithm: Algorithm used for signing
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            if algorithm not in self.SUPPORTED_ALGORITHMS:
                return False
            
            # Serialize transaction data
            tx_string = self._serialize_transaction(transaction_data)
            tx_hash = hashlib.sha256(tx_string.encode()).digest()
            
            # Verify signature
            with liboqs.Signature(self.SUPPORTED_ALGORITHMS[algorithm]) as signer:
                signer.import_public_key(public_key)
                return signer.verify(tx_hash, signature)
                
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False
    
    def upgrade_transaction_signature(self, transaction_data: Dict[str, Any], 
                                    address: str) -> Dict[str, Any]:
        """
        Upgrade a transaction with quantum-safe signature
        
        Args:
            transaction_data: Original transaction data
            address: Address to sign with
            
        Returns:
            Enhanced transaction data with PQC signature
        """
        # Sign the transaction
        signature_result = self.sign_transaction(transaction_data, address)
        
        if not signature_result.success:
            raise RuntimeError(f"Failed to sign transaction: {signature_result.error}")
        
        # Create enhanced transaction with PQC signature
        enhanced_transaction = transaction_data.copy()
        enhanced_transaction['pqc_signature'] = {
            'signature': base64.b64encode(signature_result.signature).decode(),
            'public_key': base64.b64encode(signature_result.public_key).decode(),
            'algorithm': signature_result.algorithm,
            'timestamp': int(time.time())
        }
        
        # Add metadata
        enhanced_transaction['quantum_safe'] = True
        enhanced_transaction['original_signature'] = transaction_data.get('signature', '')
        
        return enhanced_transaction
    
    def _serialize_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """
        Serialize transaction data for consistent hashing
        
        Args:
            transaction_data: Transaction data dictionary
            
        Returns:
            Serialized string representation
        """
        # Create a deterministic serialization
        serializable_data = {
            'from': transaction_data.get('from', ''),
            'to': transaction_data.get('to', ''),
            'value': str(transaction_data.get('value', '0')),
            'gasPrice': str(transaction_data.get('gasPrice', '0')),
            'gasLimit': str(transaction_data.get('gasLimit', '0')),
            'nonce': str(transaction_data.get('nonce', '0')),
            'data': transaction_data.get('data', '0x')
        }
        
        # Sort keys for consistent ordering
        return json.dumps(serializable_data, sort_keys=True, separators=(',', ':'))
    
    def get_supported_algorithms(self) -> Dict[str, str]:
        """Get list of supported algorithms"""
        return self.SUPPORTED_ALGORITHMS.copy()
    
    def get_key_info(self, address: str) -> Optional[Dict[str, Any]]:
        """Get key information for an address"""
        return self.key_pairs.get(address)
    
    def cleanup(self):
        """Clean up resources"""
        self.key_pairs.clear()

# Example usage and testing
if __name__ == "__main__":
    import time
    
    # Initialize the PQC engine
    engine = PQCSignatureEngine('dilithium2')
    
    # Example transaction data
    sample_transaction = {
        'from': '0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4',
        'to': '0x8ba1f109551bD432803012645Hac136c4c4C4C4C4',
        'value': '1000000000000000000',  # 1 ETH in wei
        'gasPrice': '20000000000',  # 20 gwei
        'gasLimit': '21000',
        'nonce': 42,
        'data': '0x'
    }
    
    print("Testing Quantum-Safe Signature Engine...")
    print(f"Supported algorithms: {engine.get_supported_algorithms()}")
    
    # Test signature generation and verification
    address = sample_transaction['from']
    
    # Generate key pair
    public_key, private_key = engine.generate_keypair(address)
    print(f"Generated key pair for {address}")
    
    # Sign transaction
    signature_result = engine.sign_transaction(sample_transaction, address)
    print(f"Signature result: {signature_result.success}")
    
    if signature_result.success:
        # Verify signature
        is_valid = engine.verify_signature(
            sample_transaction, 
            signature_result.signature, 
            signature_result.public_key, 
            signature_result.algorithm
        )
        print(f"Signature verification: {is_valid}")
        
        # Test transaction upgrade
        enhanced_tx = engine.upgrade_transaction_signature(sample_transaction, address)
        print(f"Enhanced transaction: {json.dumps(enhanced_tx, indent=2)}")
    
    engine.cleanup()
