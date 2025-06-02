from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.db import get_db_connection, insert_patient_if_not_exists
from utils.forms import validar_data, sanitizar_entrada
import logging

agenda_bp = Blueprint('agenda', __name__)

@agenda_bp.route('/agenda', methods=['GET', 'POST'])
def agenda():
    """Display and manage appointments"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        try:
            data = sanitizar_entrada(request.form.get('data', ''))
            paciente = sanitizar_entrada(request.form.get('paciente', ''))
            motivo = sanitizar_entrada(request.form.get('motivo', ''))
            
            # Validation
            if not paciente or not data:
                flash('Nome do paciente e data são obrigatórios.', 'error')
                return redirect(url_for('agenda.agenda'))
            
            if not validar_data(data):
                flash('Data inválida. Use o formato AAAA-MM-DD.', 'error')
                return redirect(url_for('agenda.agenda'))
            
            # Insert patient if not exists
            paciente_id = insert_patient_if_not_exists(paciente)
            
            # Create appointment
            conn.execute("""
                INSERT INTO agenda (data, paciente, motivo, id_paciente, id_medico)
                VALUES (?, ?, ?, ?, ?)
            """, (data, paciente, motivo, paciente_id, session['usuario']['id']))
            
            conn.commit()
            flash('Agendamento criado com sucesso!', 'success')
            logging.info(f'Appointment created for patient: {paciente} on {data}')
            
        except Exception as e:
            logging.error(f'Appointment creation error: {e}')
            flash('Erro ao criar agendamento.', 'error')
    
    try:
        # Get appointments with filters
        filtro_data = request.args.get('data')
        filtro_paciente = sanitizar_entrada(request.args.get('paciente', ''))
        
        query = "SELECT * FROM agenda WHERE id_medico = ?"
        params = [session['usuario']['id']]
        
        if filtro_data:
            query += " AND data = ?"
            params.append(filtro_data)
        
        if filtro_paciente:
            query += " AND paciente LIKE ?"
            params.append(f'%{filtro_paciente}%')
        
        query += " ORDER BY data DESC, created_at DESC LIMIT 50"
        
        agendamentos = conn.execute(query, params).fetchall()
        conn.close()
        
        return render_template('agenda.html', 
                             agendamentos=agendamentos,
                             filtro_data=filtro_data,
                             filtro_paciente=filtro_paciente)
                             
    except Exception as e:
        logging.error(f'Agenda display error: {e}')
        flash('Erro ao carregar agenda.', 'error')
        return render_template('agenda.html', agendamentos=[])

@agenda_bp.route('/agenda/excluir/<int:id>', methods=['POST'])
def excluir_agendamento(id):
    """Delete appointment"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM agenda WHERE id = ? AND id_medico = ?", 
                    (id, session['usuario']['id']))
        conn.commit()
        conn.close()
        
        flash('Agendamento excluído com sucesso!', 'success')
        logging.info(f'Appointment {id} deleted by user {session["usuario"]["id"]}')
        
    except Exception as e:
        logging.error(f'Delete appointment error: {e}')
        flash('Erro ao excluir agendamento.', 'error')
    
    return redirect(url_for('agenda.agenda'))

@agenda_bp.route('/agenda/editar/<int:id>', methods=['POST'])
def editar_agendamento(id):
    """Edit appointment"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        data = sanitizar_entrada(request.form.get('data', ''))
        paciente = sanitizar_entrada(request.form.get('paciente', ''))
        motivo = sanitizar_entrada(request.form.get('motivo', ''))
        
        # Validation
        if not paciente or not data:
            flash('Nome do paciente e data são obrigatórios.', 'error')
            return redirect(url_for('agenda.agenda'))
        
        if not validar_data(data):
            flash('Data inválida. Use o formato AAAA-MM-DD.', 'error')
            return redirect(url_for('agenda.agenda'))
        
        # Update appointment
        conn = get_db_connection()
        conn.execute("""
            UPDATE agenda SET data = ?, paciente = ?, motivo = ?
            WHERE id = ? AND id_medico = ?
        """, (data, paciente, motivo, id, session['usuario']['id']))
        
        conn.commit()
        conn.close()
        
        flash('Agendamento atualizado com sucesso!', 'success')
        logging.info(f'Appointment {id} updated by user {session["usuario"]["id"]}')
        
    except Exception as e:
        logging.error(f'Edit appointment error: {e}')
        flash('Erro ao editar agendamento.', 'error')
    
    return redirect(url_for('agenda.agenda'))
