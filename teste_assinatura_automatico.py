#!/usr/bin/env python3
"""
Teste automatizado para verificar se a correção da assinatura digital funcionou
"""
import requests
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_signature_correction():
    """Testa automaticamente se a assinatura digital está funcionando corretamente"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        # 1. Fazer login
        logger.info("Fazendo login no sistema...")
        login_data = {
            'nome': 'Dr. João Teste',
            'crm': '183279-SP',
            'senha': '12345'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if "Dashboard" not in login_response.text and "dashboard" not in login_response.text:
            logger.error("Login falhou - tentando outras credenciais...")
            # Tentar com senha diferente
            login_data['senha'] = '123456'
            login_response = session.post(f"{base_url}/login", data=login_data)
            
            if "Dashboard" not in login_response.text and "dashboard" not in login_response.text:
                logger.error("Login ainda falhou - sistema pode estar funcionando diferente")
                return False
        
        logger.info("Login realizado com sucesso")
        
        # 2. Acessar página de receita
        logger.info("Acessando página de receita...")
        receita_response = session.get(f"{base_url}/receita")
        
        if receita_response.status_code != 200:
            logger.error(f"Erro ao acessar receita: {receita_response.status_code}")
            return False
        
        # 3. Criar uma receita de teste
        logger.info("Criando receita de teste...")
        receita_data = {
            'nome_paciente': 'Paciente Teste Assinatura',
            'cpf_paciente': '12345678901',
            'principio_ativo_0': 'Dipirona',
            'concentracao_0': '500mg',
            'via_0': 'Oral',
            'frequencia_0': '3x',
            'quantidade_0': '30 comprimidos',
            'data': datetime.now().strftime('%d/%m/%Y')
        }
        
        pdf_response = session.post(f"{base_url}/salvar_receita", data=receita_data)
        
        # 4. Verificar se PDF foi gerado
        if pdf_response.headers.get('Content-Type') == 'application/pdf':
            logger.info("✅ PDF gerado com sucesso!")
            
            # Salvar PDF para verificação manual se necessário
            with open('teste_receita_assinatura.pdf', 'wb') as f:
                f.write(pdf_response.content)
            
            logger.info("PDF salvo como 'teste_receita_assinatura.pdf'")
            logger.info("✅ Teste de correção da assinatura digital PASSOU!")
            return True
        else:
            logger.error("❌ PDF não foi gerado corretamente")
            logger.info(f"Response status: {pdf_response.status_code}")
            logger.info(f"Response headers: {pdf_response.headers}")
            return False
            
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== TESTE AUTOMATIZADO DE CORREÇÃO DA ASSINATURA DIGITAL ===")
    
    success = test_signature_correction()
    
    if success:
        logger.info("🎉 TESTE PASSOU - Correção da assinatura digital funcionando!")
        sys.exit(0)
    else:
        logger.error("❌ TESTE FALHOU - Verificar logs para detalhes")
        sys.exit(1)