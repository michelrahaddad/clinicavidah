"""
Sistema Médico VIDAH - Aplicação principal
Usando arquitetura modular corrigida
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_final import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
