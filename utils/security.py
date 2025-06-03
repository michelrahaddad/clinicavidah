import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session

# Rate limiting storage (in production, use Redis)
rate_limit_storage = {}

def rate_limit(max_requests=100, per_minutes=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            key = f"{client_ip}:{f.__name__}"
            now = datetime.now()
            
            if key in rate_limit_storage:
                requests, window_start = rate_limit_storage[key]
                
                # Reset window if time has passed
                if now - window_start > timedelta(minutes=per_minutes):
                    rate_limit_storage[key] = (1, now)
                else:
                    if requests >= max_requests:
                        logging.warning(f'Rate limit exceeded for {client_ip} on {f.__name__}')
                        return jsonify({'error': 'Rate limit exceeded'}), 429
                    
                    rate_limit_storage[key] = (requests + 1, window_start)
            else:
                rate_limit_storage[key] = (1, now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def generate_secure_token():
    """Generate cryptographically secure token"""
    return secrets.token_urlsafe(32)

def hash_sensitive_data(data):
    """Hash sensitive data for storage"""
    salt = secrets.token_hex(16)
    return hashlib.pbkdf2_hmac('sha256', data.encode('utf-8'), salt.encode('utf-8'), 100000).hex()

def audit_log(action, user_id=None, details=None):
    """Log security-relevant actions"""
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'user_id': user_id,
        'client_ip': client_ip,
        'user_agent': user_agent,
        'details': details
    }
    
    logging.info(f'AUDIT: {log_entry}')
    
    # In production, store in dedicated audit table or external service
    return log_entry

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function