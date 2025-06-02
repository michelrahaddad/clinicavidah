import logging
import os
from flask import Flask, redirect, url_for
from flask_wtf import CSRFProtect
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.receita import receita_bp
from routes.exames_lab import exames_lab_bp
from routes.exames_img import exames_img_bp
from routes.prontuario import prontuario_bp
from routes.agenda import agenda_bp
from routes.medicos import medicos_bp

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sistema_medico.log'),
        logging.StreamHandler()
    ]
)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'vidah_ecocardiograma_2025_dev_key')
csrf = CSRFProtect(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(receita_bp)
app.register_blueprint(exames_lab_bp)
app.register_blueprint(exames_img_bp)
app.register_blueprint(prontuario_bp)
app.register_blueprint(agenda_bp)
app.register_blueprint(medicos_bp)

@app.route('/')
def index():
    """Redirect root to login page"""
    return redirect(url_for('auth.login'))

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return redirect(url_for('auth.login'))

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f'Server Error: {error}')
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
