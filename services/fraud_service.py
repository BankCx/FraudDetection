from datetime import datetime, timedelta
import json
import sqlite3
from collections import deque
from models.fraud_model import FraudModel
from config.security import validate_token, log_security_event

class FraudService:
    def __init__(self):
        self.model = FraudModel()
        self.db_path = 'fraud.db'
        # In-memory storage for recent results and metrics
        self.recent_results = deque(maxlen=1000)  # Keep last 1000 results
        self.metrics_cache = {
            'total': 0,
            'fraud_count': 0,
            'last_hour_count': 0,
            'last_hour_fraud_count': 0,
            'last_update': datetime.now()
        }

    def get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def save_result(self, result):
        """Save a prediction result for metrics tracking"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in result:
                result['timestamp'] = datetime.now().isoformat()
            
            # Add to recent results
            self.recent_results.append(result)
            
            # Update metrics
            self.metrics_cache['total'] += 1
            if result.get('label') == 'fraud':
                self.metrics_cache['fraud_count'] += 1
            
            # Update last hour metrics
            self._update_last_hour_metrics()
            
            # Log security event
            log_security_event(f"Result saved: {result.get('id', 'unknown')} - {result.get('label', 'unknown')}")
            
        except Exception as e:
            print(f"Error saving result: {str(e)}")

    def recent(self, n=25):
        """Get the most recent n prediction results"""
        try:
            # Return the last n results from the deque
            return list(self.recent_results)[-n:]
        except Exception as e:
            print(f"Error retrieving recent results: {str(e)}")
            return []

    def metrics(self):
        """Get fraud detection metrics"""
        try:
            # Update last hour metrics
            self._update_last_hour_metrics()
            
            total = self.metrics_cache['total']
            fraud_count = self.metrics_cache['fraud_count']
            
            return {
                'total': total,
                'fraud_rate': fraud_count / total if total > 0 else 0.0,
                'last_hour_avg': self.metrics_cache['last_hour_count'] / 60.0,  # Average per minute
                'last_hour_fraud_rate': self.metrics_cache['last_hour_fraud_count'] / max(self.metrics_cache['last_hour_count'], 1),
                'last_update': self.metrics_cache['last_update'].isoformat()
            }
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            return {
                'total': 0,
                'fraud_rate': 0.0,
                'last_hour_avg': 0.0,
                'last_hour_fraud_rate': 0.0,
                'last_update': datetime.now().isoformat()
            }

    def _update_last_hour_metrics(self):
        """Update last hour metrics"""
        try:
            now = datetime.now()
            one_hour_ago = now - timedelta(hours=1)
            
            # Count transactions in last hour
            last_hour_count = 0
            last_hour_fraud_count = 0
            
            for result in self.recent_results:
                try:
                    result_time = datetime.fromisoformat(result.get('timestamp', ''))
                    if result_time >= one_hour_ago:
                        last_hour_count += 1
                        if result.get('label') == 'fraud':
                            last_hour_fraud_count += 1
                except:
                    continue
            
            self.metrics_cache['last_hour_count'] = last_hour_count
            self.metrics_cache['last_hour_fraud_count'] = last_hour_fraud_count
            self.metrics_cache['last_update'] = now
            
        except Exception as e:
            print(f"Error updating last hour metrics: {str(e)}")

    def validate_transaction(self, transaction_data, token):
        """Validate a transaction (legacy method)"""
        if not validate_token(token):
            return False

        transaction = json.loads(transaction_data)
        
        try:
            is_fraud = self.model.predict(transaction)
            
            log_security_event(f"Transaction validated: {transaction}")
            
            return not is_fraud
        except Exception as e:
            print(f"Error validating transaction: {str(e)}")
            return False

    def store_transaction(self, transaction_data):
        """Store a transaction in the database (legacy method)"""
        transaction = json.loads(transaction_data)
        
        query = f"""
        INSERT INTO transactions (amount, timestamp, location, device_id, ip_address)
        VALUES ({transaction['amount']}, '{transaction['timestamp']}', '{transaction['location']}',
                '{transaction['device_id']}', '{transaction['ip_address']}')
        """
        
        conn = self.get_db_connection()
        try:
            conn.execute(query)
            conn.commit()
        except Exception as e:
            print(f"Error storing transaction: {str(e)}")
        finally:
            conn.close()

    def get_transactions(self, user_id, start_date, end_date):
        """Get transactions for a user (legacy method)"""
        query = f"""
        SELECT * FROM transactions 
        WHERE user_id = {user_id} 
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        """
        
        conn = self.get_db_connection()
        try:
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error retrieving transactions: {str(e)}")
            return []
        finally:
            conn.close()

    def update_model(self, training_data):
        """Update the fraud detection model (legacy method)"""
        self.model.update(training_data)
        self.model.save_model('fraud_model.pkl')

    def analyze_transactions(self, user_id):
        """Analyze transactions for a user (legacy method)"""
        query = f"""
        SELECT * FROM transactions 
        WHERE user_id = {user_id}
        """
        
        conn = self.get_db_connection()
        try:
            cursor = conn.execute(query)
            transactions = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total_transactions': len(transactions),
                'total_amount': sum(t['amount'] for t in transactions),
                'average_amount': sum(t['amount'] for t in transactions) / len(transactions) if transactions else 0
            }
        except Exception as e:
            print(f"Error analyzing transactions: {str(e)}")
            return {}
        finally:
            conn.close()

    def report_fraud(self, transaction_id, report_data):
        """Report fraud for a transaction (legacy method)"""
        report = json.loads(report_data)
        
        query = f"""
        INSERT INTO fraud_reports (transaction_id, report_type, description)
        VALUES ({transaction_id}, '{report['type']}', '{report['description']}')
        """
        
        conn = self.get_db_connection()
        try:
            conn.execute(query)
            conn.commit()
        except Exception as e:
            print(f"Error reporting fraud: {str(e)}")
        finally:
            conn.close() 