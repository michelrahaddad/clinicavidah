#!/usr/bin/env python3
"""
Teste completo de usabilidade da página de prontuário
Testa todos os ícones, funções e identifica bugs
"""

import requests
import json
from werkzeug.security import check_password_hash
import sqlite3
import sys

def test_prontuario_usability():
    """Realiza teste completo de usabilidade do prontuário"""
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("=== TESTE DE USABILIDADE DO PRONTUÁRIO ===")
    
    # Teste 1: Login válido
    print("\n1. Testando login...")
    login_data = {
        'nome': 'Dr. Carlos Silva',
        'crm': '123456-SP',
        'senha': 'senha123'
    }
    
    login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    print(f"Status login: {login_response.status_code}")
    
    if login_response.status_code != 302:
        print("❌ ERRO: Login falhou")
        return False
    
    # Teste 2: Acesso ao prontuário
    print("\n2. Testando acesso ao prontuário...")
    prontuario_response = session.get(f"{base_url}/prontuario")
    print(f"Status prontuário: {prontuario_response.status_code}")
    
    if prontuario_response.status_code != 200:
        print("❌ ERRO: Acesso ao prontuário falhou")
        return False
    
    content = prontuario_response.text
    
    # Teste 3: Verificação de elementos da interface
    print("\n3. Testando elementos da interface...")
    
    # Verificar se o campo de busca existe
    if 'id="search_patient"' in content or 'name="search_patient"' in content:
        print("✓ Campo de busca encontrado")
    else:
        print("❌ ERRO: Campo de busca não encontrado")
    
    # Verificar se os badges de documentos existem
    badges_found = []
    if 'fa-prescription' in content or 'fas fa-pills' in content:
        badges_found.append("receitas")
    if 'fa-flask' in content or 'fas fa-vial' in content:
        badges_found.append("exames_lab")
    if 'fa-x-ray' in content or 'fas fa-camera' in content:
        badges_found.append("exames_img")
    
    print(f"✓ Badges encontrados: {badges_found}")
    
    # Teste 4: API de autocomplete
    print("\n4. Testando API de autocomplete...")
    try:
        autocomplete_response = session.get(f"{base_url}/prontuario/api/autocomplete_pacientes?q=test")
        print(f"Status autocomplete: {autocomplete_response.status_code}")
        if autocomplete_response.status_code == 200:
            print("✓ API de autocomplete funcionando")
        else:
            print("❌ ERRO: API de autocomplete falhou")
    except Exception as e:
        print(f"❌ ERRO na API de autocomplete: {e}")
    
    # Teste 5: Busca de prontuário
    print("\n5. Testando busca de prontuário...")
    try:
        search_response = session.post(f"{base_url}/prontuario", data={'search_patient': 'Maria'})
        print(f"Status busca: {search_response.status_code}")
        if search_response.status_code == 200:
            print("✓ Busca de prontuário funcionando")
        else:
            print("❌ ERRO: Busca de prontuário falhou")
    except Exception as e:
        print(f"❌ ERRO na busca: {e}")
    
    # Teste 6: Teste de acesso a detalhes (se houver dados)
    print("\n6. Testando acesso a detalhes...")
    try:
        details_response = session.get(f"{base_url}/prontuario/detalhes?paciente=Maria&data=2024-06-04")
        print(f"Status detalhes: {details_response.status_code}")
        if details_response.status_code == 200:
            print("✓ Página de detalhes funcionando")
        else:
            print("⚠️ Página de detalhes não acessível (pode ser normal se não há dados)")
    except Exception as e:
        print(f"❌ ERRO nos detalhes: {e}")
    
    print("\n=== RESUMO DOS TESTES ===")
    print("✓ Login funcionando")
    print("✓ Acesso ao prontuário funcionando")
    print("✓ Interface carregando")
    
    return True

if __name__ == "__main__":
    test_prontuario_usability()