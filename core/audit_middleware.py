"""
Middleware de auditoria - Sistema Médico VIDAH
"""
from flask import request, session, g
from core.logging_config import audit_logger, security_logger
from datetime import datetime
import time

def setup_audit_middleware(app):
    """Configura middleware de auditoria"""
    
    @app.before_request
    def log_request():
        """Log de todas as requisições"""
        g.start_time = time.time()
        user = session.get('usuario', {})
        user_info = f"{user.get('nome', 'Anonymous')} ({user.get('tipo', 'guest')})"
        
        audit_logger.info(
            f"Request: {request.method} {request.path} - "
            f"User: {user_info} - "
            f"IP: {request.remote_addr} - "
            f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
        )
        
        # Log tentativas de acesso sem autenticação em rotas protegidas
        protected_routes = ['/dashboard', '/medical', '/receitas', '/exames']
        if any(request.path.startswith(route) for route in protected_routes):
            if 'usuario' not in session:
                security_logger.warning(
                    f"Unauthorized access attempt to {request.path} from {request.remote_addr}"
                )
    
    @app.after_request
    def log_response(response):
        """Log de respostas"""
        duration = time.time() - g.start_time
        user = session.get('usuario', {})
        user_info = f"{user.get('nome', 'Anonymous')}"
        
        audit_logger.info(
            f"Response: {response.status_code} - "
            f"Duration: {duration:.3f}s - "
            f"User: {user_info} - "
            f"Path: {request.path}"
        )
        
        # Log erros críticos
        if response.status_code >= 500:
            security_logger.error(
                f"Server error {response.status_code} on {request.path} "
                f"for user {user_info}"
            )
        
        return response
