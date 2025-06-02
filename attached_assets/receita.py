from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from utils.db import get_db_connection, insert_patient_if_not_exists
from utils.forms import validar_medicamentos, sanitizar_entrada
from datetime import datetime
import logging
import weasyprint
import io

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
        conn = get_db_connection()
        medico = conn.execute("SELECT nome, crm FROM medicos WHERE id = ?", 
                             (session['usuario']['id'],)).fetchone()
        
        cursor = conn.execute("""
            INSERT INTO receitas (nome_paciente, medicamentos, posologias, duracoes, vias, medico, data, id_paciente, id_medico)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nome_paciente,
            ','.join(medicamentos),
            ','.join(posologias),
            ','.join(duracoes),
            ','.join(vias),
            medico['nome'],
            data,
            paciente_id,
            session['usuario']['id']
        ))
        
        receita_id = cursor.lastrowid
        
        # Add to prontuario
        conn.execute("""
            INSERT INTO prontuario (tipo, id_registro, id_paciente, id_medico, data)
            VALUES (?, ?, ?, ?, ?)
        """, ('receita', receita_id, paciente_id, session['usuario']['id'], data))
        
        conn.commit()
        conn.close()
        
        # Generate PDF
        pdf_html = render_template('receita_pdf.html',
                                 nome_paciente=nome_paciente,
                                 medicamentos=medicamentos,
                                 posologias=posologias,
                                 duracoes=duracoes,
                                 vias=vias,
                                 medico=medico['nome'],
                                 crm=medico['crm'],
                                 data=data,
                                 zip=zip)
        
        pdf_file = weasyprint.HTML(string=pdf_html).write_pdf()
        
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

@receita_bp.route('/refazer/receita/<int:id>', methods=['GET'])
def refazer_receita(id):
    """Refill prescription from prontuario"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        conn = get_db_connection()
        receita = conn.execute("SELECT * FROM receitas WHERE id = ?", (id,)).fetchone()
        conn.close()
        
        if not receita:
            flash('Receita não encontrada.', 'error')
            return redirect(url_for('prontuario.prontuario'))
        
        medicamentos = receita['medicamentos'].split(',')
        posologias = receita['posologias'].split(',')
        duracoes = receita['duracoes'].split(',')
        vias = receita['vias'].split(',')
        
        return render_template('receita.html',
                             receita={
                                 'nome_paciente': receita['nome_paciente'],
                                 'medicamentos': [{'nome': m, 'posologia': p, 'duracao': d, 'via': v} 
                                                for m, p, d, v in zip(medicamentos, posologias, duracoes, vias)]
                             },
                             refazer=True)
    except Exception as e:
        logging.error(f'Refill prescription error: {e}')
        flash('Erro ao carregar receita.', 'error')
        return redirect(url_for('prontuario.prontuario'))
