#!/usr/bin/env python3
"""
Teste automatizado completo dos badges médicos
Simula login e testa a funcionalidade completa
"""

import requests
import json
from bs4 import BeautifulSoup

def testar_sistema_completo():
    """Testa o sistema completo automaticamente"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("🔍 Testando sistema de badges médicos...")
    
    # 1. Testar acesso à página de login
    try:
        response = session.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✓ Página de login acessível")
        else:
            print(f"❌ Erro no login: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    # 2. Fazer login
    try:
        login_data = {
            'nome': 'michel raineri ahddad',
            'crm': '183299-SP'
        }
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code == 200 or response.status_code == 302:
            print("✓ Login realizado com sucesso")
        else:
            print(f"❌ Erro no login: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False
    
    # 3. Acessar prontuário
    try:
        response = session.get(f"{base_url}/prontuario")
        if response.status_code == 200:
            print("✓ Prontuário acessível")
            
            # Analisar HTML para verificar badges
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Verificar se existem badges médicos
            badges_receita = soup.find_all('span', class_='receita-badge')
            badges_lab = soup.find_all('span', class_='lab-badge')
            badges_img = soup.find_all('span', class_='img-badge')
            badges_relatorio = soup.find_all('span', class_='relatorio-badge')
            badges_atestado = soup.find_all('span', class_='atestado-badge')
            badges_alto_custo = soup.find_all('span', class_='alto-custo-badge')
            
            print(f"   Badges encontrados:")
            print(f"   - Receitas: {len(badges_receita)}")
            print(f"   - Lab: {len(badges_lab)}")
            print(f"   - Imagem: {len(badges_img)}")
            print(f"   - Relatórios: {len(badges_relatorio)}")
            print(f"   - Atestados: {len(badges_atestado)}")
            print(f"   - Alto Custo: {len(badges_alto_custo)}")
            
            # Verificar se há círculos verdes genéricos
            circulos_verdes = soup.find_all('span', string=lambda text: text and text.isdigit() and len(text) <= 3)
            circulos_problematicos = [c for c in circulos_verdes if 'medical-badge' not in c.get('class', [])]
            
            if circulos_problematicos:
                print(f"⚠️  Encontrados {len(circulos_problematicos)} círculos verdes genéricos")
                for circulo in circulos_problematicos:
                    print(f"    - {circulo}")
                return False
            else:
                print("✓ Nenhum círculo verde genérico encontrado")
            
        else:
            print(f"❌ Erro ao acessar prontuário: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar prontuário: {e}")
        return False
    
    # 4. Testar busca específica por Michel
    try:
        response = session.get(f"{base_url}/prontuario?busca_paciente=Michel")
        if response.status_code == 200:
            print("✓ Busca por Michel funcionando")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Verificar emojis específicos
            emojis_encontrados = []
            if "💊" in response.text:
                emojis_encontrados.append("💊 receitas")
            if "🧪" in response.text:
                emojis_encontrados.append("🧪 lab")
            if "🩻" in response.text:
                emojis_encontrados.append("🩻 imagem")
            if "🧾" in response.text:
                emojis_encontrados.append("🧾 relatórios")
            if "📄" in response.text:
                emojis_encontrados.append("📄 atestados")
            if "💰💊" in response.text:
                emojis_encontrados.append("💰💊 alto custo")
            
            print(f"   Emojis médicos encontrados: {', '.join(emojis_encontrados)}")
            
            if len(emojis_encontrados) >= 3:
                print("✅ Badges médicos funcionando corretamente!")
                return True
            else:
                print("⚠️  Poucos emojis médicos encontrados")
                return False
                
        else:
            print(f"❌ Erro na busca: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        return False

if __name__ == '__main__':
    resultado = testar_sistema_completo()
    if resultado:
        print("\n🎉 TESTE PASSOU: Badges médicos funcionando corretamente!")
    else:
        print("\n❌ TESTE FALHOU: Badges médicos precisam de correção")