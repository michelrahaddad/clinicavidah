import os
import logging
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__)
    
    # Basic configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    try:
        from routes.auth import auth_bp
        from routes.dashboard import dashboard_bp
        from routes.prontuario import prontuario_bp
        from routes.receita import receita_bp
        from routes.exames_lab import exames_lab_bp
        from routes.exames_img import exames_img_bp
        from routes.configuracoes import configuracoes_bp
        
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(prontuario_bp)
        app.register_blueprint(receita_bp)
        app.register_blueprint(exames_lab_bp)
        app.register_blueprint(exames_img_bp)
        app.register_blueprint(configuracoes_bp)
        
        logging.info("Core blueprints registered successfully")
    except Exception as e:
        logging.error(f"Error registering blueprints: {e}")
    
    # Create tables
    with app.app_context():
        try:
            import models
            db.create_all()
            logging.info("Database tables created successfully")
        except Exception as e:
            logging.error(f"Error creating database tables: {e}")
    
    # Root route
    @app.route('/')
    def index():
        return redirect('/auth/login')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)