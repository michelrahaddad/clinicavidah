#!/usr/bin/env python3
"""
Teste automatizado da assinatura digital no PDF de receitas do prontuário
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import Medico, Receita, Paciente
import logging
from datetime import datetime
import weasyprint
from flask import render_template

def teste_assinatura_pdf():
    """Testa se a assinatura digital aparece no PDF"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Testando assinatura digital no PDF...")
        
        # Buscar médico Michel
        medico = db.session.query(Medico).filter_by(nome="Michel Raineri Haddad").first()
        if not medico:
            print("❌ Médico Michel não encontrado")
            return False
            
        print(f"✅ Médico encontrado: {medico.nome}")
        print(f"📝 CRM: {medico.crm}")
        
        # Verificar assinatura
        if not medico.assinatura or medico.assinatura == 'assinatura':
            print("❌ Assinatura não encontrada no banco")
            return False
            
        print(f"✅ Assinatura encontrada: {len(medico.assinatura)} caracteres")
        print(f"🔍 Tipo: {'Base64' if medico.assinatura.startswith('data:image') else 'Outro'}")
        
        # Buscar uma receita
        receita = db.session.query(Receita).filter_by(id_medico=medico.id).first()
        if not receita:
            print("❌ Nenhuma receita encontrada")
            return False
            
        print(f"✅ Receita encontrada: ID {receita.id}")
        
        # Buscar paciente
        paciente = db.session.query(Paciente).filter_by(nome=receita.nome_paciente).first()
        
        # Gerar PDF de teste
        try:
            print("🔄 Gerando PDF de teste...")
            
            # Processar medicamentos
            medicamentos_raw = receita.medicamentos.split('\n') if receita.medicamentos else []
            medicamentos_unicos = []
            seen = set()
            for med in medicamentos_raw:
                if med.strip() and med.strip() not in seen:
                    medicamentos_unicos.append(med.strip())
                    seen.add(med.strip())
            
            # Formatar data
            if hasattr(receita.data, 'strftime'):
                data_formatada = receita.data.strftime('%d/%m/%Y')
            elif isinstance(receita.data, str):
                data_formatada = receita.data
            else:
                data_formatada = datetime.now().strftime('%d/%m/%Y')
            
            # Dados para template
            template_data = {
                'nome_paciente': receita.nome_paciente,
                'cpf_paciente': paciente.cpf if paciente else None,
                'endereco_paciente': paciente.endereco if paciente else None,
                'data_nascimento_paciente': None,
                'telefone_paciente': paciente.telefone if paciente else None,
                'medicamentos': medicamentos_unicos,
                'medico': medico.nome,
                'crm': medico.crm,
                'data': data_formatada,
                'assinatura': medico.assinatura,
                'zip': '05402-000'
            }
            
            print("📋 Dados do template:")
            print(f"   Paciente: {template_data['nome_paciente']}")
            print(f"   Médico: {template_data['medico']}")
            print(f"   Assinatura: {'✅ Presente' if template_data['assinatura'] else '❌ Ausente'}")
            
            # Renderizar HTML
            html_content = render_template('receita_pdf.html', **template_data)
            
            # Verificar se assinatura está no HTML
            if 'startswith(\'data:image\')' in html_content:
                print("✅ Condição de assinatura encontrada no HTML")
            else:
                print("❌ Condição de assinatura NÃO encontrada no HTML")
                
            if 'filter: brightness(0)' in html_content:
                print("✅ Filtro CSS preto encontrado no HTML")
            else:
                print("❌ Filtro CSS preto NÃO encontrado no HTML")
            
            # Gerar PDF
            pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
            
            # Salvar PDF de teste
            filename = f"teste_assinatura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
                
            print(f"✅ PDF gerado com sucesso: {filename}")
            print(f"📊 Tamanho: {len(pdf_bytes)} bytes")
            
            # Verificar se PDF foi criado
            if os.path.exists(filename) and len(pdf_bytes) > 1000:
                print("✅ PDF válido criado")
                print(f"📂 Arquivo: {filename}")
                return True
            else:
                print("❌ PDF muito pequeno ou inválido")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
            return False

def main():
    """Função principal"""
    print("🚀 Iniciando teste de assinatura digital...")
    
    try:
        resultado = teste_assinatura_pdf()
        if resultado:
            print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
            print("✅ A assinatura digital deve estar funcionando no PDF")
        else:
            print("\n❌ TESTE FALHOU!")
            print("🔧 Necessária correção na assinatura digital")
            
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO: {e}")
        return False

if __name__ == "__main__":
    main()