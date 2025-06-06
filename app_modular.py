"""
Sistema Médico VIDAH - Aplicação principal modernizada
Estrutura modular com Blueprints, logging centralizado e validadores
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Importar configurações e componentes core
from config import config
from core.logging import VidahLogger

class Base(DeclarativeBase):
    pass

# Instâncias globais
db = SQLAlchemy(model_class=Base)
vidah_logger = VidahLogger()

def create_app(config_name=None):
    """Factory function para criar a aplicação Flask"""
    
    # Determinar ambiente
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Criar aplicação
    app = Flask(__name__)
    
    # Configurar aplicação
    app.config.from_object(config.get(config_name, config['default']))
    
    # Configurar proxy para produção
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Inicializar extensões
    db.init_app(app)
    vidah_logger.init_app(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Configurar handlers de erro
    configure_error_handlers(app)
    
    # Configurar middleware de segurança
    configure_security_middleware(app)
    
    # Criar tabelas do banco de dados
    with app.app_context():
        import models  # noqa: F401
        db.create_all()
        vidah_logger.logger.info("Database tables created successfully")
    
    return app

def register_blueprints(app):
    """Registra todos os blueprints da aplicação"""
    
    # Blueprints modulares novos
    from blueprints.auth import auth_bp
    from blueprints.dashboard import dashboard_bp
    from blueprints.prescriptions import prescriptions_bp
    from blueprints.patients import patients_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(prescriptions_bp)
    app.register_blueprint(patients_bp)
    
    # Blueprints existentes (compatibilidade)
    try:
        from routes.receita import receita_bp
        app.register_blueprint(receita_bp, url_prefix='/receita')
    except ImportError:
        pass
    
    try:
        from routes.prontuario import prontuario_bp
        app.register_blueprint(prontuario_bp)
    except ImportError:
        pass
    
    try:
        from routes.exames_lab import exames_lab_bp
        app.register_blueprint(exames_lab_bp)
    except ImportError:
        pass
    
    try:
        from routes.exames_img import exames_img_bp
        app.register_blueprint(exames_img_bp)
    except ImportError:
        pass
    
    try:
        from routes.medicamentos import medicamentos_bp
        app.register_blueprint(medicamentos_bp)
    except ImportError:
        pass
    
    try:
        from routes.admin import admin_bp
        app.register_blueprint(admin_bp)
    except ImportError:
        pass
    
    try:
        from routes.pacientes import pacientes_bp as old_pacientes_bp
        app.register_blueprint(old_pacientes_bp, url_prefix='/pacientes_old')
    except ImportError:
        pass
    
    # Blueprint principal (rotas básicas)
    register_main_routes(app)

def register_main_routes(app):
    """Registra rotas principais da aplicação"""
    from flask import render_template, session, redirect, url_for
    from core.logging import get_logger
    
    logger = get_logger('main')
    
    @app.route('/')
    def index():
        """Página inicial - redireciona baseado na autenticação"""
        if session.get('usuario') or session.get('admin_usuario'):
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard principal do sistema"""
        if not (session.get('usuario') or session.get('admin_usuario')):
            return redirect(url_for('auth.login'))
        
        user = session.get('usuario') or session.get('admin_usuario')
        user_type = session.get('usuario_tipo', 'medico')
        
        logger.info(f"Dashboard accessed by: {user} ({user_type})")
        
        return render_template('dashboard.html', 
                             user=user, 
                             user_type=user_type)
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return {'status': 'healthy', 'service': 'Sistema Médico VIDAH'}, 200

def configure_error_handlers(app):
    """Configura handlers de erro personalizados"""
    from flask import render_template, jsonify
    from core.logging import get_logger
    
    logger = get_logger('errors')
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 error: {error}")
        if app.config.get('DEBUG'):
            return render_template('errors/404.html'), 404
        return jsonify({'error': 'Página não encontrada'}), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"403 error: {error}")
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {error}")
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        logger.warning(f"Rate limit exceeded: {error}")
        return jsonify({'error': 'Muitas tentativas. Tente novamente mais tarde.'}), 429

def configure_security_middleware(app):
    """Configura middleware de segurança"""
    from flask import request, session
    from core.logging import get_logger
    
    logger = get_logger('security')
    
    @app.before_request
    def security_headers():
        """Adiciona headers de segurança"""
        # Fazer sessão permanente se autenticado
        if session.get('usuario') or session.get('admin_usuario'):
            session.permanent = True
    
    @app.after_request
    def add_security_headers(response):
        """Adiciona headers de segurança na resposta"""
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # HSTS for HTTPS
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'"
        )
        response.headers['Content-Security-Policy'] = csp
        
        return response
    
    @app.before_request
    def log_request():
        """Log de requisições para auditoria"""
        if not request.endpoint or request.endpoint.startswith('static'):
            return
        
        user = session.get('usuario') or session.get('admin_usuario', 'anonymous')
        logger.info(f"Request: {request.method} {request.path} by {user}")

# Instância da aplicação para compatibilidade
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)