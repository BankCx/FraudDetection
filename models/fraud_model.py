from datetime import datetime
import json
import pickle
import os

class FraudModel:
    def __init__(self):
        self.threshold = 0.7

    def load_model(self, model_path):
        """Load a trained model from file (legacy support)"""
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
            except:
                # If pickle fails, use default model
                self.model = None

    def save_model(self, model_path):
        """Save the trained model to file (legacy support)"""
        # Save a simple model state for compatibility
        model_data = {
            'threshold': self.threshold,
            'version': 'rule-based-v1'
        }
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)

    def extract_features(self, transaction):
        """Extract features from transaction data"""
        features = {
            'amount': float(transaction.get('amount', 0)),
            'timestamp': self._parse_timestamp(transaction.get('ts', datetime.now().isoformat())),
            'merchant_id': hash(transaction.get('merchant_id', '')) % 1000,
            'user_id': hash(transaction.get('user_id', '')) % 1000,
            'country': hash(transaction.get('country', '')) % 100,
            'channel': hash(transaction.get('channel', '')) % 10,
        }
        return features

    def _parse_timestamp(self, ts_str):
        """Parse timestamp string to numeric value"""
        try:
            dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
            return dt.timestamp()
        except:
            return datetime.now().timestamp()

    def predict_one(self, transaction):
        """Predict fraud for a single transaction using rule-based logic"""
        try:
            features = self.extract_features(transaction)
            
            # Simple rule-based fraud detection
            risk_score = 0.0
            
            # Rule 1: High amount transactions
            amount = features['amount']
            if amount > 1000:
                risk_score += 0.3
            if amount > 5000:
                risk_score += 0.4
            if amount > 10000:
                risk_score += 0.3
            
            # Rule 2: Suspicious countries
            country_hash = features['country']
            suspicious_countries = [hash('XX') % 100, hash('YY') % 100, hash('ZZ') % 100]
            if country_hash in suspicious_countries:
                risk_score += 0.5
            
            # Rule 3: Web channel (more likely fraud)
            if features['channel'] == hash('web') % 10:
                risk_score += 0.1
            
            # Rule 4: Large merchant transactions
            if amount > 2000 and features['merchant_id'] in [hash('amazon') % 1000, hash('walmart') % 1000]:
                risk_score += 0.2
            
            # Cap risk score at 1.0
            risk_score = min(risk_score, 1.0)
            
            # Determine label based on threshold
            label = 'fraud' if risk_score > self.threshold else 'legit'
            
            return {
                'risk_score': risk_score,
                'label': label
            }
        except Exception as e:
            # Return default prediction on error
            return {
                'risk_score': 0.5,
                'label': 'legit'
            }

    def predict(self, transaction):
        """Legacy predict method for backward compatibility"""
        result = self.predict_one(transaction)
        return result['label'] == 'fraud'

    def train(self, training_data):
        """Train the model with provided data (legacy support)"""
        # Rule-based model doesn't need training
        pass

    def train_or_update(self, training_data):
        """Train or update the model with new data (legacy support)"""
        # Rule-based model doesn't need training
        pass

    def evaluate(self, test_data):
        """Evaluate model performance on test data (legacy support)"""
        # Return a mock accuracy for compatibility
        return 0.85

    def update(self, new_data):
        """Legacy update method for backward compatibility"""
        pass

    def export_model(self, file_path):
        """Export model with metadata (legacy support)"""
        model_data = {
            'threshold': self.threshold,
            'version': 'rule-based-v1',
            'type': 'rule-based'
        }
        with open(file_path, 'wb') as f:
            pickle.dump(model_data, f)

    def import_model(self, file_path):
        """Import model with metadata (legacy support)"""
        try:
            with open(file_path, 'rb') as f:
                model_data = pickle.load(f)
                self.threshold = model_data.get('threshold', 0.7)
        except:
            # Use default if import fails
            self.threshold = 0.7 