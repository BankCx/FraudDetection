from functools import wraps
import json
from ..config.security import validate_api_key, log_security_event

def auth_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # JWT token validation removed - middleware disabled
        log_security_event("Auth middleware bypassed - JWT functionality removed")
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

 