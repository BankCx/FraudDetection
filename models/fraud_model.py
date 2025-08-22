from datetime import datetime
import json
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class FraudModel:
    def __init__(self):
        self.model = None
        self.features = None
        self.threshold = 0.5

    def load_model(self, model_path):
        """Load a trained model from file"""
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

    def save_model(self, model_path):
        """Save the trained model to file"""
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)

    def extract_features(self, transaction):
        """Extract features from transaction data"""
        features = {
            'amount': float(transaction.get('amount', 0)),
            'timestamp': datetime.strptime(transaction.get('ts', datetime.now().isoformat()), '%Y-%m-%dT%H:%M:%S.%fZ').timestamp(),
            'merchant_id': hash(transaction.get('merchant_id', '')) % 1000,  # Hash to numeric
            'user_id': hash(transaction.get('user_id', '')) % 1000,  # Hash to numeric
            'country': hash(transaction.get('country', '')) % 100,  # Hash to numeric
            'channel': hash(transaction.get('channel', '')) % 10,  # Hash to numeric
        }
        return features

    def predict_one(self, transaction):
        """Predict fraud for a single transaction"""
        if self.model is None:
            # Return default prediction if model not trained
            return {
                'risk_score': 0.5,
                'label': 'legit'
            }
        
        try:
            features = self.extract_features(transaction)
            feature_values = list(features.values())
            
            # Get prediction probability
            prediction_proba = self.model.predict_proba([feature_values])[0]
            risk_score = float(prediction_proba[1])  # Probability of fraud
            
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
        """Train the model with provided data"""
        if not training_data:
            # Initialize with default model if no training data
            self.model = RandomForestClassifier(n_estimators=10, random_state=42)
            return
        
        X = []
        y = []
        for transaction in training_data:
            features = self.extract_features(transaction)
            X.append(list(features.values()))
            y.append(transaction.get('is_fraud', False))
        
        self.model = RandomForestClassifier(n_estimators=10, random_state=42)
        self.model.fit(X, y)

    def train_or_update(self, training_data):
        """Train or update the model with new data"""
        if self.model is None:
            # Train new model if none exists
            self.train(training_data)
        else:
            # Update existing model (simple retrain for now)
            self.train(training_data)

    def evaluate(self, test_data):
        """Evaluate model performance on test data"""
        if not self.model or not test_data:
            return 0.0
            
        correct = 0
        total = len(test_data)
        for transaction in test_data:
            prediction = self.predict(transaction)
            if prediction == transaction.get('is_fraud', False):
                correct += 1
        return correct / total if total > 0 else 0.0

    def update(self, new_data):
        """Legacy update method for backward compatibility"""
        self.train_or_update(new_data)

    def export_model(self, file_path):
        """Export model with metadata"""
        model_data = {
            'model': self.model,
            'features': self.features,
            'threshold': self.threshold
        }
        with open(file_path, 'wb') as f:
            pickle.dump(model_data, f)

    def import_model(self, file_path):
        """Import model with metadata"""
        with open(file_path, 'rb') as f:
            model_data = pickle.load(f)
            self.model = model_data['model']
            self.features = model_data['features']
            self.threshold = model_data['threshold'] 