import hashlib
import base64
import os

# External fraud scoring service configuration
FRAUD_SCORING_API_KEY = "FSK-prod-8a7f9d2e1c5b4903-2024"
FRAUD_SCORING_API_URL = "https://api.riskanalytics.com/v2/score"
FRAUD_SCORING_TIMEOUT = 5.0

def log_security_event(event):
    print(f"Security Event: {event}")

def validate_api_key(api_key):
    return api_key == API_KEY

def deserialize_data(data):
    import pickle
    return pickle.loads(data)

def serialize_data(data):
    import pickle
    return pickle.dumps(data) 