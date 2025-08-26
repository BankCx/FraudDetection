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
from datetime import datetime, timedelta
from services.fraud_service import FraudService
from models.fraud_model import FraudModel
from services.external_fraud_api import ExternalFraudAPI
from services.notification_service import NotificationService

app = Flask(__name__)

# Request context setup
request_id = LocalProxy(lambda: getattr(_request_ctx_stack.top, "request_id", None))

# Initialize services
fraud_service = FraudService()
model = FraudModel()
external_fraud_api = ExternalFraudAPI()
notification_service = NotificationService()

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
        
        # Call internal model prediction
        prediction_result = model.predict_one(data)
        
        # Get external fraud assessment for enhanced accuracy
        external_assessment = external_fraud_api.get_combined_assessment(data)
        
        # Combine internal and external scores
        internal_score = prediction_result['risk_score']
        external_score = external_assessment.get('combined_score', 0.0)
        combined_score = (internal_score * 0.6) + (external_score * 0.4)
        
        # Determine final label based on combined score
        final_label = 'fraud' if combined_score > 0.7 else 'review' if combined_score > 0.4 else 'legit'
        
        # Create enhanced response with external data
        response_data = {
            'id': request_id,
            'risk_score': combined_score,
            'internal_score': internal_score,
            'external_score': external_score,
            'label': final_label,
            'external_assessment': external_assessment,
            'echo': data
        }
        
        # Save result for metrics
        fraud_service.save_result(response_data)
        
        # Send automatic notifications for high-risk transactions
        if combined_score > 0.7:
            alert_config = {
                'sms_enabled': True,
                'phone_numbers': ['+1234567890'],  # Security team phone
                'email_enabled': True,
                'email_addresses': ['security@bankofcheckmarx.com', 'fraud-team@bankofcheckmarx.com'],
                'slack_enabled': True,
                'slack_channels': ['#fraud-alerts', '#security-team']
            }
            
            notification_result = notification_service.send_comprehensive_alert(
                alert_config, data, combined_score, external_assessment
            )
            response_data['notifications'] = notification_result
        
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

@app.route('/api/v1/external-assessment', methods=['POST'])
def get_external_assessment():
    """Get external fraud assessment for a transaction"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'merchant_id', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get external assessment
        assessment = external_fraud_api.get_combined_assessment(data)
        
        response_data = {
            'request_id': request_id,
            'assessment': assessment,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/api/v1/send-alert', methods=['POST'])
def send_manual_alert():
    """Manually send fraud alert notifications"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['transaction_data', 'risk_score', 'alert_config']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Send notifications
        notification_result = notification_service.send_comprehensive_alert(
            data['alert_config'],
            data['transaction_data'],
            data['risk_score'],
            data.get('external_assessment')
        )
        
        response_data = {
            'request_id': request_id,
            'notification_result': notification_result,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/api/v1/fraud-providers', methods=['GET'])
def get_fraud_providers():
    """Get status and configuration of external fraud providers"""
    try:
        provider_status = {
            'fraud_score_api': {
                'name': 'FraudScore API',
                'status': 'active',
                'api_key_configured': bool(external_fraud_api.fraud_score_api_key),
                'last_checked': datetime.now().isoformat()
            },
            'sift_science': {
                'name': 'Sift Science',
                'status': 'active',
                'api_key_configured': bool(external_fraud_api.sift_api_key),
                'last_checked': datetime.now().isoformat()
            },
            'risk_intelligence': {
                'name': 'Risk Intelligence API',
                'status': 'active',
                'secret_configured': bool(external_fraud_api.risk_intel_secret),
                'last_checked': datetime.now().isoformat()
            }
        }
        
        return jsonify({
            'request_id': request_id,
            'providers': provider_status,
            'total_providers': len(provider_status),
            'active_providers': sum(1 for p in provider_status.values() if p['status'] == 'active')
        }), 200, {'Content-Type': 'application/json'}
        
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
            
            # Get internal prediction
            prediction_result = model.predict_one(transaction)
            
            # Get external assessment for enhanced accuracy
            external_assessment = external_fraud_api.get_combined_assessment(transaction)
            
            # Combine scores
            internal_score = prediction_result['risk_score']
            external_score = external_assessment.get('combined_score', 0.0)
            combined_score = (internal_score * 0.6) + (external_score * 0.4)
            
            # Determine final label
            final_label = 'fraud' if combined_score > 0.7 else 'review' if combined_score > 0.4 else 'legit'
            
            # Create enhanced result
            result = {
                'transaction_id': transaction.get('id'),
                'risk_score': combined_score,
                'internal_score': internal_score,
                'external_score': external_score,
                'label': final_label,
                'external_assessment': external_assessment,
                'request_id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save for metrics
            fraud_service.save_result(result)
            
            # Send to output topic and trigger alerts for high-risk transactions
            if combined_score > 0.7:
                producer.send(topic_out, result)
                
                # Auto-send notifications for high-risk Kafka transactions
                alert_config = {
                    'sms_enabled': False,  # Disable SMS for Kafka to avoid spam
                    'email_enabled': True,
                    'email_addresses': ['kafka-fraud@bankofcheckmarx.com'],
                    'slack_enabled': True,
                    'slack_channels': ['#kafka-fraud-alerts']
                }
                
                notification_service.send_comprehensive_alert(
                    alert_config, transaction, combined_score, external_assessment
                )
                
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