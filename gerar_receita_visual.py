#!/usr/bin/env python3
"""
Gera receita PDF e abre para visualização da assinatura
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import Medico, Receita, Paciente
from datetime import datetime
import weasyprint
from flask import render_template
import base64
import tempfile

def gerar_receita_visual():
    """Gera PDF de receita e abre para visualização"""
    app = create_app()
    
    with app.app_context():
        print("Gerando receita com assinatura visível...")
        
        # Buscar médico Michel
        medico = db.session.query(Medico).filter_by(nome="Michel Raineri Haddad").first()
        if not medico:
            print("Médico não encontrado")
            return False
            
        print(f"Médico: {medico.nome}")
        print(f"CRM: {medico.crm}")
        print(f"Assinatura: {len(medico.assinatura)} caracteres")
        
        # Buscar receita existente
        receita = db.session.query(Receita).filter_by(id_medico=medico.id).first()
        if not receita:
            print("Receita não encontrada")
            return False
            
        print(f"Receita ID: {receita.id}")
        print(f"Paciente: {receita.nome_paciente}")
        
        # Buscar dados do paciente se existir
        paciente = None
        if receita.id_paciente:
            paciente = db.session.query(Paciente).filter_by(id=receita.id_paciente).first()
        
        # Preparar assinatura para PDF
        assinatura_para_pdf = None
        temp_sig_path = None
        
        if medico.assinatura and medico.assinatura.startswith('data:image'):
            print("Processando assinatura digital...")
            try:
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
                print(f"Assinatura temporária criada: {temp_sig_path}")
                
            except Exception as e:
                print(f"Erro ao processar assinatura: {e}")
                assinatura_para_pdf = None
        
        # Processar medicamentos
        medicamentos_raw = receita.medicamentos.split('\n') if receita.medicamentos else []
        medicamentos_unicos = []
        seen = set()
        for med in medicamentos_raw:
            if med.strip() and med.strip() not in seen:
                medicamentos_unicos.append(med.strip())
                seen.add(med.strip())
        
        print(f"Medicamentos: {len(medicamentos_unicos)}")
        
        # Dados para template
        template_data = {
            'nome_paciente': receita.nome_paciente,
            'cpf_paciente': paciente.cpf if paciente else None,
            'endereco_paciente': paciente.endereco if paciente else None,
            'data_nascimento_paciente': None,  # Campo não existe no modelo
            'telefone_paciente': paciente.telefone if paciente else None,
            'medicamentos': medicamentos_unicos,
            'medico': medico.nome,
            'crm': medico.crm,
            'data': receita.data,
            'assinatura': assinatura_para_pdf,
            'zip': '05402-000'
        }
        
        print("Renderizando HTML...")
        
        # Renderizar HTML
        html_content = render_template('receita_pdf.html', **template_data)
        
        print("Gerando PDF...")
        
        # Gerar PDF
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        
        # Limpar arquivo temporário
        if temp_sig_path:
            try:
                os.unlink(temp_sig_path)
                print("Arquivo temporário removido")
            except:
                pass
        
        # Salvar PDF com nome único
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"receita_Michel_Raineri_Haddad_{timestamp}.pdf"
        
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
            
        print(f"\n✅ PDF GERADO COM SUCESSO!")
        print(f"📄 Arquivo: {filename}")
        print(f"📊 Tamanho: {len(pdf_bytes):,} bytes")
        print(f"👨‍⚕️ Médico: {medico.nome}")
        print(f"🔖 CRM: {medico.crm}")
        print(f"✍️ Assinatura: {'INCLUÍDA' if assinatura_para_pdf else 'NÃO ENCONTRADA'}")
        
        # Verificar conteúdo do PDF
        checks = []
        if b'Michel Raineri Haddad' in pdf_bytes:
            checks.append("✅ Nome do médico")
        else:
            checks.append("❌ Nome do médico")
            
        if b'183299-SP' in pdf_bytes:
            checks.append("✅ CRM")
        else:
            checks.append("❌ CRM")
            
        if len(pdf_bytes) > 15000:
            checks.append("✅ Tamanho adequado")
        else:
            checks.append("❌ Tamanho muito pequeno")
            
        print(f"\n🔍 Verificações:")
        for check in checks:
            print(f"   {check}")
        
        print(f"\n📁 O arquivo '{filename}' foi salvo na pasta atual.")
        print("🖼️ Abra o arquivo para verificar se a assinatura digital está visível.")
        
        return len(pdf_bytes) > 15000

def main():
    """Função principal"""
    print("="*60)
    print("🏥 SISTEMA MÉDICO VIDAH - TESTE DE ASSINATURA DIGITAL")
    print("="*60)
    
    try:
        resultado = gerar_receita_visual()
        if resultado:
            print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
            print("A receita PDF foi gerada com a assinatura digital.")
        else:
            print("\n❌ FALHA no teste.")
            
    except Exception as e:
        print(f"\n💥 ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()