"""
Sistema Médico VIDAH - Aplicação Final Corrigida
"""
from flask import Flask, session, redirect, request, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import timedelta
from sqlalchemy.orm import DeclarativeBase
import logging
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Base(DeclarativeBase):
    pass

def create_app():
    """Factory function para criar a aplicação Flask"""
    
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET") or "dev-secret-key"
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configuração do banco de dados
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
    
    # Inicializar banco de dados
    from core.database import db
    db.init_app(app)
    
    with app.app_context():
        import models
        db.create_all()
        logging.info("Database tables created")
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar rotas principais
    register_main_routes(app)
    
    # Configurar handlers de erro
    configure_error_handlers(app)
    
    # Middleware de segurança
    configure_security_middleware(app)
    
    logging.info("Sistema Médico VIDAH inicializado")
    return app

def register_blueprints(app):
    """Registra todos os blueprints"""
    try:
        from auth_simple import auth_bp
        from blueprints.dashboard import dashboard_bp
        from routes.medical import medical_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(medical_bp)
        
        logging.info("Blueprints registrados com sucesso")
    except Exception as e:
        logging.error(f"Erro ao registrar blueprints: {e}")
        # Registrar rotas de fallback
        register_fallback_routes(app)

def register_fallback_routes(app):
    """Registra rotas básicas de fallback"""
    
    @app.route('/auth/login', methods=['GET', 'POST'])
    def fallback_login():
        from werkzeug.security import check_password_hash
        from core.database import db
        from models import Medico
        
        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            crm = request.form.get('crm', '').strip()
            senha = request.form.get('senha', '')
            
            medico = db.session.query(Medico).filter_by(nome=nome, crm=crm).first()
            
            if medico and check_password_hash(medico.senha, senha):
                session['usuario'] = {
                    'id': medico.id,
                    'nome': medico.nome,
                    'crm': medico.crm,
                    'tipo': 'medico'
                }
                return redirect('/dashboard/')
        
        return render_template('login.html')

def register_main_routes(app):
    """Registra rotas principais"""
    
    @app.route('/')
    def index():
        """Página inicial"""
        if 'usuario' in session:
            return redirect('/dashboard/')
        return redirect('/auth/login')
    
    @app.route('/dashboard')
    def dashboard_redirect():
        """Redirecionamento para dashboard"""
        return redirect('/dashboard/')
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return {'status': 'ok', 'message': 'Sistema Médico VIDAH operacional'}

def configure_error_handlers(app):
    """Configura handlers de erro"""
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

def configure_security_middleware(app):
    """Configura middleware de segurança"""
    
    @app.before_request
    def security_headers():
        """Adiciona headers de segurança"""
        pass
    
    @app.after_request
    def add_security_headers(response):
        """Headers de segurança nas respostas"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    @app.before_request
    def log_request():
        """Log de requisições"""
        user = session.get('usuario', {})
        logging.info(f"Request: {request.method} {request.path} - User: {user.get('nome', 'Anonymous')}")

# Criar aplicação
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)