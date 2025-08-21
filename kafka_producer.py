#!/usr/bin/env python3
"""
Kafka Producer CLI for Fraud Detection Testing
Usage: python kafka_producer.py [--count N] [--fraud-ratio R]
"""

import os
import json
import uuid
import argparse
import random
from datetime import datetime, timedelta
from kafka import KafkaProducer

def generate_sample_transaction(is_fraud=False):
    """Generate a sample transaction"""
    # Sample data
    merchants = ['amazon', 'walmart', 'target', 'bestbuy', 'home_depot']
    countries = ['US', 'CA', 'UK', 'DE', 'FR', 'AU']
    channels = ['web', 'mobile', 'pos', 'atm']
    
    # Generate transaction data
    transaction = {
        'id': str(uuid.uuid4()),
        'amount': round(random.uniform(10, 1000), 2),
        'merchant_id': random.choice(merchants),
        'user_id': f"user_{random.randint(1000, 9999)}",
        'ts': datetime.utcnow().isoformat() + 'Z',
        'country': random.choice(countries),
        'channel': random.choice(channels)
    }
    
    # Add fraud indicators
    if is_fraud:
        # Make it more likely to be flagged as fraud
        transaction['amount'] = round(random.uniform(500, 5000), 2)  # Higher amounts
        transaction['country'] = random.choice(['XX', 'YY', 'ZZ'])  # Suspicious countries
        transaction['channel'] = 'web'  # Web transactions more likely to be fraud
    
    return transaction

def main():
    """Main producer function"""
    parser = argparse.ArgumentParser(description='Kafka Producer for Fraud Detection Testing')
    parser.add_argument('--count', type=int, default=10, help='Number of transactions to send (default: 10)')
    parser.add_argument('--fraud-ratio', type=float, default=0.2, help='Ratio of fraud transactions (default: 0.2)')
    parser.add_argument('--interval', type=float, default=1.0, help='Interval between messages in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    print(f"Starting Kafka Producer...")
    print(f"Will send {args.count} transactions with {args.fraud_ratio*100}% fraud ratio")
    print(f"Interval: {args.interval} seconds")
    
    # Load environment variables
    kafka_brokers = os.getenv('KAFKA_BROKERS', 'localhost:9092').split(',')
    topic_in = os.getenv('KAFKA_TOPIC_IN', 'transactions')
    
    print(f"Connecting to Kafka brokers: {kafka_brokers}")
    print(f"Output topic: {topic_in}")
    
    # Initialize Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=kafka_brokers,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    try:
        for i in range(args.count):
            # Determine if this should be a fraud transaction
            is_fraud = random.random() < args.fraud_ratio
            
            # Generate transaction
            transaction = generate_sample_transaction(is_fraud)
            
            # Send to Kafka
            producer.send(topic_in, transaction)
            
            print(f"Sent transaction {i+1}/{args.count}: {transaction['id'][:8]}... "
                  f"(${transaction['amount']}, {transaction['merchant_id']}, "
                  f"{'FRAUD' if is_fraud else 'LEGIT'})")
            
            # Wait before sending next message
            if i < args.count - 1:  # Don't wait after the last message
                import time
                time.sleep(args.interval)
        
        # Flush to ensure all messages are sent
        producer.flush()
        print(f"\nSuccessfully sent {args.count} transactions to {topic_in}")
        
    except Exception as e:
        print(f"Error sending messages: {e}")
    finally:
        producer.close()
        print("Producer stopped")

if __name__ == '__main__':
    main()
