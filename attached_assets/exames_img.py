from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from utils.db import get_db_connection, insert_patient_if_not_exists
from utils.forms import sanitizar_entrada
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
        conn = get_db_connection()
        medico = conn.execute("SELECT nome, crm FROM medicos WHERE id = ?", 
                             (session['usuario']['id'],)).fetchone()
        
        cursor = conn.execute("""
            INSERT INTO exames_img (nome_paciente, exames, medico, data, id_paciente, id_medico)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            nome_paciente,
            ','.join(exames),
            medico['nome'],
            data,
            paciente_id,
            session['usuario']['id']
        ))
        
        exame_id = cursor.lastrowid
        
        # Add to prontuario
        conn.execute("""
            INSERT INTO prontuario (tipo, id_registro, id_paciente, id_medico, data)
            VALUES (?, ?, ?, ?, ?)
        """, ('exame_img', exame_id, paciente_id, session['usuario']['id'], data))
        
        conn.commit()
        conn.close()
        
        # Generate PDF
        pdf_html = render_template('exames_img_pdf.html',
                                 nome_paciente=nome_paciente,
                                 exames=exames,
                                 medico=medico['nome'],
                                 crm=medico['crm'],
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

@exames_img_bp.route('/refazer/exame_img/<int:id>', methods=['GET'])
def refazer_exame_img(id):
    """Refill imaging exam from prontuario"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        conn = get_db_connection()
        exame = conn.execute("SELECT * FROM exames_img WHERE id = ?", (id,)).fetchone()
        conn.close()
        
        if not exame:
            flash('Exame não encontrado.', 'error')
            return redirect(url_for('prontuario.prontuario'))
        
        exames = exame['exames'].split(',')
        
        return render_template('exames_img.html',
                             exame={
                                 'nome_paciente': exame['nome_paciente'],
                                 'exames': exames
                             },
                             refazer=True)
    except Exception as e:
        logging.error(f'Refill imaging exam error: {e}')
        flash('Erro ao carregar exame.', 'error')
        return redirect(url_for('prontuario.prontuario'))
