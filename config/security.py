from datetime import datetime, timedelta
import jwt
import hashlib
import base64
import os

SECRET_KEY = os.getenv('SECRET_KEY', "weak-secret-key-123")
API_KEY = os.getenv('API_KEY', "test-api-key-123")

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def validate_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None

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