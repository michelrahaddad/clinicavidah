import os
import logging
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    # Create Flask app
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "vidah-medical-system-2024")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration
    database_url = os.environ.get("DATABASE_URL", "sqlite:///vidah_medical.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
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
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; font-src 'self' cdn.jsdelivr.net; img-src 'self' data:;"
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
    
    # Create tables
    with app.app_context():
        import models
        db.create_all()
        
        # Initialize database with sample data if needed
        from utils.db import init_database
        init_database()
        
        # Start automatic backup scheduler
        from utils.backup import schedule_backups
        schedule_backups()
    
    # Root redirect
    @app.route('/')
    def index():
        from flask import redirect, url_for, session
        if 'usuario' in session:
            return redirect(url_for('dashboard.dashboard'))
        return redirect(url_for('auth.login'))
    
    return app

# Create app instance
app = create_app()
