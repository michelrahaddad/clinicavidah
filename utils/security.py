from functools import wraps
from flask import session, redirect, url_for, request, flash
from models import LogSistema
from app import db
from datetime import datetime
import logging

def require_admin(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar múltiplas formas de autenticação admin
        if ('admin_data' not in session and 
            'admin' not in session and 
            session.get('admin') != True):
            flash('Acesso não autorizado. Faça login como administrador.', 'error')
            logging.warning(f'Unauthorized admin access attempt to {f.__name__}')
            return redirect(url_for('auth.login'))
        
        # Log successful admin access
        admin_data = session.get('admin_data', {})
        admin_name = admin_data.get('nome', 'Unknown Admin') if admin_data else session.get('usuario', 'Unknown')
        logging.info(f'Admin access granted to {f.__name__} by: {admin_name}')
        return f(*args, **kwargs)
    return decorated_function

def log_admin_action(tipo, usuario, acao, ip_address=None, detalhes=None):
    """Log admin actions to database"""
    try:
        log_entry = LogSistema(
            tipo=tipo,
            usuario=usuario,
            acao=acao,
            ip_address=ip_address or request.remote_addr if request else None,
            detalhes=detalhes
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        logging.error(f'Error logging admin action: {e}')

def rate_limit(max_requests=10, per_minutes=5):
    """Rate limiting decorator (placeholder for future implementation)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # For now, just pass through
            # Future: implement Redis-based rate limiting
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_auth(f):
    """Decorator to require user authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return {'error': 'Authentication required'}, 401
        return f(*args, **kwargs)
    return decorated_function

def audit_log(action):
    """Decorator to log user actions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                if 'usuario' in session:
                    log_admin_action(
                        'user_action', 
                        session['usuario']['nome'], 
                        action,
                        request.remote_addr if request else None
                    )
                return result
            except Exception as e:
                logging.error(f'Error in audited function {f.__name__}: {e}')
                raise
        return decorated_function
    return decorator