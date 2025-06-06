#!/usr/bin/env python3
"""
Teste automático da assinatura digital no PDF
Verifica se a assinatura do médico está sendo integrada corretamente
"""

import requests
import sys
import os

def testar_assinatura_pdf():
    """Testa se a assinatura digital está funcionando no PDF"""
    
    base_url = "http://localhost:5000"
    
    # Criar sessão
    session = requests.Session()
    
    try:
        # Fazer login
        login_data = {
            'nome': 'Michel Raineri Haddad',
            'crm': '183299-SP'
        }
        
        print("🔑 Fazendo login...")
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            return False
        
        # Testar geração de PDF
        print("📄 Testando geração de PDF...")
        pdf_response = session.get(f"{base_url}/gerar_pdf_receita/25")
        
        if pdf_response.status_code != 200:
            print(f"❌ Erro na geração do PDF: {pdf_response.status_code}")
            return False
        
        # Verificar se é realmente um PDF
        content_type = pdf_response.headers.get('content-type', '')
        print(f"📋 Content-Type: {content_type}")
        
        if 'application/pdf' not in content_type:
            print("❌ Resposta não é um PDF")
            print(f"Conteúdo recebido: {pdf_response.text[:200]}...")
            return False
        
        # Verificar tamanho do PDF
        pdf_size = len(pdf_response.content)
        print(f"📏 Tamanho do PDF: {pdf_size} bytes")
        
        if pdf_size < 10000:  # PDF muito pequeno pode indicar problema
            print("⚠️  PDF parece muito pequeno")
            return False
        
        # Salvar PDF para verificação
        with open('receita_teste_assinatura.pdf', 'wb') as f:
            f.write(pdf_response.content)
        
        print("✅ PDF gerado com sucesso!")
        print("📁 Arquivo salvo como: receita_teste_assinatura.pdf")
        
        # Verificar se contém dados da assinatura (procurar por base64)
        pdf_text = str(pdf_response.content)
        if 'data:image' in pdf_text and 'base64' in pdf_text:
            print("✅ Assinatura digital detectada no PDF!")
            return True
        else:
            print("❌ Assinatura digital não encontrada no PDF")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Iniciando teste automático da assinatura digital...")
    print("=" * 50)
    
    sucesso = testar_assinatura_pdf()
    
    print("=" * 50)
    if sucesso:
        print("🎉 TESTE PASSOU: Assinatura digital funcionando!")
        sys.exit(0)
    else:
        print("🚫 TESTE FALHOU: Problema com assinatura digital")
        sys.exit(1)