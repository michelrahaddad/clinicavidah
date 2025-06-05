#!/usr/bin/env python3
"""
Script de debug para identificar o erro 500 no servidor
"""

import sys
import traceback
from flask import Flask
from app import app

def debug_app_startup():
    """Debug da inicialização do app"""
    try:
        print("Testando importação dos módulos...")
        
        # Testa imports principais
        from routes import auth, prontuario, receita, exames_lab, exames_img
        print("✓ Imports principais OK")
        
        # Testa configuração do app
        print(f"✓ App configurado: {app.name}")
        print(f"✓ Blueprints registrados: {len(app.blueprints)}")
        
        # Lista blueprints
        for name, blueprint in app.blueprints.items():
            print(f"  - {name}: {blueprint}")
        
        # Testa rotas básicas
        with app.test_client() as client:
            print("Testando rota raiz...")
            response = client.get('/')
            print(f"Status: {response.status_code}")
            
            print("Testando rota de login...")
            response = client.get('/auth/login')
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                print(f"Erro: {response.data.decode()}")
        
        print("✓ Teste de debug concluído")
        
    except Exception as e:
        print(f"✗ Erro durante debug: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_app_startup()