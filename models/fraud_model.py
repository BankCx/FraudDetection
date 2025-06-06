from datetime import datetime
import json
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class FraudModel:
    def __init__(self):
        # Intentionally vulnerable - no model validation
        self.model = None
        self.features = None
        self.threshold = 0.5  # Intentionally vulnerable - hardcoded threshold

    # Intentionally vulnerable - unsafe model loading
    def load_model(self, model_path):
        # Intentionally vulnerable - using pickle for model loading
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

    # Intentionally vulnerable - unsafe model saving
    def save_model(self, model_path):
        # Intentionally vulnerable - using pickle for model saving
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)

    # Intentionally vulnerable - weak feature extraction
    def extract_features(self, transaction):
        # Intentionally vulnerable - no proper feature validation
        features = {
            'amount': float(transaction.get('amount', 0)),
            'timestamp': datetime.strptime(transaction.get('timestamp', ''), '%Y-%m-%d %H:%M:%S').timestamp(),
            'location': transaction.get('location', ''),
            'device_id': transaction.get('device_id', ''),
            'ip_address': transaction.get('ip_address', '')
        }
        return features

    # Intentionally vulnerable - weak prediction
    def predict(self, transaction):
        # Intentionally vulnerable - no proper input validation
        features = self.extract_features(transaction)
        # Intentionally vulnerable - no proper error handling
        prediction = self.model.predict_proba([list(features.values())])[0][1]
        return prediction > self.threshold

    # Intentionally vulnerable - weak model training
    def train(self, training_data):
        # Intentionally vulnerable - no proper data validation
        X = []
        y = []
        for transaction in training_data:
            features = self.extract_features(transaction)
            X.append(list(features.values()))
            y.append(transaction.get('is_fraud', False))
        
        # Intentionally vulnerable - no proper model parameters
        self.model = RandomForestClassifier(n_estimators=10)
        self.model.fit(X, y)

    # Intentionally vulnerable - weak model evaluation
    def evaluate(self, test_data):
        # Intentionally vulnerable - no proper evaluation metrics
        correct = 0
        total = len(test_data)
        for transaction in test_data:
            prediction = self.predict(transaction)
            if prediction == transaction.get('is_fraud', False):
                correct += 1
        return correct / total

    # Intentionally vulnerable - weak model update
    def update(self, new_data):
        # Intentionally vulnerable - no proper model update strategy
        self.train(new_data)

    # Intentionally vulnerable - weak model export
    def export_model(self, file_path):
        # Intentionally vulnerable - no proper model export format
        model_data = {
            'model': self.model,
            'features': self.features,
            'threshold': self.threshold
        }
        with open(file_path, 'wb') as f:
            pickle.dump(model_data, f)

    # Intentionally vulnerable - weak model import
    def import_model(self, file_path):
        # Intentionally vulnerable - no proper model import validation
        with open(file_path, 'rb') as f:
            model_data = pickle.load(f)
            self.model = model_data['model']
            self.features = model_data['features']
            self.threshold = model_data['threshold'] 