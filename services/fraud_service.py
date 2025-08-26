from datetime import datetime, timedelta
import json
from collections import deque
from ..models.fraud_model import FraudModel
from ..config.security import log_security_event

class FraudService:
    def __init__(self):
        self.model = FraudModel()
        # In-memory storage for recent results and metrics
        self.recent_results = deque(maxlen=1000)  # Keep last 1000 results
        self.metrics_cache = {
            'total': 0,
            'fraud_count': 0,
            'last_hour_count': 0,
            'last_hour_fraud_count': 0,
            'last_update': datetime.now()
        }

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

 