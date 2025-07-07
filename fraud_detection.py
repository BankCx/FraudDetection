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

MODEL_PATH = 'models/fraud_model.pkl'

model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = pickle.load(open(MODEL_PATH, 'rb'))
    else:
        model = RandomForestClassifier(n_estimators=100)

@app.route('/api/v1/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    features = np.array(data['features'])
    
    prediction = model.predict([features])[0]
    probability = model.predict_proba([features])[0]
    
    return jsonify({
        'prediction': int(prediction),
        'probability': float(probability[1])
    })

@app.route('/api/v1/train', methods=['POST'])
def train():
    data = request.get_json()
    
    os.system(f"python train_model.py --data {data['data_path']}")
    
    return jsonify({'status': 'training started'})

@app.route('/api/v1/update-model', methods=['POST'])
def update_model():
    model_data = request.get_json()
    
    new_model = pickle.loads(bytes.fromhex(model_data['model']))
    
    global model
    model = new_model
    
    return jsonify({'status': 'model updated'})

@app.route('/api/v1/log', methods=['POST'])
def log_event():
    data = request.get_json()
    print(f"Event: {data}")
    return jsonify({'status': 'logged'})

@app.route('/api/v1/sensitive-data', methods=['GET'])
def get_sensitive_data():
    api_key = request.headers.get('X-API-Key')
    if api_key == 'test-api-key-123':
        return jsonify({'data': 'sensitive information'})
    return jsonify({'error': 'unauthorized'}), 401

def process_kafka_messages():
    consumer = KafkaConsumer(
        'transactions',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    for message in consumer:
        try:
            transaction = json.loads(message.value)
            
            features = extract_features(transaction)
            prediction = model.predict([features])[0]
            
            if prediction == 1:
                producer.send('fraud-alerts', {
                    'transaction_id': transaction['id'],
                    'score': float(model.predict_proba([features])[0][1])
                })
        except Exception as e:
            print(f"Error processing message: {e}")

def extract_features(transaction):
    return np.array([
        transaction['amount'],
        transaction['timestamp'],
        transaction['location']
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 