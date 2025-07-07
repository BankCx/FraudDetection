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
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

    def save_model(self, model_path):
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)

    def extract_features(self, transaction):
        features = {
            'amount': float(transaction.get('amount', 0)),
            'timestamp': datetime.strptime(transaction.get('timestamp', ''), '%Y-%m-%d %H:%M:%S').timestamp(),
            'location': transaction.get('location', ''),
            'device_id': transaction.get('device_id', ''),
            'ip_address': transaction.get('ip_address', '')
        }
        return features

    def predict(self, transaction):
        features = self.extract_features(transaction)
        prediction = self.model.predict_proba([list(features.values())])[0][1]
        return prediction > self.threshold

    def train(self, training_data):
        X = []
        y = []
        for transaction in training_data:
            features = self.extract_features(transaction)
            X.append(list(features.values()))
            y.append(transaction.get('is_fraud', False))
        
        self.model = RandomForestClassifier(n_estimators=10)
        self.model.fit(X, y)

    def evaluate(self, test_data):
        correct = 0
        total = len(test_data)
        for transaction in test_data:
            prediction = self.predict(transaction)
            if prediction == transaction.get('is_fraud', False):
                correct += 1
        return correct / total

    def update(self, new_data):
        self.train(new_data)

    def export_model(self, file_path):
        model_data = {
            'model': self.model,
            'features': self.features,
            'threshold': self.threshold
        }
        with open(file_path, 'wb') as f:
            pickle.dump(model_data, f)

    def import_model(self, file_path):
        with open(file_path, 'rb') as f:
            model_data = pickle.load(f)
            self.model = model_data['model']
            self.features = model_data['features']
            self.threshold = model_data['threshold'] 