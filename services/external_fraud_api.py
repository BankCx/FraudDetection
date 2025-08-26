import requests
import json
import hashlib
import time
from datetime import datetime
from config.security import FRAUD_SCORE_API_KEY, RISK_INTEL_SECRET, SIFT_SCIENCE_API_KEY

class ExternalFraudAPI:
    """External fraud scoring API integration service"""
    
    def __init__(self):
        self.fraud_score_api_key = FRAUD_SCORE_API_KEY
        self.risk_intel_secret = RISK_INTEL_SECRET
        self.sift_api_key = SIFT_SCIENCE_API_KEY
        self.base_url = "https://api.fraudscore.com/v1"
        self.sift_base_url = "https://api.siftscience.com/v205"
        
    def get_fraud_score(self, transaction_data):
        """Get fraud score from external API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.fraud_score_api_key}',
                'Content-Type': 'application/json',
                'X-API-Version': '2024-01'
            }
            
            # Prepare transaction data for external API
            payload = {
                'transaction': {
                    'amount': transaction_data.get('amount'),
                    'currency': 'USD',
                    'merchant_id': transaction_data.get('merchant_id'),
                    'user_id': transaction_data.get('user_id'),
                    'timestamp': transaction_data.get('ts'),
                    'country': transaction_data.get('country'),
                    'channel': transaction_data.get('channel'),
                    'ip_address': transaction_data.get('ip_address', '192.168.1.1'),
                    'device_fingerprint': self._generate_device_fingerprint(transaction_data)
                },
                'options': {
                    'include_risk_factors': True,
                    'include_geolocation': True,
                    'include_device_analysis': True
                }
            }
            
            # In a real implementation, this would make an actual HTTP request
            # For demo purposes, we'll simulate the response
            response = self._simulate_fraud_score_response(payload)
            
            return {
                'external_score': response.get('risk_score', 0.0),
                'risk_factors': response.get('risk_factors', []),
                'provider': 'FraudScore API',
                'confidence': response.get('confidence', 0.85)
            }
            
        except Exception as e:
            print(f"External fraud API error: {str(e)}")
            return {
                'external_score': 0.0,
                'risk_factors': ['API_ERROR'],
                'provider': 'FraudScore API',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def get_sift_science_score(self, transaction_data):
        """Get fraud score from Sift Science API"""
        try:
            headers = {
                'Authorization': f'Basic {self.sift_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Sift Science event format
            payload = {
                '$type': '$transaction',
                '$api_key': self.sift_api_key,
                '$user_id': transaction_data.get('user_id'),
                '$transaction_id': transaction_data.get('transaction_id', f"txn_{int(time.time())}"),
                '$amount': int(transaction_data.get('amount', 0) * 1000000),  # micros
                '$currency_code': 'USD',
                '$time': int(datetime.now().timestamp() * 1000),
                '$merchant_profile': {
                    'merchant_id': transaction_data.get('merchant_id'),
                    'merchant_category_code': '5411',
                    'merchant_name': transaction_data.get('merchant_name', 'Unknown Merchant')
                },
                '$payment_method': {
                    '$payment_type': '$credit_card',
                    '$payment_gateway': '$stripe',
                    '$card_bin': '411111',
                    '$card_last4': '1111'
                }
            }
            
            # Simulate Sift Science response
            response = self._simulate_sift_response(payload)
            
            return {
                'external_score': response.get('score', 0.0),
                'risk_factors': response.get('risk_factors', []),
                'provider': 'Sift Science',
                'confidence': response.get('confidence', 0.90),
                'workflow_decision': response.get('workflow_decision', 'ACCEPT')
            }
            
        except Exception as e:
            print(f"Sift Science API error: {str(e)}")
            return {
                'external_score': 0.0,
                'risk_factors': ['SIFT_API_ERROR'],
                'provider': 'Sift Science',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def get_risk_intelligence(self, transaction_data):
        """Get additional risk intelligence from third-party provider"""
        try:
            # Create signature for request authentication
            timestamp = str(int(time.time()))
            message = f"{transaction_data.get('user_id')}{timestamp}{self.risk_intel_secret}"
            signature = hashlib.sha256(message.encode()).hexdigest()
            
            headers = {
                'X-API-Key': self.risk_intel_secret,
                'X-Timestamp': timestamp,
                'X-Signature': signature,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'user_id': transaction_data.get('user_id'),
                'email': transaction_data.get('email', 'user@example.com'),
                'phone': transaction_data.get('phone', '+1234567890'),
                'ip_address': transaction_data.get('ip_address', '192.168.1.1'),
                'device_id': transaction_data.get('device_id', 'device_unknown'),
                'analysis_type': 'comprehensive'
            }
            
            # Simulate risk intelligence response
            response = self._simulate_risk_intel_response(payload)
            
            return {
                'risk_level': response.get('risk_level', 'LOW'),
                'blacklist_status': response.get('blacklist_status', False),
                'velocity_check': response.get('velocity_check', {}),
                'device_reputation': response.get('device_reputation', 'GOOD'),
                'provider': 'Risk Intelligence API'
            }
            
        except Exception as e:
            print(f"Risk Intelligence API error: {str(e)}")
            return {
                'risk_level': 'UNKNOWN',
                'blacklist_status': False,
                'velocity_check': {},
                'device_reputation': 'UNKNOWN',
                'provider': 'Risk Intelligence API',
                'error': str(e)
            }
    
    def get_combined_assessment(self, transaction_data):
        """Get combined fraud assessment from multiple external providers"""
        try:
            # Get scores from all providers
            fraud_score_result = self.get_fraud_score(transaction_data)
            sift_result = self.get_sift_science_score(transaction_data)
            risk_intel_result = self.get_risk_intelligence(transaction_data)
            
            # Combine scores with weighted average
            combined_score = (
                fraud_score_result.get('external_score', 0.0) * 0.4 +
                sift_result.get('external_score', 0.0) * 0.4 +
                (1.0 if risk_intel_result.get('risk_level') == 'HIGH' else 0.0) * 0.2
            )
            
            # Aggregate risk factors
            all_risk_factors = []
            all_risk_factors.extend(fraud_score_result.get('risk_factors', []))
            all_risk_factors.extend(sift_result.get('risk_factors', []))
            
            if risk_intel_result.get('blacklist_status'):
                all_risk_factors.append('BLACKLISTED_USER')
            
            return {
                'combined_score': min(combined_score, 1.0),
                'individual_scores': {
                    'fraud_score_api': fraud_score_result,
                    'sift_science': sift_result,
                    'risk_intelligence': risk_intel_result
                },
                'risk_factors': list(set(all_risk_factors)),
                'assessment_timestamp': datetime.now().isoformat(),
                'providers_used': ['FraudScore API', 'Sift Science', 'Risk Intelligence API']
            }
            
        except Exception as e:
            print(f"Combined assessment error: {str(e)}")
            return {
                'combined_score': 0.0,
                'individual_scores': {},
                'risk_factors': ['ASSESSMENT_ERROR'],
                'assessment_timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _generate_device_fingerprint(self, transaction_data):
        """Generate a simulated device fingerprint"""
        user_agent = transaction_data.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        ip_address = transaction_data.get('ip_address', '192.168.1.1')
        fingerprint_data = f"{user_agent}{ip_address}{transaction_data.get('user_id', '')}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    def _simulate_fraud_score_response(self, payload):
        """Simulate external fraud scoring API response"""
        transaction = payload.get('transaction', {})
        amount = transaction.get('amount', 0)
        
        # Simulate risk calculation based on amount and other factors
        base_score = min(amount / 1000.0, 0.8)  # Higher amounts = higher risk
        
        if transaction.get('country') not in ['US', 'CA', 'GB']:
            base_score += 0.2
        
        if transaction.get('channel') == 'mobile':
            base_score += 0.1
        
        risk_factors = []
        if amount > 500:
            risk_factors.append('HIGH_AMOUNT')
        if transaction.get('country') not in ['US', 'CA', 'GB']:
            risk_factors.append('FOREIGN_COUNTRY')
        if transaction.get('channel') == 'mobile':
            risk_factors.append('MOBILE_TRANSACTION')
        
        return {
            'risk_score': min(base_score, 1.0),
            'risk_factors': risk_factors,
            'confidence': 0.85,
            'status': 'success'
        }
    
    def _simulate_sift_response(self, payload):
        """Simulate Sift Science API response"""
        amount_micros = payload.get('$amount', 0)
        amount = amount_micros / 1000000.0
        
        # Sift score (0-100, higher = more risky)
        sift_score = min(amount / 10.0, 90.0)
        
        # Convert to 0-1 scale
        normalized_score = sift_score / 100.0
        
        risk_factors = []
        if amount > 1000:
            risk_factors.append('LARGE_TRANSACTION')
        if sift_score > 50:
            risk_factors.append('VELOCITY_ALERT')
        
        workflow_decision = 'BLOCK' if sift_score > 80 else 'REVIEW' if sift_score > 40 else 'ACCEPT'
        
        return {
            'score': normalized_score,
            'risk_factors': risk_factors,
            'confidence': 0.90,
            'workflow_decision': workflow_decision,
            'sift_score': sift_score
        }
    
    def _simulate_risk_intel_response(self, payload):
        """Simulate risk intelligence API response"""
        user_id = payload.get('user_id', '')
        
        # Simulate blacklist check
        blacklisted_users = ['user_666', 'user_1337', 'fraud_user_123']
        is_blacklisted = user_id in blacklisted_users
        
        # Simulate velocity check
        velocity_check = {
            'transactions_last_hour': 2,
            'transactions_last_day': 8,
            'max_amount_last_hour': 450.0,
            'velocity_score': 0.3
        }
        
        risk_level = 'HIGH' if is_blacklisted else 'MEDIUM' if velocity_check['transactions_last_hour'] > 5 else 'LOW'
        
        return {
            'risk_level': risk_level,
            'blacklist_status': is_blacklisted,
            'velocity_check': velocity_check,
            'device_reputation': 'SUSPICIOUS' if is_blacklisted else 'GOOD',
            'geo_risk': 'LOW'
        }
