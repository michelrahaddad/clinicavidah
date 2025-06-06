#!/usr/bin/env python3
"""
Teste automatizado para verificar se o botão Exames Lab foi corrigido
"""
import requests
import logging
from bs4 import BeautifulSoup
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_botao_exames_lab_corrigido():
    """Testa se o botão Exames Lab foi corrigido"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    logger.info("=== TESTE DO BOTÃO EXAMES LAB CORRIGIDO ===")
    
    try:
        # 1. Login
        logger.info("Realizando login...")
        login_data = {
            'nome': 'Michel Raineri Haddad',
            'crm': '183299-SP',
            'senha': '12345'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code != 200:
            logger.error(f"❌ Erro no login: {login_response.status_code}")
            return False
            
        if "Dashboard" not in login_response.text and "dashboard" not in login_response.text:
            logger.error("❌ Login não redirecionou para dashboard")
            return False
        
        logger.info("✅ Login realizado com sucesso")
        
        # 2. Acessar página de receita
        logger.info("Acessando página de receita...")
        receita_response = session.get(f"{base_url}/receita")
        
        if receita_response.status_code != 200:
            logger.error(f"❌ Erro ao acessar receita: {receita_response.status_code}")
            return False
        
        logger.info("✅ Página de receita acessada")
        
        # 3. Verificar se o botão existe na página
        soup = BeautifulSoup(receita_response.text, 'html.parser')
        
        # Buscar pelo ID específico
        btn_exames_lab = soup.find('a', id='btn-exames-lab')
        
        if not btn_exames_lab:
            logger.error("❌ Botão #btn-exames-lab não encontrado na página")
            return False
        
        logger.info("✅ Botão Exames Lab encontrado na página")
        
        # 4. Verificar atributos do botão
        href = btn_exames_lab.get('href')
        classes = btn_exames_lab.get('class', [])
        
        logger.info(f"Href do botão: {href}")
        logger.info(f"Classes do botão: {classes}")
        
        if not href or 'exames_lab' not in href:
            logger.error("❌ Botão sem href correto para exames_lab")
            return False
        
        logger.info("✅ Href do botão está correto")
        
        # 5. Testar redirecionamento direto
        logger.info("Testando redirecionamento para /exames_lab...")
        exames_response = session.get(f"{base_url}/exames_lab")
        
        if exames_response.status_code != 200:
            logger.error(f"❌ Rota /exames_lab não acessível: {exames_response.status_code}")
            return False
        
        if "Exames Laboratoriais" not in exames_response.text and "exames" not in exames_response.text.lower():
            logger.error("❌ Página de exames lab não carregou corretamente")
            return False
        
        logger.info("✅ Rota /exames_lab funciona corretamente")
        
        # 6. Verificar JavaScript na página
        script_sections = soup.find_all('script')
        has_navigation_setup = False
        
        for script in script_sections:
            if script.string and 'setupNavigationButtons' in script.string:
                has_navigation_setup = True
                logger.info("✅ JavaScript de navegação encontrado")
                break
        
        if not has_navigation_setup:
            logger.warning("⚠️ JavaScript de navegação não encontrado")
        
        # 7. Resultado final
        logger.info("\n=== RESULTADO DO TESTE ===")
        logger.info("✅ BOTÃO EXAMES LAB CORRIGIDO COM SUCESSO!")
        logger.info("✅ Login funcionando")
        logger.info("✅ Página de receita acessível")
        logger.info("✅ Botão presente na página com ID correto")
        logger.info("✅ Href do botão apontando para rota correta")
        logger.info("✅ Rota /exames_lab funcionando")
        logger.info("✅ Página de exames lab carregando corretamente")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {e}")
        return False

if __name__ == "__main__":
    success = test_botao_exames_lab_corrigido()
    if success:
        print("\n🎉 TESTE PASSOU! O botão Exames Lab foi corrigido com sucesso!")
    else:
        print("\n❌ TESTE FALHOU! Ainda há problemas com o botão.")