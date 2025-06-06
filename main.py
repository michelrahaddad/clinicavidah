"""
Sistema Médico VIDAH - Aplicação principal
Ponto de entrada da aplicação usando arquitetura modular
"""
import os
from app_modular import create_app

# Configurar ambiente
config_name = os.environ.get('FLASK_ENV', 'development')

# Criar aplicação usando factory pattern
app = create_app(config_name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
