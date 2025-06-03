from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from utils.db import get_db_connection, insert_patient_if_not_exists
from utils.forms import validar_medicamentos, sanitizar_entrada
from models import Medico, Receita, Prontuario
from app import db
from datetime import datetime
import logging
import weasyprint

receita_bp = Blueprint('receita', __name__)

@receita_bp.route('/receita', methods=['GET'])
def receita():
    """Display prescription form"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('receita.html')

@receita_bp.route('/salvar_receita', methods=['POST'])
def salvar_receita():
    """Save prescription and generate PDF"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get form data
        data = datetime.now().strftime('%Y-%m-%d')
        nome_paciente = sanitizar_entrada(request.form.get('nome_paciente', ''))
        medicamentos = [sanitizar_entrada(m) for m in request.form.getlist('medicamento[]')]
        posologias = [sanitizar_entrada(p) for p in request.form.getlist('posologia[]')]
        duracoes = [sanitizar_entrada(d) for d in request.form.getlist('duracao[]')]
        vias = [sanitizar_entrada(v) for v in request.form.getlist('via[]')]
        
        # Validation
        if not nome_paciente:
            flash('Nome do paciente é obrigatório.', 'error')
            return redirect(url_for('receita.receita'))
        
        is_valid, message = validar_medicamentos(medicamentos, posologias, duracoes, vias)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('receita.receita'))
        
        # Insert patient if not exists
        paciente_id = insert_patient_if_not_exists(nome_paciente)
        
        # Save prescription
        medico = Medico.query.get(session['usuario']['id'])
        
        receita_obj = Receita(
            nome_paciente=nome_paciente,
            medicamentos=','.join(medicamentos),
            posologias=','.join(posologias),
            duracoes=','.join(duracoes),
            vias=','.join(vias),
            medico_nome=medico.nome,
            data=data,
            id_paciente=paciente_id,
            id_medico=session['usuario']['id']
        )
        
        db.session.add(receita_obj)
        db.session.flush()
        
        # Add to prontuario
        prontuario = Prontuario(
            tipo='receita',
            id_registro=receita_obj.id,
            id_paciente=paciente_id,
            id_medico=session['usuario']['id'],
            data=data
        )
        
        db.session.add(prontuario)
        db.session.commit()
        
        # Generate PDF
        logging.info(f'Starting PDF generation for prescription: {nome_paciente}')
        pdf_html = render_template('receita_pdf.html',
                                 nome_paciente=nome_paciente,
                                 medicamentos=medicamentos,
                                 posologias=posologias,
                                 duracoes=duracoes,
                                 vias=vias,
                                 medico=medico.nome,
                                 crm=medico.crm,
                                 assinatura=medico.assinatura,
                                 data=data,
                                 zip=zip)
        
        logging.info('HTML template rendered successfully')
        pdf_file = weasyprint.HTML(string=pdf_html).write_pdf()
        logging.info('PDF file generated successfully')
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=receita_{nome_paciente}_{data}.pdf'
        
        flash('Receita salva e PDF gerado com sucesso!', 'success')
        logging.info(f'Prescription created for patient: {nome_paciente}')
        
        return response
        
    except Exception as e:
        logging.error(f'Prescription error: {e}')
        flash('Erro ao salvar receita. Tente novamente.', 'error')
        return redirect(url_for('receita.receita'))

@receita_bp.route('/receita/refazer/<int:id>', methods=['GET'])
def refazer_receita(id):
    """Refill prescription from prontuario"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        receita_obj = Receita.query.get_or_404(id)
        
        # Check if this is a PDF generation request
        if request.args.get('print') == '1':
            return gerar_pdf_reimprimir_receita(receita_obj)
        
        medicamentos = receita_obj.medicamentos.split(',')
        posologias = receita_obj.posologias.split(',')
        duracoes = receita_obj.duracoes.split(',')
        vias = receita_obj.vias.split(',')
        
        return render_template('receita.html',
                             receita={
                                 'nome_paciente': receita_obj.nome_paciente,
                                 'medicamentos': [{'nome': m, 'posologia': p, 'duracao': d, 'via': v} 
                                                for m, p, d, v in zip(medicamentos, posologias, duracoes, vias)]
                             },
                             refazer=True)
    except Exception as e:
        logging.error(f'Refill prescription error: {e}')
        flash('Erro ao carregar receita.', 'error')
        return redirect(url_for('prontuario.prontuario'))

def gerar_pdf_reimprimir_receita(receita_obj):
    """Generate PDF for existing prescription with current date"""
    try:
        medico = Medico.query.get(session['usuario']['id'])
        data_atual = datetime.now().strftime('%d/%m/%Y')
        
        pdf_html = render_template('receita_pdf.html',
                                 nome_paciente=receita_obj.nome_paciente,
                                 medicamentos=receita_obj.medicamentos.split(','),
                                 posologias=receita_obj.posologias.split(','),
                                 duracoes=receita_obj.duracoes.split(','),
                                 vias=receita_obj.vias.split(','),
                                 medico=medico.nome,
                                 crm=medico.crm,
                                 data=data_atual,
                                 assinatura=medico.assinatura,
                                 zip=zip)
        
        pdf_file = weasyprint.HTML(string=pdf_html).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=receita_{receita_obj.nome_paciente}_{datetime.now().strftime("%Y%m%d")}.pdf'
        
        return response
        
    except Exception as e:
        logging.error(f'Error generating prescription PDF: {e}')
        flash('Erro ao gerar PDF da receita.', 'error')
        return redirect(url_for('prontuario.prontuario'))
