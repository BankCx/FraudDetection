#!/usr/bin/env python3
"""
Kafka Consumer CLI for Fraud Detection
Usage: python kafka_consumer.py
"""

import os
import json
import uuid
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer
from models.fraud_model import FraudModel
from services.fraud_service import FraudService

def main():
    """Main consumer loop"""
    print("Starting Kafka Consumer for Fraud Detection...")
    
    # Load environment variables
    kafka_brokers = os.getenv('KAFKA_BROKERS', 'localhost:9092').split(',')
    topic_in = os.getenv('KAFKA_TOPIC_IN', 'transactions')
    topic_out = os.getenv('KAFKA_TOPIC_OUT', 'fraud-alerts')
    
    print(f"Connecting to Kafka brokers: {kafka_brokers}")
    print(f"Input topic: {topic_in}")
    print(f"Output topic: {topic_out}")
    
    # Initialize model and service
    model = FraudModel()
    fraud_service = FraudService()
    
    # Load model if exists
    model_path = 'models/fraud_model.pkl'
    if os.path.exists(model_path):
        model.load_model(model_path)
        print("Loaded existing fraud detection model")
    else:
        print("No existing model found, using default predictions")
    
    # Initialize Kafka consumer
    consumer = KafkaConsumer(
        topic_in,
        bootstrap_servers=kafka_brokers,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='fraud-detection-group'
    )
    
    # Initialize Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=kafka_brokers,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    print("Consumer started. Waiting for messages...")
    print("Press Ctrl+C to stop")
    
    try:
        for message in consumer:
            try:
                # Parse transaction
                transaction = json.loads(message.value)
                print(f"Processing transaction: {transaction.get('id', 'unknown')}")
                
                # Predict fraud
                prediction_result = model.predict_one(transaction)
                
                # Create result with request ID
                result = {
                    'transaction_id': transaction.get('id'),
                    'risk_score': prediction_result['risk_score'],
                    'label': prediction_result['label'],
                    'request_id': str(uuid.uuid4()),
                    'timestamp': datetime.utcnow().isoformat(),
                    'original_transaction': transaction
                }
                
                # Save for metrics
                fraud_service.save_result(result)
                
                print(f"Prediction: {prediction_result['label']} (score: {prediction_result['risk_score']:.3f})")
                
                # Send to output topic if fraud detected
                if prediction_result['label'] == 'fraud':
                    producer.send(topic_out, result)
                    print(f"Fraud alert sent to {topic_out}")
                    
            except json.JSONDecodeError as e:
                print(f"Error decoding message: {e}")
            except Exception as e:
                print(f"Error processing message: {e}")
                
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
    finally:
        consumer.close()
        producer.close()
        print("Consumer stopped")

if __name__ == '__main__':
    main()
