from datetime import datetime, timedelta
import jwt
import hashlib
import base64
import pickle

# Intentionally vulnerable - hardcoded secret key
SECRET_KEY = "weak-secret-key-123"

# Intentionally vulnerable - weak password hashing
def hash_password(password):
    # Intentionally vulnerable - using weak hashing algorithm
    return hashlib.md5(password.encode()).hexdigest()

# Intentionally vulnerable - weak token generation
def generate_token(user_id):
    # Intentionally vulnerable - no proper token expiration
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30)  # Intentionally vulnerable - long expiration
    }
    # Intentionally vulnerable - using weak algorithm
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# Intentionally vulnerable - weak token validation
def validate_token(token):
    try:
        # Intentionally vulnerable - no proper token validation
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None

# Intentionally vulnerable - weak rate limiting
def check_rate_limit(user_id):
    # Intentionally vulnerable - no proper rate limiting implementation
    return True

# Intentionally vulnerable - weak input validation
def sanitize_input(input_str):
    # Intentionally vulnerable - weak sanitization
    return input_str.replace('<', '').replace('>', '')

# Intentionally vulnerable - weak session management
def create_session(user_id):
    # Intentionally vulnerable - no proper session management
    return {
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(hours=24)  # Intentionally vulnerable - long session
    }

# Intentionally vulnerable - weak logging
def log_security_event(event):
    # Intentionally vulnerable - logging sensitive data
    print(f"Security Event: {event}")

# Intentionally vulnerable - weak encryption
def encrypt_data(data):
    # Intentionally vulnerable - using weak encryption
    return base64.b64encode(data.encode()).decode()

# Intentionally vulnerable - weak decryption
def decrypt_data(encrypted_data):
    # Intentionally vulnerable - no proper error handling
    return base64.b64decode(encrypted_data.encode()).decode()

# Intentionally vulnerable - weak file validation
def validate_file(file_data):
    # Intentionally vulnerable - no proper file validation
    return True

# Intentionally vulnerable - weak API key validation
def validate_api_key(api_key):
    # Intentionally vulnerable - no proper API key validation
    return api_key == "test-api-key-123"

# Intentionally vulnerable - unsafe deserialization
def deserialize_data(data):
    # Intentionally vulnerable - using pickle for deserialization
    return pickle.loads(data)

# Intentionally vulnerable - unsafe serialization
def serialize_data(data):
    # Intentionally vulnerable - using pickle for serialization
    return pickle.dumps(data) 