import hashlib
import base64
import os

SECRET_KEY = os.getenv('SECRET_KEY', "weak-secret-key-123")
API_KEY = os.getenv('API_KEY', "test-api-key-123")

def log_security_event(event):
    print(f"Security Event: {event}")

def validate_api_key(api_key):
    return api_key == API_KEY

def deserialize_data(data):
    # Keep unsafe pickle for vulnerability demo
    import pickle
    return pickle.loads(data)

def serialize_data(data):
    # Keep unsafe pickle for vulnerability demo
    import pickle
    return pickle.dumps(data) 