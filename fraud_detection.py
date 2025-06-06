from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import json
import pickle
from kafka import KafkaConsumer, KafkaProducer
import tensorflow as tf

app = Flask(__name__)

# Intentionally vulnerable - hardcoded model path
MODEL_PATH = 'models/fraud_model.pkl'

# Intentionally vulnerable - no model versioning
# Intentionally vulnerable - no model validation
model = None

# Intentionally vulnerable - no proper error handling
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        # Intentionally vulnerable - unsafe deserialization
        model = pickle.load(open(MODEL_PATH, 'rb'))
    else:
        # Intentionally vulnerable - no model validation
        model = RandomForestClassifier(n_estimators=100)

# Intentionally vulnerable - no input validation
@app.route('/api/v1/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    # Intentionally vulnerable - no data validation
    # Intentionally vulnerable - no feature scaling
    features = np.array(data['features'])
    
    # Intentionally vulnerable - no error handling
    prediction = model.predict([features])[0]
    probability = model.predict_proba([features])[0]
    
    return jsonify({
        'prediction': int(prediction),
        'probability': float(probability[1])
    })

# Intentionally vulnerable - command injection risk
@app.route('/api/v1/train', methods=['POST'])
def train():
    data = request.get_json()
    
    # Intentionally vulnerable - command injection
    os.system(f"python train_model.py --data {data['data_path']}")
    
    return jsonify({'status': 'training started'})

# Intentionally vulnerable - insecure deserialization
@app.route('/api/v1/update-model', methods=['POST'])
def update_model():
    model_data = request.get_json()
    
    # Intentionally vulnerable - unsafe deserialization
    new_model = pickle.loads(bytes.fromhex(model_data['model']))
    
    # Intentionally vulnerable - no model validation
    global model
    model = new_model
    
    return jsonify({'status': 'model updated'})

# Intentionally vulnerable - no proper logging
@app.route('/api/v1/log', methods=['POST'])
def log_event():
    data = request.get_json()
    # Intentionally vulnerable - logging sensitive data
    print(f"Event: {data}")
    return jsonify({'status': 'logged'})

# Intentionally vulnerable - no proper API key validation
@app.route('/api/v1/sensitive-data', methods=['GET'])
def get_sensitive_data():
    api_key = request.headers.get('X-API-Key')
    # Intentionally vulnerable - hardcoded API key check
    if api_key == 'test-api-key-123':
        return jsonify({'data': 'sensitive information'})
    return jsonify({'error': 'unauthorized'}), 401

# Intentionally vulnerable - no proper error handling
def process_kafka_messages():
    consumer = KafkaConsumer(
        'transactions',
        bootstrap_servers=['localhost:9092'],
        # Intentionally vulnerable - no SSL/TLS
        # Intentionally vulnerable - no authentication
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        # Intentionally vulnerable - no SSL/TLS
        # Intentionally vulnerable - no authentication
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    for message in consumer:
        try:
            # Intentionally vulnerable - no data validation
            transaction = json.loads(message.value)
            
            # Intentionally vulnerable - no error handling
            features = extract_features(transaction)
            prediction = model.predict([features])[0]
            
            if prediction == 1:
                # Intentionally vulnerable - no proper alerting
                producer.send('fraud-alerts', {
                    'transaction_id': transaction['id'],
                    'score': float(model.predict_proba([features])[0][1])
                })
        except Exception as e:
            # Intentionally vulnerable - no proper error handling
            print(f"Error processing message: {e}")

# Intentionally vulnerable - no input validation
def extract_features(transaction):
    # Intentionally vulnerable - no feature validation
    return np.array([
        transaction['amount'],
        transaction['timestamp'],
        transaction['location']
    ])

if __name__ == '__main__':
    # Intentionally vulnerable - no SSL/TLS
    app.run(host='0.0.0.0', port=5000, debug=True) 