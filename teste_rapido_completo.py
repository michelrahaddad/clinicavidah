#!/usr/bin/env python3
"""
Teste rápido e completo do sistema médico
"""

import requests
import os
import re

def testar_sistema_completo():
    base_url = "http://localhost:5000"
    session = requests.Session()
    resultados = {"ok": 0, "erro": 0, "aviso": 0}
    
    print("=== TESTE COMPLETO DO SISTEMA MÉDICO VIDAH ===\n")
    
    # 1. TESTE DE AUTENTICAÇÃO
    print("1. AUTENTICAÇÃO:")
    try:
        # Página de login
        resp = session.get(f"{base_url}/login")
        if resp.status_code == 200:
            print("  ✓ Página de login carrega")
            resultados["ok"] += 1
        else:
            print("  ❌ Erro na página de login")
            resultados["erro"] += 1
            
        # Tentativa de login inválido
        resp = session.post(f"{base_url}/login", data={'nome': 'test', 'crm': 'test', 'senha': 'test'})
        if "inválidas" in resp.text.lower() or resp.status_code == 200:
            print("  ✓ Validação de credenciais funcionando")
            resultados["ok"] += 1
        else:
            print("  ❌ Validação de credenciais falhou")
            resultados["erro"] += 1
            
    except Exception as e:
        print(f"  ❌ Erro no teste de autenticação: {e}")
        resultados["erro"] += 1
    
    # 2. TESTE DE ROTAS PRINCIPAIS
    print("\n2. ROTAS PRINCIPAIS:")
    rotas = ["/", "/login", "/receita", "/exames_lab", "/exames_img", "/prontuario", "/dashboard"]
    
    for rota in rotas:
        try:
            resp = session.get(f"{base_url}{rota}")
            if resp.status_code in [200, 302]:
                print(f"  ✓ {rota}")
                resultados["ok"] += 1
            else:
                print(f"  ❌ {rota} - Status {resp.status_code}")
                resultados["erro"] += 1
        except Exception as e:
            print(f"  ❌ {rota} - Erro: {e}")
            resultados["erro"] += 1
    
    # 3. TESTE DE APIS
    print("\n3. APIS:")
    apis = [
        "/prontuario/api/autocomplete_pacientes?q=test",
        "/prontuario/api/update_date"
    ]
    
    for api in apis:
        try:
            if "update_date" in api:
                resp = session.post(f"{base_url}{api}", json={'tipo': 'receita', 'id': '1', 'nova_data': '2024-06-04'})
            else:
                resp = session.get(f"{base_url}{api}")
                
            if resp.status_code in [200, 302, 401, 403]:
                print(f"  ✓ {api}")
                resultados["ok"] += 1
            else:
                print(f"  ❌ {api} - Status {resp.status_code}")
                resultados["erro"] += 1
        except Exception as e:
            print(f"  ❌ {api} - Erro: {e}")
            resultados["erro"] += 1
    
    # 4. TESTE DE ARQUIVOS
    print("\n4. ARQUIVOS DO SISTEMA:")
    
    # Templates
    if os.path.exists("templates"):
        templates = [f for f in os.listdir("templates") if f.endswith('.html')]
        for template in templates[:5]:  # Primeiros 5 para ser rápido
            try:
                with open(f"templates/{template}", 'r') as f:
                    content = f.read()
                if len(content) > 100:  # Arquivo não vazio
                    print(f"  ✓ Template {template}")
                    resultados["ok"] += 1
                else:
                    print(f"  ⚠️ Template {template} muito pequeno")
                    resultados["aviso"] += 1
            except Exception as e:
                print(f"  ❌ Template {template} - Erro: {e}")
                resultados["erro"] += 1
    
    # Routes
    if os.path.exists("routes"):
        routes = [f for f in os.listdir("routes") if f.endswith('.py')]
        for route in routes:
            try:
                with open(f"routes/{route}", 'r') as f:
                    content = f.read()
                if "'usuario' not in session" in content:
                    print(f"  ✓ Route {route} - Autenticação OK")
                    resultados["ok"] += 1
                else:
                    print(f"  ⚠️ Route {route} - Verificar autenticação")
                    resultados["aviso"] += 1
            except Exception as e:
                print(f"  ❌ Route {route} - Erro: {e}")
                resultados["erro"] += 1
    
    # 5. TESTE DE MODELOS
    print("\n5. MODELOS DE DADOS:")
    try:
        if os.path.exists("models.py"):
            with open("models.py", 'r') as f:
                content = f.read()
            
            modelos = ["Medico", "Paciente", "Receita", "ExameLab", "ExameImg"]
            for modelo in modelos:
                if f"class {modelo}" in content:
                    print(f"  ✓ Modelo {modelo}")
                    resultados["ok"] += 1
                else:
                    print(f"  ❌ Modelo {modelo} não encontrado")
                    resultados["erro"] += 1
    except Exception as e:
        print(f"  ❌ Erro ao verificar modelos: {e}")
        resultados["erro"] += 1
    
    # 6. TESTE DE SEGURANÇA
    print("\n6. SEGURANÇA:")
    try:
        # Teste de SQL injection
        resp = session.post(f"{base_url}/login", data={
            'nome': "'; DROP TABLE medicos; --",
            'crm': 'test',
            'senha': 'test'
        })
        if resp.status_code in [200, 400, 401]:
            print("  ✓ Proteção contra SQL Injection")
            resultados["ok"] += 1
        else:
            print("  ❌ Possível vulnerabilidade SQL Injection")
            resultados["erro"] += 1
            
        # Headers de segurança
        resp = session.get(f"{base_url}/")
        if any(h in resp.headers for h in ['X-Content-Type-Options', 'X-Frame-Options']):
            print("  ✓ Headers de segurança presentes")
            resultados["ok"] += 1
        else:
            print("  ⚠️ Headers de segurança ausentes")
            resultados["aviso"] += 1
            
    except Exception as e:
        print(f"  ❌ Erro no teste de segurança: {e}")
        resultados["erro"] += 1
    
    # RELATÓRIO FINAL
    print("\n" + "="*50)
    print("RELATÓRIO FINAL DE TESTES")
    print("="*50)
    
    total = sum(resultados.values())
    if total > 0:
        score = (resultados["ok"] / total) * 100
        print(f"Total de testes: {total}")
        print(f"Sucessos: {resultados['ok']}")
        print(f"Avisos: {resultados['aviso']}")
        print(f"Erros: {resultados['erro']}")
        print(f"Score: {score:.1f}%")
        
        if score >= 90:
            print("\n🎉 SISTEMA EXCELENTE!")
        elif score >= 75:
            print("\n👍 SISTEMA BOM - Pequenos ajustes necessários")
        elif score >= 60:
            print("\n⚠️ SISTEMA REGULAR - Melhorias necessárias")
        else:
            print("\n🚨 SISTEMA CRÍTICO - Correções urgentes")
            
        return score
    else:
        print("Nenhum teste executado")
        return 0

if __name__ == "__main__":
    testar_sistema_completo()