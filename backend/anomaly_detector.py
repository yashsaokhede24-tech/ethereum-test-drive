"""
AI/ML Anomaly Detection for Blockchain Transactions
Detects suspicious patterns in transaction data using machine learning
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from typing import Dict, List, Any, Tuple, Optional
import json
import time
from dataclasses import dataclass
import joblib
import os

@dataclass
class AnomalyResult:
    """Result of anomaly detection analysis"""
    is_anomaly: bool
    anomaly_score: float
    risk_level: str
    features: Dict[str, float]
    explanation: str
    timestamp: int

class TransactionAnomalyDetector:
    """
    Machine Learning-based anomaly detector for blockchain transactions
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize the anomaly detector
        
        Args:
            model_path: Path to saved model file
        """
        self.model_path = model_path or "models/anomaly_detector.pkl"
        self.scaler = StandardScaler()
        self.anomaly_model = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100
        )
        self.clustering_model = DBSCAN(eps=0.5, min_samples=5)
        self.is_trained = False
        self.feature_importance = {}
        
        # Load existing model if available
        self.load_model()
    
    def extract_features(self, transaction: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract numerical features from transaction data
        
        Args:
            transaction: Transaction data dictionary
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Basic transaction features
        features['value_eth'] = float(transaction.get('value', '0')) / 1e18
        features['gas_price_gwei'] = float(transaction.get('gasPrice', '0')) / 1e9
        features['gas_limit'] = float(transaction.get('gasLimit', '0'))
        features['nonce'] = float(transaction.get('nonce', '0'))
        
        # Data length and complexity
        data = transaction.get('data', '0x')
        features['data_length'] = len(data)
        features['data_complexity'] = len([c for c in data if c.isalnum()]) / max(len(data), 1)
        
        # Address patterns
        from_addr = transaction.get('from', '')
        to_addr = transaction.get('to', '')
        features['from_address_entropy'] = self._calculate_entropy(from_addr)
        features['to_address_entropy'] = self._calculate_entropy(to_addr)
        features['address_similarity'] = self._calculate_similarity(from_addr, to_addr)
        
        # Time-based features (if available)
        current_time = time.time()
        features['hour_of_day'] = (current_time % 86400) / 3600
        features['day_of_week'] = (current_time // 86400) % 7
        
        # Gas efficiency
        if features['gas_limit'] > 0:
            features['gas_efficiency'] = features['value_eth'] / features['gas_limit']
        else:
            features['gas_efficiency'] = 0
        
        # Round number detection
        features['is_round_value'] = 1 if features['value_eth'] % 1 == 0 else 0
        features['is_round_gas_price'] = 1 if features['gas_price_gwei'] % 1 == 0 else 0
        
        return features
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not text:
            return 0
        
        # Count character frequencies
        char_counts = {}
        for char in text.lower():
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0
        text_length = len(text)
        for count in char_counts.values():
            probability = count / text_length
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        return entropy
    
    def _calculate_similarity(self, addr1: str, addr2: str) -> float:
        """Calculate similarity between two addresses"""
        if not addr1 or not addr2:
            return 0
        
        # Simple character-based similarity
        common_chars = sum(1 for a, b in zip(addr1.lower(), addr2.lower()) if a == b)
        max_length = max(len(addr1), len(addr2))
        
        return common_chars / max_length if max_length > 0 else 0
    
    def train_model(self, transactions: List[Dict[str, Any]]) -> bool:
        """
        Train the anomaly detection model
        
        Args:
            transactions: List of transaction data for training
            
        Returns:
            True if training successful, False otherwise
        """
        try:
            print(f"Training anomaly detection model with {len(transactions)} transactions...")
            
            # Extract features from all transactions
            feature_data = []
            for tx in transactions:
                features = self.extract_features(tx)
                feature_data.append(features)
            
            # Convert to DataFrame
            df = pd.DataFrame(feature_data)
            
            # Handle missing values
            df = df.fillna(0)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(df)
            
            # Train anomaly detection model
            self.anomaly_model.fit(X_scaled)
            
            # Train clustering model for pattern analysis
            self.clustering_model.fit(X_scaled)
            
            # Calculate feature importance (using variance)
            feature_variance = np.var(X_scaled, axis=0)
            self.feature_importance = dict(zip(df.columns, feature_variance))
            
            self.is_trained = True
            
            # Save the trained model
            self.save_model()
            
            print("Model training completed successfully")
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def detect_anomaly(self, transaction: Dict[str, Any]) -> AnomalyResult:
        """
        Detect if a transaction is anomalous
        
        Args:
            transaction: Transaction data to analyze
            
        Returns:
            AnomalyResult object
        """
        try:
            # Extract features
            features = self.extract_features(transaction)
            
            if not self.is_trained:
                # Return neutral result if model not trained
                return AnomalyResult(
                    is_anomaly=False,
                    anomaly_score=0.0,
                    risk_level="unknown",
                    features=features,
                    explanation="Model not trained",
                    timestamp=int(time.time())
                )
            
            # Convert to array and scale
            feature_array = np.array([list(features.values())])
            feature_array_scaled = self.scaler.transform(feature_array)
            
            # Predict anomaly
            anomaly_score = self.anomaly_model.decision_function(feature_array_scaled)[0]
            is_anomaly = self.anomaly_model.predict(feature_array_scaled)[0] == -1
            
            # Determine risk level
            if is_anomaly:
                if anomaly_score < -0.5:
                    risk_level = "high"
                elif anomaly_score < -0.2:
                    risk_level = "medium"
                else:
                    risk_level = "low"
            else:
                risk_level = "normal"
            
            # Generate explanation
            explanation = self._generate_explanation(features, anomaly_score, is_anomaly)
            
            return AnomalyResult(
                is_anomaly=is_anomaly,
                anomaly_score=float(anomaly_score),
                risk_level=risk_level,
                features=features,
                explanation=explanation,
                timestamp=int(time.time())
            )
            
        except Exception as e:
            return AnomalyResult(
                is_anomaly=False,
                anomaly_score=0.0,
                risk_level="error",
                features={},
                explanation=f"Error in detection: {str(e)}",
                timestamp=int(time.time())
            )
    
    def _generate_explanation(self, features: Dict[str, float], 
                            anomaly_score: float, is_anomaly: bool) -> str:
        """Generate human-readable explanation for anomaly detection result"""
        explanations = []
        
        if not is_anomaly:
            return "Transaction appears normal based on learned patterns."
        
        # Check for specific anomaly patterns
        if features.get('value_eth', 0) > 100:
            explanations.append("High transaction value")
        
        if features.get('gas_price_gwei', 0) > 100:
            explanations.append("Unusually high gas price")
        
        if features.get('data_length', 0) > 1000:
            explanations.append("Large transaction data")
        
        if features.get('address_similarity', 0) > 0.8:
            explanations.append("Similar sender and receiver addresses")
        
        if features.get('is_round_value', 0) == 1 and features.get('value_eth', 0) > 10:
            explanations.append("Round number transaction value")
        
        if not explanations:
            explanations.append("Unusual pattern detected")
        
        return f"Anomaly detected: {', '.join(explanations)} (score: {anomaly_score:.3f})"
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        return self.feature_importance.copy()
    
    def save_model(self) -> bool:
        """Save the trained model to disk"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            model_data = {
                'anomaly_model': self.anomaly_model,
                'scaler': self.scaler,
                'clustering_model': self.clustering_model,
                'feature_importance': self.feature_importance,
                'is_trained': self.is_trained
            }
            
            joblib.dump(model_data, self.model_path)
            print(f"Model saved to {self.model_path}")
            return True
            
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def load_model(self) -> bool:
        """Load a previously trained model from disk"""
        try:
            if not os.path.exists(self.model_path):
                print(f"No saved model found at {self.model_path}")
                return False
            
            model_data = joblib.load(self.model_path)
            
            self.anomaly_model = model_data['anomaly_model']
            self.scaler = model_data['scaler']
            self.clustering_model = model_data['clustering_model']
            self.feature_importance = model_data['feature_importance']
            self.is_trained = model_data['is_trained']
            
            print(f"Model loaded from {self.model_path}")
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    import random
    
    # Initialize detector
    detector = TransactionAnomalyDetector()
    
    # Generate sample training data
    print("Generating sample training data...")
    sample_transactions = []
    
    for i in range(1000):
        tx = {
            'from': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
            'to': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
            'value': str(random.randint(100000000000000000, 1000000000000000000)),  # 0.1-1 ETH
            'gasPrice': str(random.randint(1000000000, 50000000000)),  # 1-50 gwei
            'gasLimit': str(random.randint(21000, 100000)),
            'nonce': random.randint(0, 100),
            'data': f"0x{''.join(random.choices('0123456789abcdef', k=random.randint(0, 100)))}"
        }
        sample_transactions.append(tx)
    
    # Add some anomalous transactions
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
        sample_transactions.append(tx)
    
    # Train the model
    success = detector.train_model(sample_transactions)
    
    if success:
        print("Testing anomaly detection...")
        
        # Test with normal transaction
        normal_tx = {
            'from': '0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4',
            'to': '0x8ba1f109551bD432803012645Hac136c4c4C4C4C4',
            'value': '1000000000000000000',  # 1 ETH
            'gasPrice': '20000000000',  # 20 gwei
            'gasLimit': '21000',
            'nonce': 42,
            'data': '0x'
        }
        
        result = detector.detect_anomaly(normal_tx)
        print(f"Normal transaction result: {result.is_anomaly} ({result.risk_level})")
        print(f"Explanation: {result.explanation}")
        
        # Test with anomalous transaction
        anomalous_tx = {
            'from': '0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4',
            'to': '0x8ba1f109551bD432803012645Hac136c4c4C4C4C4',
            'value': '100000000000000000000',  # 100 ETH
            'gasPrice': '1000000000000',  # 1000 gwei
            'gasLimit': '1000000',
            'nonce': 42,
            'data': f"0x{''.join(random.choices('0123456789abcdef', k=1000))}"
        }
        
        result = detector.detect_anomaly(anomalous_tx)
        print(f"Anomalous transaction result: {result.is_anomaly} ({result.risk_level})")
        print(f"Explanation: {result.explanation}")
        
        # Show feature importance
        importance = detector.get_feature_importance()
        print(f"Feature importance: {json.dumps(importance, indent=2)}")
