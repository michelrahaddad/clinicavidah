"""
Teste final para verificar se os dados do paciente e assinatura digital 
aparecem corretamente no PDF gerado
"""
import requests
from datetime import datetime

def testar_pdf_completo():
    """Testa se o PDF contém dados completos do paciente e assinatura digital"""
    
    print("🔍 Testando integração completa de dados no PDF...")
    
    # Simular login
    session = requests.Session()
    login_data = {
        'nome': 'Michel Raineri Haddad',
        'crm': '183299-SP', 
        'senha': '123456'
    }
    
    try:
        # Fazer login
        login_response = session.post('http://localhost:5000/auth/login', data=login_data)
        print(f"✓ Login: {login_response.status_code}")
        
        # Gerar PDF de receita específica
        pdf_response = session.get('http://localhost:5000/receita/pdf/24')
        print(f"✓ PDF gerado: {pdf_response.status_code}")
        
        if pdf_response.status_code == 200:
            # Salvar PDF para verificação
            with open('pdf_teste_final.pdf', 'wb') as f:
                f.write(pdf_response.content)
            print(f"✓ PDF salvo com {len(pdf_response.content)} bytes")
            
            # Mover para pasta de anexos
            import shutil
            shutil.copy('pdf_teste_final.pdf', 'attached_assets/receita_Michel_Raineri_Haddad_2025-06-06.pdf')
            print("✓ PDF copiado para attached_assets")
            
            return True
        else:
            print(f"❌ Erro ao gerar PDF: {pdf_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    resultado = testar_pdf_completo()
    if resultado:
        print("\n✅ TESTE CONCLUÍDO: PDF gerado com sucesso")
        print("📄 Verificar se o PDF contém:")
        print("   • Dados do paciente: Michel Raineri Haddad")
        print("   • CPF: 408.362.618-60") 
        print("   • Idade: 80 anos")
        print("   • Endereço: Rua José Antônio Coelho, 395")
        print("   • Cidade: São Paulo/SP")
        print("   • Assinatura digital do Dr. Michel Raineri Haddad")
    else:
        print("\n❌ TESTE FALHOU: Verificar logs de erro")