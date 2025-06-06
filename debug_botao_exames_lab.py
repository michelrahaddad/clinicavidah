#!/usr/bin/env python3
"""
Debug completo do botão Exames Lab na página de receita
"""
import requests
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_botao_exames_lab():
    """Debug completo do botão Exames Lab"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    logger.info("=== DEBUG BOTÃO EXAMES LAB ===")
    
    try:
        # 1. Login
        logger.info("Fazendo login...")
        login_data = {
            'nome': 'Michel Raineri Haddad',
            'crm': '183299-SP',
            'senha': '12345'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if "Dashboard" not in login_response.text and "dashboard" not in login_response.text:
            logger.error("❌ Login falhou")
            return False
        
        logger.info("✅ Login realizado com sucesso")
        
        # 2. Acessar página de receita
        logger.info("Acessando página de receita...")
        receita_response = session.get(f"{base_url}/receita")
        
        if receita_response.status_code != 200:
            logger.error(f"❌ Erro ao acessar receita: {receita_response.status_code}")
            return False
        
        # 3. Analisar HTML da página
        soup = BeautifulSoup(receita_response.text, 'html.parser')
        
        # Procurar o botão Exames Lab
        exames_lab_buttons = soup.find_all(['a', 'button'], string=lambda text: text and 'Exames Lab' in text)
        
        logger.info(f"Botões 'Exames Lab' encontrados: {len(exames_lab_buttons)}")
        
        for i, btn in enumerate(exames_lab_buttons):
            logger.info(f"Botão {i+1}:")
            logger.info(f"  Tag: {btn.name}")
            logger.info(f"  Classes: {btn.get('class', [])}")
            logger.info(f"  Href: {btn.get('href', 'N/A')}")
            logger.info(f"  Onclick: {btn.get('onclick', 'N/A')}")
            logger.info(f"  Style: {btn.get('style', 'N/A')}")
            logger.info(f"  HTML: {str(btn)[:200]}...")
        
        # 4. Testar rota diretamente
        logger.info("Testando rota /exames_lab diretamente...")
        exames_lab_response = session.get(f"{base_url}/exames_lab")
        
        if exames_lab_response.status_code == 200:
            logger.info("✅ Rota /exames_lab funciona corretamente")
        else:
            logger.error(f"❌ Rota /exames_lab falhou: {exames_lab_response.status_code}")
        
        # 5. Verificar se há elementos sobrepostos
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'exames_lab' in script.string:
                logger.info(f"JavaScript relacionado encontrado: {script.string[:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante debug: {e}")
        return False

if __name__ == "__main__":
    debug_botao_exames_lab()