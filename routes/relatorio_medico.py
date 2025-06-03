from flask import Blueprint, render_template, redirect, url_for, flash, request, session, make_response
from models import RelatorioMedico, Medico, Paciente, Cid10
from app import db
from sqlalchemy import text
from utils.forms import sanitizar_entrada
from datetime import datetime
import logging
import weasyprint

relatorio_medico_bp = Blueprint('relatorio_medico', __name__)

@relatorio_medico_bp.route('/relatorio_medico', methods=['GET'])
def relatorio_medico():
    """Display medical report form"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    # Get last registered patient for auto-fill
    ultimo_paciente = session.get('ultimo_paciente', {})
    nome_paciente = ultimo_paciente.get('nome', '')
    
    return render_template('relatorio_medico.html', nome_paciente=nome_paciente)

@relatorio_medico_bp.route('/salvar_relatorio_medico', methods=['POST'])
def salvar_relatorio_medico():
    """Save medical report and generate PDF"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get form data
        data = datetime.now().strftime('%Y-%m-%d')
        nome_paciente = sanitizar_entrada(request.form.get('nome_paciente', ''))
        cid_codigo = sanitizar_entrada(request.form.get('cid_codigo', 'I10.0'))
        cid_descricao = sanitizar_entrada(request.form.get('cid_descricao', 'Hipertensão arterial'))
        relatorio_texto = sanitizar_entrada(request.form.get('relatorio_texto', ''))
        
        if not all([nome_paciente, relatorio_texto]):
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return redirect(url_for('relatorio_medico.relatorio_medico'))
        
        # Get doctor info
        medico = Medico.query.filter_by(id=session['usuario']['id']).first()
        if not medico:
            flash('Médico não encontrado.', 'error')
            return redirect(url_for('relatorio_medico.relatorio_medico'))
        
        # Get or create patient
        from utils.db import insert_patient_if_not_exists
        paciente_id = insert_patient_if_not_exists(nome_paciente)
        
        # Create medical report using SQL insert
        db.session.execute(
            text("""
            INSERT INTO relatorios_medicos 
            (nome_paciente, cid_codigo, cid_descricao, relatorio_texto, medico_nome, data, id_paciente, id_medico, created_at)
            VALUES (:nome_paciente, :cid_codigo, :cid_descricao, :relatorio_texto, :medico_nome, :data, :id_paciente, :id_medico, :created_at)
            """),
            {
                'nome_paciente': nome_paciente,
                'cid_codigo': cid_codigo,
                'cid_descricao': cid_descricao,
                'relatorio_texto': relatorio_texto,
                'medico_nome': medico.nome,
                'data': data,
                'id_paciente': paciente_id,
                'id_medico': medico.id,
                'created_at': datetime.now()
            }
        )
        
        # Get the ID of the inserted record
        result = db.session.execute(text("SELECT lastval()"))
        relatorio_id = result.scalar()
        db.session.commit()
        
        # Generate PDF
        pdf_html = render_template('relatorio_medico_pdf.html',
                                 nome_paciente=nome_paciente,
                                 cid_codigo=cid_codigo,
                                 cid_descricao=cid_descricao,
                                 relatorio_texto=relatorio_texto,
                                 medico=medico.nome,
                                 crm=medico.crm,
                                 assinatura=medico.assinatura,
                                 data=data)
        
        pdf_file = weasyprint.HTML(string=pdf_html).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=relatorio_medico_{nome_paciente}_{data}.pdf'
        
        flash('Relatório médico salvo e PDF gerado com sucesso!', 'success')
        logging.info(f'Medical report created for patient: {nome_paciente}')
        
        return response
        
    except Exception as e:
        logging.error(f'Medical report error: {e}')
        flash('Erro ao salvar relatório. Tente novamente.', 'error')
        return redirect(url_for('relatorio_medico.relatorio_medico'))