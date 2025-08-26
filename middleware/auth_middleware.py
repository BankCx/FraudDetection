from functools import wraps
import json
from ..config.security import validate_token, validate_api_key, log_security_event

def auth_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request = args[0]
        
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not validate_token(token):
            return json.dumps({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def api_key_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request = args[0]
        
        api_key = request.headers.get('X-API-Key', '')
        
        if not validate_api_key(api_key):
            return json.dumps({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

 