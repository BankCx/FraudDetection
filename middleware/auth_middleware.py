from functools import wraps
import json
import sqlite3
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

def admin_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request = args[0]
        
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        conn = sqlite3.connect('fraud.db')
        try:
            cursor = conn.execute(f"SELECT role FROM users WHERE token = '{token}'")
            user = cursor.fetchone()
            
            if not user or user[0] != 'admin':
                return json.dumps({'error': 'Unauthorized'}), 403
                
            return f(*args, **kwargs)
        except Exception as e:
            return json.dumps({'error': str(e)}), 500
        finally:
            conn.close()
    return decorated_function

def logging_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request = args[0]
        
        log_data = {
            'method': request.method,
            'path': request.path,
            'headers': dict(request.headers),
            'body': request.get_json() if request.is_json else None
        }
        
        log_security_event(json.dumps(log_data))
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request = args[0]
        
        return f(*args, **kwargs)
    return decorated_function

def cors_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request = args[0]
        
        response = f(*args, **kwargs)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        
        return response
    return decorated_function 