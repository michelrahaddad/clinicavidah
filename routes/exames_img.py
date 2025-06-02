from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from utils.db import insert_patient_if_not_exists
from utils.forms import sanitizar_entrada
from models import Medico, ExameImg, Prontuario
from app import db
from datetime import datetime
import logging
import weasyprint

exames_img_bp = Blueprint('exames_img', __name__)

@exames_img_bp.route('/exames_img', methods=['GET'])
def exames_img():
    """Display imaging exams form"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('exames_img.html')

@exames_img_bp.route('/salvar_exames_img', methods=['POST'])
def salvar_exames_img():
    """Save imaging exams and generate PDF"""
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
            return redirect(url_for('exames_img.exames_img'))
        
        if not exames:
            flash('Selecione pelo menos um exame de imagem.', 'error')
            return redirect(url_for('exames_img.exames_img'))
        
        # Insert patient if not exists
        paciente_id = insert_patient_if_not_exists(nome_paciente)
        
        # Save imaging exams
        medico = Medico.query.get(session['usuario']['id'])
        
        exame_obj = ExameImg(
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
            tipo='exame_img',
            id_registro=exame_obj.id,
            id_paciente=paciente_id,
            id_medico=session['usuario']['id'],
            data=data
        )
        
        db.session.add(prontuario)
        db.session.commit()
        
        # Generate PDF
        pdf_html = render_template('exames_img_pdf.html',
                                 nome_paciente=nome_paciente,
                                 exames=exames,
                                 medico=medico.nome,
                                 crm=medico.crm,
                                 data=data)
        
        pdf_file = weasyprint.HTML(string=pdf_html).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=exames_img_{nome_paciente}_{data}.pdf'
        
        flash('Exames de imagem salvos e PDF gerado com sucesso!', 'success')
        logging.info(f'Imaging exams created for patient: {nome_paciente}')
        
        return response
        
    except Exception as e:
        logging.error(f'Imaging exams error: {e}')
        flash('Erro ao salvar exames. Tente novamente.', 'error')
        return redirect(url_for('exames_img.exames_img'))

@exames_img_bp.route('/exames_img/refazer/<int:id>', methods=['GET'])
def refazer_exame_img(id):
    """Refill imaging exam from prontuario"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        exame = ExameImg.query.get_or_404(id)
        
        # Check if this is a PDF generation request
        if request.args.get('print') == '1':
            return gerar_pdf_reimprimir_exame_img(exame)
        
        exames = exame.exames.split(',')
        
        return render_template('exames_img.html',
                             exame={
                                 'nome_paciente': exame.nome_paciente,
                                 'exames': exames
                             },
                             refazer=True)
    except Exception as e:
        logging.error(f'Refill imaging exam error: {e}')
        flash('Erro ao carregar exame.', 'error')
        return redirect(url_for('prontuario.prontuario'))

def gerar_pdf_reimprimir_exame_img(exame):
    """Generate PDF for existing imaging exam with current date"""
    try:
        medico = Medico.query.get(session['usuario']['id'])
        data_atual = datetime.now().strftime('%d/%m/%Y')
        
        pdf_html = render_template('exames_img_pdf.html',
                                 nome_paciente=exame.nome_paciente,
                                 exames=exame.exames.split(','),
                                 medico_nome=medico.nome,
                                 medico_crm=medico.crm,
                                 data=data_atual,
                                 assinatura=medico.assinatura)
        
        pdf_file = weasyprint.HTML(string=pdf_html).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=exames_img_{exame.nome_paciente}_{datetime.now().strftime("%Y%m%d")}.pdf'
        
        return response
        
    except Exception as e:
        logging.error(f'Error generating imaging exam PDF: {e}')
        flash('Erro ao gerar PDF do exame.', 'error')
        return redirect(url_for('prontuario.prontuario'))
