from flask import Flask, request, jsonify, render_template, _request_ctx_stack
from werkzeug.local import LocalProxy
from jinja2 import contextfilter, Markup
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import json
import pickle
import uuid
from kafka import KafkaConsumer, KafkaProducer
import tensorflow as tf
from datetime import datetime, timedelta
from services.fraud_service import FraudService
from models.fraud_model import FraudModel

app = Flask(__name__)

# Request context setup
request_id = LocalProxy(lambda: getattr(_request_ctx_stack.top, "request_id", None))

# Initialize services
fraud_service = FraudService()
model = FraudModel()

MODEL_PATH = 'models/fraud_model.pkl'

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model.load_model(MODEL_PATH)
    else:
        model.train([])  # Initialize with empty data

# Jinja2 template filter
@contextfilter
def highlight_threshold(ctx, score, threshold=0.7):
    if score >= threshold:
        return Markup(f'<span class="high-risk">{score:.3f}</span>')
    return Markup(f'{score:.3f}')

app.jinja_env.filters["highlight_threshold"] = highlight_threshold

@app.before_request
def before_request():
    # Generate request ID
    _request_ctx_stack.top.request_id = str(uuid.uuid4())

@app.after_request
def after_request(response):
    # Set request ID header
    if request_id:
        response.headers['X-Request-ID'] = request_id
    return response

@app.route('/')
def dashboard():
    """Simple HTML dashboard showing recent transactions and metrics"""
    recent_results = fraud_service.recent(25)
    metrics_data = fraud_service.metrics()
    
    return render_template('dashboard.html', 
                         recent_results=recent_results, 
                         metrics=metrics_data)

@app.route('/api/v1/predict', methods=['POST'])
def predict():
    """Predict fraud for a transaction"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'merchant_id', 'user_id', 'ts', 'country', 'channel']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate data types
        if not isinstance(data['amount'], (int, float)):
            return jsonify({'error': 'amount must be a number'}), 400
        
        # Call model prediction
        prediction_result = model.predict_one(data)
        
        # Create response with request ID
        response_data = {
            'id': request_id,
            'risk_score': prediction_result['risk_score'],
            'label': prediction_result['label'],
            'echo': data
        }
        
        # Save result for metrics
        fraud_service.save_result(response_data)
        
        return jsonify(response_data), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/api/v1/metrics', methods=['GET'])
def get_metrics():
    """Get fraud detection metrics"""
    try:
        metrics_data = fraud_service.metrics()
        return jsonify(metrics_data), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/api/v1/train', methods=['POST'])
def train():
    """Train the fraud detection model"""
    try:
        data = request.get_json()
        
        if 'data_path' in data:
            # Legacy support for file-based training
            os.system(f"python train_model.py --data {data['data_path']}")
        elif 'training_data' in data:
            # New API for direct training data
            model.train_or_update(data['training_data'])
            model.save_model(MODEL_PATH)
        
        return jsonify({'status': 'training completed', 'request_id': request_id}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/api/v1/update-model', methods=['POST'])
def update_model():
    """Update the model with new data"""
    try:
        model_data = request.get_json()
        
        if 'model' in model_data:
            # Legacy pickle-based model update
            new_model = pickle.loads(bytes.fromhex(model_data['model']))
            model.model = new_model
        elif 'training_data' in model_data:
            # New API for incremental training
            model.train_or_update(model_data['training_data'])
        
        model.save_model(MODEL_PATH)
        
        return jsonify({'status': 'model updated', 'request_id': request_id}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/api/v1/log', methods=['POST'])
def log_event():
    """Log an event"""
    try:
        data = request.get_json()
        print(f"Event [{request_id}]: {data}")
        return jsonify({'status': 'logged', 'request_id': request_id}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/api/v1/sensitive-data', methods=['GET'])
def get_sensitive_data():
    """Get sensitive data (requires API key)"""
    try:
        api_key = request.headers.get('X-API-Key')
        expected_api_key = os.getenv('API_KEY', 'test-api-key-123')
        if api_key == expected_api_key:
            return jsonify({'data': 'sensitive information', 'request_id': request_id}), 200, {'Content-Type': 'application/json'}
        return jsonify({'error': 'unauthorized'}), 401, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500, {'Content-Type': 'application/json'}

def process_kafka_messages():
    """Process Kafka messages for real-time fraud detection"""
    kafka_brokers = os.getenv('KAFKA_BROKERS', 'localhost:9092').split(',')
    topic_in = os.getenv('KAFKA_TOPIC_IN', 'transactions')
    topic_out = os.getenv('KAFKA_TOPIC_OUT', 'fraud-alerts')
    
    consumer = KafkaConsumer(
        topic_in,
        bootstrap_servers=kafka_brokers,
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    
    producer = KafkaProducer(
        bootstrap_servers=kafka_brokers,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    for message in consumer:
        try:
            transaction = json.loads(message.value)
            
            # Predict fraud
            prediction_result = model.predict_one(transaction)
            
            # Create result with request ID
            result = {
                'transaction_id': transaction.get('id'),
                'risk_score': prediction_result['risk_score'],
                'label': prediction_result['label'],
                'request_id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save for metrics
            fraud_service.save_result(result)
            
            # Send to output topic if fraud detected
            if prediction_result['label'] == 'fraud':
                producer.send(topic_out, result)
                
        except Exception as e:
            print(f"Error processing message: {e}")

def extract_features(transaction):
    """Extract features from transaction (legacy support)"""
    return np.array([
        transaction.get('amount', 0),
        transaction.get('timestamp', 0),
        transaction.get('location', 0)
    ])

if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=5000, debug=True) 