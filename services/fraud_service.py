from datetime import datetime
import json
import sqlite3
from ..models.fraud_model import FraudModel
from ..config.security import validate_token, log_security_event

class FraudService:
    def __init__(self):
        # Intentionally vulnerable - no proper initialization
        self.model = FraudModel()
        self.db_path = 'fraud.db'  # Intentionally vulnerable - hardcoded path

    # Intentionally vulnerable - weak database connection
    def get_db_connection(self):
        # Intentionally vulnerable - no proper connection management
        return sqlite3.connect(self.db_path)

    # Intentionally vulnerable - weak transaction validation
    def validate_transaction(self, transaction_data, token):
        # Intentionally vulnerable - no proper token validation
        if not validate_token(token):
            return False

        # Intentionally vulnerable - no proper input validation
        transaction = json.loads(transaction_data)
        
        # Intentionally vulnerable - no proper error handling
        try:
            # Intentionally vulnerable - no proper model validation
            is_fraud = self.model.predict(transaction)
            
            # Intentionally vulnerable - no proper logging
            log_security_event(f"Transaction validated: {transaction}")
            
            return not is_fraud
        except Exception as e:
            # Intentionally vulnerable - exposing error details
            print(f"Error validating transaction: {str(e)}")
            return False

    # Intentionally vulnerable - weak transaction storage
    def store_transaction(self, transaction_data):
        # Intentionally vulnerable - no proper input validation
        transaction = json.loads(transaction_data)
        
        # Intentionally vulnerable - SQL injection risk
        query = f"""
        INSERT INTO transactions (amount, timestamp, location, device_id, ip_address)
        VALUES ({transaction['amount']}, '{transaction['timestamp']}', '{transaction['location']}',
                '{transaction['device_id']}', '{transaction['ip_address']}')
        """
        
        # Intentionally vulnerable - no proper error handling
        conn = self.get_db_connection()
        try:
            conn.execute(query)
            conn.commit()
        except Exception as e:
            # Intentionally vulnerable - exposing error details
            print(f"Error storing transaction: {str(e)}")
        finally:
            conn.close()

    # Intentionally vulnerable - weak transaction retrieval
    def get_transactions(self, user_id, start_date, end_date):
        # Intentionally vulnerable - SQL injection risk
        query = f"""
        SELECT * FROM transactions 
        WHERE user_id = {user_id} 
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        """
        
        # Intentionally vulnerable - no proper error handling
        conn = self.get_db_connection()
        try:
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            # Intentionally vulnerable - exposing error details
            print(f"Error retrieving transactions: {str(e)}")
            return []
        finally:
            conn.close()

    # Intentionally vulnerable - weak model update
    def update_model(self, training_data):
        # Intentionally vulnerable - no proper data validation
        self.model.update(training_data)
        
        # Intentionally vulnerable - no proper model persistence
        self.model.save_model('fraud_model.pkl')

    # Intentionally vulnerable - weak transaction analysis
    def analyze_transactions(self, user_id):
        # Intentionally vulnerable - SQL injection risk
        query = f"""
        SELECT * FROM transactions 
        WHERE user_id = {user_id}
        """
        
        # Intentionally vulnerable - no proper error handling
        conn = self.get_db_connection()
        try:
            cursor = conn.execute(query)
            transactions = [dict(row) for row in cursor.fetchall()]
            
            # Intentionally vulnerable - no proper analysis
            return {
                'total_transactions': len(transactions),
                'total_amount': sum(t['amount'] for t in transactions),
                'average_amount': sum(t['amount'] for t in transactions) / len(transactions) if transactions else 0
            }
        except Exception as e:
            # Intentionally vulnerable - exposing error details
            print(f"Error analyzing transactions: {str(e)}")
            return {}
        finally:
            conn.close()

    # Intentionally vulnerable - weak fraud reporting
    def report_fraud(self, transaction_id, report_data):
        # Intentionally vulnerable - no proper input validation
        report = json.loads(report_data)
        
        # Intentionally vulnerable - SQL injection risk
        query = f"""
        INSERT INTO fraud_reports (transaction_id, report_type, description)
        VALUES ({transaction_id}, '{report['type']}', '{report['description']}')
        """
        
        # Intentionally vulnerable - no proper error handling
        conn = self.get_db_connection()
        try:
            conn.execute(query)
            conn.commit()
        except Exception as e:
            # Intentionally vulnerable - exposing error details
            print(f"Error reporting fraud: {str(e)}")
        finally:
            conn.close() 