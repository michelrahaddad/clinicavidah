#!/usr/bin/env python3
"""
Gera uma receita completa e testa a assinatura digital
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

def criar_receita_teste():
    """Cria uma receita de teste e gera PDF com assinatura"""
    app = create_app()
    
    with app.app_context():
        print("Criando receita de teste...")
        
        # Buscar médico Michel
        medico = db.session.query(Medico).filter_by(nome="Michel Raineri Haddad").first()
        if not medico:
            print("Médico não encontrado")
            return False
            
        print(f"Médico: {medico.nome}")
        print(f"Assinatura: {len(medico.assinatura)} caracteres")
        
        # Usar receita existente
        receita_existente = db.session.query(Receita).filter_by(id_medico=medico.id).first()
        if not receita_existente:
            print("Nenhuma receita encontrada")
            return False
            
        print(f"Usando receita existente ID: {receita_existente.id}")
        print(f"Paciente: {receita_existente.nome_paciente}")
        nova_receita = receita_existente
        
        # Gerar PDF usando a mesma lógica do sistema
        try:
            import base64
            import tempfile
            
            # Processar assinatura
            assinatura_para_pdf = None
            temp_sig_path = None
            
            if medico.assinatura and medico.assinatura.startswith('data:image'):
                # Extract base64 data
                header, data = medico.assinatura.split(',', 1)
                image_data = base64.b64decode(data)
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                temp_file.write(image_data)
                temp_file.close()
                temp_sig_path = temp_file.name
                
                # Use file URL for WeasyPrint
                assinatura_para_pdf = f"file://{temp_sig_path}"
                print(f"Assinatura temporária: {temp_sig_path}")
            
            # Processar medicamentos
            medicamentos_raw = nova_receita.medicamentos.split('\n')
            medicamentos_unicos = []
            seen = set()
            for med in medicamentos_raw:
                if med.strip() and med.strip() not in seen:
                    medicamentos_unicos.append(med.strip())
                    seen.add(med.strip())
            
            # Dados para template
            template_data = {
                'nome_paciente': nova_receita.nome_paciente,
                'cpf_paciente': None,
                'endereco_paciente': None,
                'data_nascimento_paciente': None,
                'telefone_paciente': None,
                'medicamentos': medicamentos_unicos,
                'medico': medico.nome,
                'crm': medico.crm,
                'data': nova_receita.data,
                'assinatura': assinatura_para_pdf,
                'zip': '05402-000'
            }
            
            print("Gerando PDF...")
            
            # Renderizar HTML
            html_content = render_template('receita_pdf.html', **template_data)
            
            # Gerar PDF
            pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
            
            # Limpar arquivo temporário
            if temp_sig_path:
                try:
                    os.unlink(temp_sig_path)
                    print("Arquivo temporário removido")
                except:
                    pass
            
            # Salvar PDF
            filename = f"receita_teste_assinatura_{datetime.now().strftime('%H%M%S')}.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
                
            print(f"PDF gerado: {filename}")
            print(f"Tamanho: {len(pdf_bytes)} bytes")
            
            # Verificar conteúdo
            if b'Michel Raineri Haddad' in pdf_bytes:
                print("Nome do médico encontrado no PDF")
            
            if len(pdf_bytes) > 10000:
                print("PDF de tamanho adequado gerado")
                return True
            else:
                print("PDF muito pequeno")
                return False
                
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            return False

def main():
    """Função principal"""
    print("Iniciando teste de receita com assinatura...")
    
    try:
        resultado = criar_receita_teste()
        if resultado:
            print("\nSUCESSO! Receita com assinatura gerada.")
        else:
            print("\nFALHA na geração da receita.")
            
    except Exception as e:
        print(f"\nERRO: {e}")

if __name__ == "__main__":
    main()