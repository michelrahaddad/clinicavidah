#!/usr/bin/env python3
"""
Teste específico para ícones clicáveis do prontuário médico
Testa sistematicamente cada ícone e sua funcionalidade de navegação
"""

import sys
import requests
import time
from datetime import datetime

def testar_servidor_funcionando():
    """Verifica se o servidor está funcionando"""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        print(f"✓ Servidor respondendo - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ Erro no servidor: {e}")
        return False

def testar_login():
    """Testa o login como admin"""
    try:
        # Primeiro, pega a página de login
        session = requests.Session()
        response = session.get('http://localhost:5000/auth/login', timeout=10)
        
        if response.status_code != 200:
            print(f"✗ Página de login falhou: {response.status_code}")
            print(f"Resposta: {response.text[:200]}...")
            return None
            
        # Tenta fazer login
        login_data = {
            'usuario': 'admin',
            'senha': 'admin123'
        }
        
        response = session.post('http://localhost:5000/auth/login', 
                              data=login_data, 
                              timeout=10,
                              allow_redirects=False)
        
        if response.status_code in [302, 200]:
            print("✓ Login realizado com sucesso")
            return session
        else:
            print(f"✗ Login falhou: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Erro durante login: {e}")
        return None

def testar_prontuario_michel(session):
    """Testa acesso ao prontuário do Michel"""
    try:
        response = session.get('http://localhost:5000/prontuario/buscar?nome=Michel', timeout=10)
        
        if response.status_code == 200:
            print("✓ Prontuário do Michel acessível")
            
            # Verifica se há badges visíveis
            badges_esperados = ['💊', '🧪', '🩻', '📄', '🏥', '💰']
            badges_encontrados = []
            
            for badge in badges_esperados:
                if badge in response.text:
                    badges_encontrados.append(badge)
            
            print(f"✓ Badges encontrados: {badges_encontrados}")
            return True
        else:
            print(f"✗ Prontuário não acessível: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Erro ao acessar prontuário: {e}")
        return False

def testar_icones_clicaveis(session):
    """Testa cada ícone clicável específico"""
    
    rotas_icones = {
        '💊 Receitas': '/prontuario/receita_especifica/1',
        '🧪 Exames Lab': '/prontuario/exame_lab_especifico/1', 
        '🩻 Exames Img': '/prontuario/exame_img_especifico/1',
        '📄 Relatórios': '/prontuario/relatorio_especifico/1',
        '🏥 Atestados': '/prontuario/atestado_especifico/1',
        '💰💊 Alto Custo': '/prontuario/alto_custo_especifico/1'
    }
    
    resultados = {}
    
    for nome_icone, rota in rotas_icones.items():
        try:
            response = session.get(f'http://localhost:5000{rota}', timeout=10)
            
            if response.status_code == 200:
                # Verifica se tem navegação lateral
                tem_navegacao = 'sidebar' in response.text.lower() or 'nav' in response.text.lower()
                # Verifica se tem dados pré-preenchidos
                tem_dados = 'Michel' in response.text
                
                resultados[nome_icone] = {
                    'status': '✓ Funcionando',
                    'navegacao': '✓' if tem_navegacao else '✗',
                    'dados': '✓' if tem_dados else '✗'
                }
                print(f"✓ {nome_icone}: Página carregou corretamente")
                
            else:
                resultados[nome_icone] = {
                    'status': f'✗ Erro {response.status_code}',
                    'navegacao': '✗',
                    'dados': '✗'
                }
                print(f"✗ {nome_icone}: Erro {response.status_code}")
                
        except Exception as e:
            resultados[nome_icone] = {
                'status': f'✗ Exceção: {str(e)[:50]}',
                'navegacao': '✗',
                'dados': '✗'
            }
            print(f"✗ {nome_icone}: Erro - {e}")
    
    return resultados

def relatorio_final(resultados):
    """Gera relatório final dos testes"""
    print("\n" + "="*60)
    print("RELATÓRIO FINAL - TESTE DOS ÍCONES CLICÁVEIS")
    print("="*60)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    for nome_icone, resultado in resultados.items():
        print(f"{nome_icone}:")
        print(f"  Status: {resultado['status']}")
        print(f"  Navegação: {resultado['navegacao']}")
        print(f"  Dados: {resultado['dados']}")
        print()
    
    # Conta sucessos
    funcionando = sum(1 for r in resultados.values() if '✓' in r['status'])
    total = len(resultados)
    
    print(f"RESUMO: {funcionando}/{total} ícones funcionando corretamente")
    
    if funcionando == total:
        print("🎉 TODOS OS ÍCONES ESTÃO FUNCIONANDO!")
    else:
        print("⚠️  Alguns ícones precisam de correção")

def main():
    """Função principal do teste"""
    print("INICIANDO TESTE DOS ÍCONES CLICÁVEIS")
    print("="*50)
    
    # Teste 1: Servidor funcionando
    if not testar_servidor_funcionando():
        print("❌ Servidor não está funcionando. Abortando testes.")
        return
    
    # Teste 2: Login
    session = testar_login()
    if not session:
        print("❌ Login falhou. Abortando testes.")
        return
    
    # Teste 3: Prontuário Michel
    if not testar_prontuario_michel(session):
        print("❌ Prontuário não acessível. Continuando com testes individuais...")
    
    # Teste 4: Ícones clicáveis
    print("\nTestando ícones clicáveis individuais...")
    resultados = testar_icones_clicaveis(session)
    
    # Relatório final
    relatorio_final(resultados)

if __name__ == "__main__":
    main()