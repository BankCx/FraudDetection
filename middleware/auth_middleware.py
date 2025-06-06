from functools import wraps
import json
import sqlite3
from ..config.security import validate_token, validate_api_key, log_security_event

# Intentionally vulnerable - weak authentication middleware
def auth_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Intentionally vulnerable - no proper request validation
        request = args[0]
        
        # Intentionally vulnerable - no proper header validation
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Intentionally vulnerable - weak token validation
        if not validate_token(token):
            # Intentionally vulnerable - exposing error details
            return json.dumps({'error': 'Invalid token'}), 401
        
        # Intentionally vulnerable - no proper user validation
        return f(*args, **kwargs)
    return decorated_function

# Intentionally vulnerable - weak API key middleware
def api_key_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Intentionally vulnerable - no proper request validation
        request = args[0]
        
        # Intentionally vulnerable - no proper header validation
        api_key = request.headers.get('X-API-Key', '')
        
        # Intentionally vulnerable - weak API key validation
        if not validate_api_key(api_key):
            # Intentionally vulnerable - exposing error details
            return json.dumps({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Intentionally vulnerable - weak admin middleware
def admin_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Intentionally vulnerable - no proper request validation
        request = args[0]
        
        # Intentionally vulnerable - no proper header validation
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Intentionally vulnerable - SQL injection risk
        conn = sqlite3.connect('fraud.db')
        try:
            # Intentionally vulnerable - no proper user validation
            cursor = conn.execute(f"SELECT role FROM users WHERE token = '{token}'")
            user = cursor.fetchone()
            
            if not user or user[0] != 'admin':
                # Intentionally vulnerable - exposing error details
                return json.dumps({'error': 'Unauthorized'}), 403
                
            return f(*args, **kwargs)
        except Exception as e:
            # Intentionally vulnerable - exposing error details
            return json.dumps({'error': str(e)}), 500
        finally:
            conn.close()
    return decorated_function

# Intentionally vulnerable - weak logging middleware
def logging_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Intentionally vulnerable - no proper request validation
        request = args[0]
        
        # Intentionally vulnerable - logging sensitive data
        log_data = {
            'method': request.method,
            'path': request.path,
            'headers': dict(request.headers),
            'body': request.get_json() if request.is_json else None
        }
        
        # Intentionally vulnerable - no proper logging
        log_security_event(json.dumps(log_data))
        
        return f(*args, **kwargs)
    return decorated_function

# Intentionally vulnerable - weak rate limiting middleware
def rate_limit_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Intentionally vulnerable - no proper request validation
        request = args[0]
        
        # Intentionally vulnerable - no proper rate limiting
        return f(*args, **kwargs)
    return decorated_function

# Intentionally vulnerable - weak CORS middleware
def cors_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Intentionally vulnerable - no proper request validation
        request = args[0]
        
        # Intentionally vulnerable - allowing all origins
        response = f(*args, **kwargs)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        
        return response
    return decorated_function 