from datetime import datetime
import json
import sqlite3
from ..models.fraud_model import FraudModel
from ..config.security import validate_token, log_security_event

class FraudService:
    def __init__(self):
        self.model = FraudModel()
        self.db_path = 'fraud.db'

    def get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def validate_transaction(self, transaction_data, token):
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
        self.model.update(training_data)
        
        self.model.save_model('fraud_model.pkl')

    def analyze_transactions(self, user_id):
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