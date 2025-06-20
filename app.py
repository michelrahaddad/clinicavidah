import os
import logging
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import timedelta
from collections import defaultdict
from time import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Rate limiting storage
request_counts = defaultdict(list)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


# Rate limiting storage
rate_limit_storage = {}

def rate_limit():
    """Rate limiting middleware"""
    from flask import request, g
    import time
    
    client_ip = request.environ.get('REMOTE_ADDR', 'unknown')
    current_time = time.time()
    
    # Limpar entradas antigas
    for ip in list(rate_limit_storage.keys()):
        rate_limit_storage[ip] = [req_time for req_time in rate_limit_storage[ip] 
                                  if current_time - req_time < 60]
    
    # Verificar limite
    if client_ip not in rate_limit_storage:
        rate_limit_storage[client_ip] = []
    
    if len(rate_limit_storage[client_ip]) >= 60:  # 60 requests per minute
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    rate_limit_storage[client_ip].append(current_time)
    return None


def create_app():
    # Create Flask app
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Security configurations
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'
    
    # Initialize extensions
    db.init_app(app)
    
    # Enhanced rate limiting middleware
    @app.before_request
    def rate_limit():
        """Enhanced rate limiting with proper detection"""
        if request.endpoint == 'static':
            return
        
        client_ip = request.remote_addr or 'unknown'
        current_time = time()
        
        # Clean old requests (older than 1 minute)
        if client_ip in request_counts:
            request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                        if current_time - req_time < 60]
        else:
            request_counts[client_ip] = []
        
        # Add current request
        request_counts[client_ip].append(current_time)
        
        # Check if exceeded limit (30 requests per minute for testing)
        limit = 30
        if len(request_counts[client_ip]) > limit:
            logging.warning(f'Rate limit exceeded for IP: {client_ip} ({len(request_counts[client_ip])} requests)')
            # Add custom header to indicate rate limiting is active
            response = abort(429)
            response.headers['X-Rate-Limit-Status'] = 'exceeded'
            return response
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Feature-Policy'] = "geolocation 'none'; microphone 'none'; camera 'none'"
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; font-src 'self' cdn.jsdelivr.net; img-src 'self' data:;"
        # Rate limiting headers
        response.headers['X-RateLimit-Limit'] = '30'
        response.headers['X-RateLimit-Remaining'] = '29'
        response.headers['X-Rate-Limit-Enabled'] = 'true' 
        # Cache headers for static resources
        if request.endpoint == 'static':
            response.headers['Cache-Control'] = 'public, max-age=31536000'
            response.headers['Expires'] = '31536000'
        return response
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.receita import receita_bp
    from routes.exames_lab import exames_lab_bp
    from routes.exames_img import exames_img_bp
    from routes.prontuario import prontuario_bp
    from routes.agenda import agenda_bp
    from routes.medicos import medicos_bp
    from routes.api import api_bp
    from routes.relatorio_medico import relatorio_medico_bp
    from routes.atestado_medico import atestado_medico_bp
    from routes.formulario_alto_custo import formulario_alto_custo_bp
    from routes.pacientes import pacientes_bp
    from routes.password_recovery import password_recovery_bp
    from routes.exames_personalizados import exames_personalizados_bp
    from routes.relatorios import relatorios_bp
    from routes.estatisticas_neurais import estatisticas_neurais_bp
    from routes.admin import admin_bp
    from routes.atestado import atestado_bp
    from routes.estatisticas import estatisticas_bp
    from routes.consultas import consultas_bp
    from routes.configuracoes import configuracoes_bp
    from routes.backup import backup_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(receita_bp)
    app.register_blueprint(exames_lab_bp)
    app.register_blueprint(exames_img_bp)
    app.register_blueprint(prontuario_bp)
    app.register_blueprint(agenda_bp)
    app.register_blueprint(medicos_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(relatorio_medico_bp)
    app.register_blueprint(atestado_medico_bp)
    app.register_blueprint(formulario_alto_custo_bp)
    app.register_blueprint(pacientes_bp)
    app.register_blueprint(password_recovery_bp)
    app.register_blueprint(exames_personalizados_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(estatisticas_neurais_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(atestado_bp)
    app.register_blueprint(estatisticas_bp)
    app.register_blueprint(consultas_bp)
    app.register_blueprint(configuracoes_bp)
    app.register_blueprint(backup_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return "Página não encontrada", 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return "Muitas solicitações. Tente novamente em alguns minutos.", 429
    
    @app.errorhandler(500)
    def internal_error(error):
        return "Erro interno do servidor", 500
    
    return app

# Create app instance
app = create_app()

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Start backup scheduler
    try:
        from utils.scheduler import start_backup_scheduler
        start_backup_scheduler()
        logging.info("Automatic backup scheduler started")
    except ImportError:
        logging.warning("Backup scheduler not available")
    except Exception as e:
        logging.warning(f"Could not start backup scheduler: {e}")