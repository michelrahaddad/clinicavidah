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
    
    # Get last registered patient for auto-fill
    ultimo_paciente = session.get('ultimo_paciente', {})
    nome_paciente = ultimo_paciente.get('nome', '')
    
    return render_template('exames_lab.html', nome_paciente=nome_paciente)

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
        
        # Get medico ID safely
        usuario_data = session['usuario']
        if isinstance(usuario_data, dict):
            medico_id = usuario_data.get('id')
        else:
            # Fallback - find medico by name
            medico = Medico.query.filter_by(nome=str(usuario_data)).first()
            medico_id = medico.id if medico else 1
        
        medico = Medico.query.get(medico_id)
        
        exame_obj = ExameLab(
            nome_paciente=nome_paciente,
            exames=','.join(exames),
            medico_nome=medico.nome if medico else "Médico não encontrado",
            data=data,
            id_paciente=paciente_id,
            id_medico=medico_id
        )
        
        db.session.add(exame_obj)
        db.session.flush()
        
        # Add to prontuario
        prontuario = Prontuario(
            tipo='exame_lab',
            id_registro=exame_obj.id,
            id_paciente=paciente_id,
            id_medico=medico_id,
            data=data
        )
        
        db.session.add(prontuario)
        db.session.commit()
        
        # Generate PDF
        try:
            pdf_html = render_template('exames_lab_pdf.html',
                                     nome_paciente=nome_paciente,
                                     exames=exames,
                                     medico=medico.nome if medico else "Médico não encontrado",
                                     crm=medico.crm if medico else "CRM não disponível",
                                     assinatura=medico.assinatura if medico else None,
                                     data=data)
            
            pdf_file = weasyprint.HTML(string=pdf_html, base_url=request.url_root).write_pdf()
            
            response = make_response(pdf_file)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename=exames_lab_{nome_paciente}_{data}.pdf'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            flash('Exames laboratoriais salvos e PDF gerado com sucesso!', 'success')
            logging.info(f'Lab exams created for patient: {nome_paciente}')
            
            return response
            
        except Exception as pdf_error:
            logging.error(f'Lab exams PDF generation error: {pdf_error}')
            flash('Exames laboratoriais salvos com sucesso! Erro na geração do PDF.', 'warning')
            return redirect(url_for('exames_lab.exames_lab'))
        
    except Exception as e:
        logging.error(f'Lab exams error: {e}')
        flash('Erro ao salvar exames. Tente novamente.', 'error')
        return redirect(url_for('exames_lab.exames_lab'))

@exames_lab_bp.route('/exames_lab/refazer/<int:id>', methods=['GET'])
def refazer_exame_lab(id):
    """Refill lab exam from prontuario"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        exame = ExameLab.query.get_or_404(id)
        
        # Check if this is a PDF generation request
        if request.args.get('print') == '1':
            return gerar_pdf_reimprimir_exame_lab(exame)
        
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

def gerar_pdf_reimprimir_exame_lab(exame):
    """Generate PDF for existing lab exam with current date"""
    try:
        # Get medico ID safely
        usuario_data = session['usuario']
        if isinstance(usuario_data, dict):
            medico_id = usuario_data.get('id')
        else:
            # Fallback - find medico by name
            medico = Medico.query.filter_by(nome=str(usuario_data)).first()
            medico_id = medico.id if medico else 1
        
        medico = Medico.query.get(medico_id)
        data_atual = datetime.now().strftime('%d/%m/%Y')
        
        # Ensure exames is a list
        exames_list = exame.exames.split(',') if isinstance(exame.exames, str) else exame.exames
        
        pdf_html = render_template('exames_lab_pdf.html',
                                 nome_paciente=exame.nome_paciente,
                                 exames=exames_list,
                                 medico=medico.nome if medico else "Médico não encontrado",
                                 crm=medico.crm if medico else "CRM não disponível",
                                 data=data_atual,
                                 assinatura=medico.assinatura if medico else None)
        
        pdf_file = weasyprint.HTML(string=pdf_html).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=exames_lab_{exame.nome_paciente}_{datetime.now().strftime("%Y%m%d")}.pdf'
        
        return response
        
    except Exception as e:
        logging.error(f'Error generating lab exam PDF: {e}')
        flash('Erro ao gerar PDF do exame.', 'error')
        return redirect(url_for('prontuario.prontuario'))
