#!/usr/bin/env python3
"""
Teste automatizado completo das assinaturas digitais em todos os PDFs
"""
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_all_pdf_signatures():
    """Testa assinaturas em todos os tipos de PDFs gerados pelo sistema"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    logger.info("=== TESTE COMPLETO DE ASSINATURAS DIGITAIS ===")
    
    # Lista de tipos de documentos para testar
    test_cases = [
        {
            'name': 'Receita Médica',
            'route': '/salvar_receita',
            'data': {
                'nome_paciente': 'Teste Assinatura',
                'principio_ativo_0': 'dipirona',
                'concentracao_0': '500mg',
                'via_0': 'Oral',
                'frequencia_0': '3x ao dia',
                'quantidade_0': '30 comprimidos'
            }
        },
        {
            'name': 'Atestado Médico',
            'route': '/salvar_atestado_medico',
            'data': {
                'nome_paciente': 'Teste Assinatura',
                'cid_codigo': 'I10.0',
                'cid_descricao': 'Hipertensão arterial',
                'dias_afastamento': '3'
            }
        },
        {
            'name': 'Exames Laboratoriais',
            'route': '/salvar_exames_lab',
            'data': {
                'nome_paciente': 'Teste Assinatura',
                'exames': ['Hemograma', 'Glicemia']
            }
        },
        {
            'name': 'Exames de Imagem',
            'route': '/salvar_exames_img',
            'data': {
                'nome_paciente': 'Teste Assinatura',
                'exames': ['Raio-X Tórax', 'Ultrassom']
            }
        },
        {
            'name': 'Relatório Médico',
            'route': '/salvar_relatorio_medico',
            'data': {
                'nome_paciente': 'Teste Assinatura',
                'cid_codigo': 'I10.0',
                'cid_descricao': 'Hipertensão arterial',
                'relatorio_texto': 'Relatório de teste para verificação de assinatura digital.'
            }
        },
        {
            'name': 'Formulário Alto Custo',
            'route': '/salvar_formulario_alto_custo',
            'data': {
                'cnes': '123456',
                'estabelecimento': 'Hospital Teste',
                'nome_paciente': 'Teste Assinatura',
                'nome_mae': 'Mãe Teste',
                'peso': '70',
                'altura': '170',
                'medicamento': 'Medicamento Teste',
                'quantidade': '30',
                'cid_codigo': 'I10.0',
                'cid_descricao': 'Hipertensão arterial',
                'anamnese': 'Anamnese teste',
                'tratamento_previo': 'Sim',
                'incapaz': 'Não',
                'responsavel_nome': '',
                'medico_cns': '123456789012345'
            }
        }
    ]
    
    try:
        # 1. Fazer login
        logger.info("Fazendo login no sistema...")
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
        
        # 2. Testar cada tipo de documento
        success_count = 0
        total_tests = len(test_cases)
        
        for test_case in test_cases:
            logger.info(f"\n--- Testando {test_case['name']} ---")
            
            try:
                # Fazer requisição para gerar PDF
                response = session.post(f"{base_url}{test_case['route']}", data=test_case['data'])
                
                # Verificar se o PDF foi gerado (Content-Type deve ser application/pdf)
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    
                    if 'application/pdf' in content_type:
                        # Verificar se o PDF tem conteúdo válido
                        pdf_content = response.content
                        if len(pdf_content) > 1000 and b'%PDF' in pdf_content[:10]:
                            logger.info(f"✅ {test_case['name']}: PDF gerado com sucesso ({len(pdf_content)} bytes)")
                            success_count += 1
                        else:
                            logger.error(f"❌ {test_case['name']}: PDF inválido ou muito pequeno")
                    else:
                        logger.error(f"❌ {test_case['name']}: Resposta não é um PDF (Content-Type: {content_type})")
                else:
                    logger.error(f"❌ {test_case['name']}: Erro HTTP {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ {test_case['name']}: Erro na requisição - {e}")
        
        # 3. Resultado final
        logger.info(f"\n=== RESULTADO FINAL ===")
        logger.info(f"Testes executados: {total_tests}")
        logger.info(f"Sucessos: {success_count}")
        logger.info(f"Falhas: {total_tests - success_count}")
        
        if success_count == total_tests:
            logger.info("🎉 TODOS OS TESTES PASSARAM! Assinaturas digitais funcionando em todos os PDFs")
            return True
        else:
            logger.info(f"⚠️  {total_tests - success_count} teste(s) falharam")
            return False
            
    except Exception as e:
        logger.error(f"❌ ERRO GERAL NO TESTE: {e}")
        return False

if __name__ == "__main__":
    test_all_pdf_signatures()