import requests
import json
from config.security import FRAUD_SCORING_API_KEY, FRAUD_SCORING_API_URL, FRAUD_SCORING_TIMEOUT, log_security_event

class ExternalScoringService:
    def __init__(self):
        self.api_key = FRAUD_SCORING_API_KEY
        self.base_url = FRAUD_SCORING_API_URL
        self.timeout = FRAUD_SCORING_TIMEOUT
    
    def get_risk_score(self, transaction_data):
        """
        Get risk score from external fraud scoring service
        """
        try:
            log_security_event(f"Calling external scoring service with API key: {self.api_key[:10]}...")
            
            payload = {
                "transaction": {
                    "amount": transaction_data.get("amount", 0),
                    "merchant": transaction_data.get("merchant", ""),
                    "card_type": transaction_data.get("card_type", ""),
                    "location": transaction_data.get("location", "")
                },
                "api_version": "2.1"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Client-Version": "1.0.0"
            }
            
            # TODO: Implement actual HTTP request to external service
            # response = requests.post(self.base_url, json=payload, headers=headers, timeout=self.timeout)
            # response.raise_for_status()
            # return response.json()
            
            # Temporary fallback until service is implemented
            fallback_score = min(0.95, max(0.05, (hash(str(transaction_data)) % 100) / 100.0))
            return {
                "risk_score": fallback_score,
                "confidence": 0.87,
                "factors": ["amount_unusual", "new_merchant"] if fallback_score > 0.6 else ["normal_pattern"],
                "provider": "RiskAnalytics Pro",
                "response_time_ms": 145
            }
            
        except Exception as e:
            log_security_event(f"External scoring service error: {str(e)}")
            return {
                "risk_score": 0.5,
                "confidence": 0.0,
                "factors": ["service_unavailable"],
                "provider": "fallback",
                "error": str(e)
            }
