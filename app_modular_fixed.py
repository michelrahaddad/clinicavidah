"""
Sistema Médico VIDAH - Aplicação principal modernizada (Versão Corrigida)
Estrutura modular com Blueprints, logging centralizado e validadores
"""
import os
import logging
from datetime import timedelta
from flask import Flask, request, session, redirect, url_for, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

# Core imports
from core.database import init_database
from config import DevelopmentConfig, ProductionConfig, TestingConfig

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = config_map.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)
    
    # Initialize database
    db = init_database(app)
    
    # Create tables within app context
    with app.app_context():
        import models  # Import models to register them
        db.create_all()
        logger.info("Database tables created")
    
    # Register blueprints
    register_blueprints(app)
    
    # Register main routes
    register_main_routes(app)
    
    # Configure error handlers
    configure_error_handlers(app)
    
    # Configure security middleware
    configure_security_middleware(app)
    
    logger.info(f"Sistema Médico VIDAH inicializado em modo {config_name}")
    return app


def register_blueprints(app):
    """Registra todos os blueprints da aplicação"""
    try:
        # Import blueprints
        from auth_simple import auth_simple
        from blueprints.dashboard import dashboard_bp
        
        # Register blueprints
        app.register_blueprint(auth_simple, url_prefix='/auth')
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
        
        logger.info("Blueprints registrados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao importar/registrar blueprints: {e}")
        # Create simple fallback routes
        from flask import request, render_template
        @app.route('/auth/login', methods=['GET', 'POST'])
        def fallback_login():
            if request.method == 'GET':
                return render_template('login.html')
            return "Auth fallback active"


def register_main_routes(app):
    """Registra rotas principais da aplicação"""
    
    @app.route('/')
    def index():
        """Página inicial - redireciona baseado na autenticação"""
        if 'usuario' in session:
            return redirect('/dashboard/')
        return redirect('/auth/login')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard principal do sistema"""
        if 'usuario' not in session:
            return redirect('/auth/login')
        
        try:
            from core.database import db
            from models import Paciente, Receita, ExameLab, ExameImg
            from datetime import datetime, timedelta
            
            user = session.get('usuario')
            user_type = session.get('usuario_tipo', 'medico')
            
            # Estatísticas básicas
            stats = {}
            
            if user_type == 'admin':
                stats['pacientes'] = db.session.query(Paciente).count()
                stats['receitas'] = db.session.query(Receita).count()
                stats['exames_lab'] = db.session.query(ExamesLab).count()
                stats['exames_img'] = db.session.query(ExamesImg).count()
            else:
                # Para médicos, mostrar apenas seus dados
                stats['pacientes'] = db.session.query(Paciente).filter_by(medico=user).count()
                stats['receitas'] = db.session.query(Receita).filter_by(medico=user).count()
                stats['exames_lab'] = db.session.query(ExamesLab).filter_by(medico=user).count()
                stats['exames_img'] = db.session.query(ExamesImg).filter_by(medico=user).count()
            
            return render_template('dashboard.html', 
                                 user=user, 
                                 user_type=user_type, 
                                 stats=stats)
        except Exception as e:
            logger.error(f"Erro no dashboard: {e}")
            return render_template('dashboard.html', 
                                 user=session.get('usuario'), 
                                 user_type=session.get('usuario_tipo', 'medico'),
                                 stats={})
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return {'status': 'healthy', 'service': 'Sistema Médico VIDAH'}, 200


def configure_error_handlers(app):
    """Configura handlers de erro personalizados"""
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Erro interno: {error}")
        return render_template('errors/500.html'), 500


def configure_security_middleware(app):
    """Configura middleware de segurança"""
    
    @app.before_request
    def security_headers():
        """Adiciona headers de segurança"""
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=8)
    
    @app.after_request
    def add_security_headers(response):
        """Adiciona headers de segurança na resposta"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    @app.before_request
    def log_request():
        """Log de requisições para auditoria"""
        if request.endpoint and 'static' not in request.endpoint:
            logger.info(f"Request: {request.method} {request.path} - User: {session.get('usuario', 'Anonymous')}")


# Create the application instance
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # For production deployment
    app = create_app()