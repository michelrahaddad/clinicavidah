from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from utils.db import insert_patient_if_not_exists
from utils.forms import sanitizar_entrada
from models import Medico, ExameLab, Prontuario
from app import db
from datetime import datetime
import logging
import weasyprint

exames_lab_bp = Blueprint('exames_lab', __name__)

@exames_lab_bp.route('/exames_lab', methods=['GET'])
def exames_lab():
    """Display lab exams form"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('exames_lab.html')

@exames_lab_bp.route('/salvar_exames_lab', methods=['POST'])
def salvar_exames_lab():
    """Save lab exams and generate PDF"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get form data
        data = datetime.now().strftime('%Y-%m-%d')
        nome_paciente = sanitizar_entrada(request.form.get('nome_paciente', ''))
        exames = request.form.getlist('exames[]')
        
        # Validation
        if not nome_paciente:
            flash('Nome do paciente é obrigatório.', 'error')
            return redirect(url_for('exames_lab.exames_lab'))
        
        if not exames:
            flash('Selecione pelo menos um exame laboratorial.', 'error')
            return redirect(url_for('exames_lab.exames_lab'))
        
        # Insert patient if not exists
        paciente_id = insert_patient_if_not_exists(nome_paciente)
        
        # Save lab exams
        medico = Medico.query.get(session['usuario']['id'])
        
        exame_obj = ExameLab(
            nome_paciente=nome_paciente,
            exames=','.join(exames),
            medico_nome=medico.nome,
            data=data,
            id_paciente=paciente_id,
            id_medico=session['usuario']['id']
        )
        
        db.session.add(exame_obj)
        db.session.flush()
        
        # Add to prontuario
        prontuario = Prontuario(
            tipo='exame_lab',
            id_registro=exame_obj.id,
            id_paciente=paciente_id,
            id_medico=session['usuario']['id'],
            data=data
        )
        
        db.session.add(prontuario)
        db.session.commit()
        
        # Generate PDF
        pdf_html = render_template('exames_lab_pdf.html',
                                 nome_paciente=nome_paciente,
                                 exames=exames,
                                 medico=medico.nome,
                                 crm=medico.crm,
                                 data=data)
        
        pdf_file = weasyprint.HTML(string=pdf_html).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=exames_lab_{nome_paciente}_{data}.pdf'
        
        flash('Exames laboratoriais salvos e PDF gerado com sucesso!', 'success')
        logging.info(f'Lab exams created for patient: {nome_paciente}')
        
        return response
        
    except Exception as e:
        logging.error(f'Lab exams error: {e}')
        flash('Erro ao salvar exames. Tente novamente.', 'error')
        return redirect(url_for('exames_lab.exames_lab'))

@exames_lab_bp.route('/refazer/exame_lab/<int:id>', methods=['GET'])
def refazer_exame_lab(id):
    """Refill lab exam from prontuario"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        exame = ExameLab.query.get_or_404(id)
        exames = exame.exames.split(',')
        
        return render_template('exames_lab.html',
                             exame={
                                 'nome_paciente': exame.nome_paciente,
                                 'exames': exames
                             },
                             refazer=True)
    except Exception as e:
        logging.error(f'Refill lab exam error: {e}')
        flash('Erro ao carregar exame.', 'error')
        return redirect(url_for('prontuario.prontuario'))
