from sqlalchemy import or_
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.db import insert_patient_if_not_exists
from utils.forms import validar_data, sanitizar_entrada
from models import Agendamento
from utils.forms import sanitizar_entrada
from app import db
from datetime import datetime
import logging

def sanitizar_entrada(valor):
    """Sanitiza entrada de usuário"""
    if not valor:
        return ""
    
    # Remove caracteres perigosos
    import re
    valor = re.sub(r'[<>"\']', '', str(valor))
    return valor.strip()


agenda_bp = Blueprint('agenda', __name__)

@agenda_bp.route('/agenda', methods=['GET', 'POST'])
def agenda():
    """Display and manage appointments"""
    if 'usuario' not in session and 'admin_usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            data = sanitizar_entrada(request.form.get('data', ''))
            paciente = sanitizar_entrada(request.form.get('paciente', ''))
            motivo = sanitizar_entrada(request.form.get('motivo', ''))
            
            # Validation
            if not paciente or not data:
                flash('Nome do paciente e data são obrigatórios.', 'error')
                return render_template('agenda.html')
            
            if not validar_data(data):
                flash('Data inválida. Use o formato AAAA-MM-DD.', 'error')
                return render_template('agenda.html')
            
            # Insert patient if not exists
            paciente_id = insert_patient_if_not_exists(paciente)
            
            # Get medico ID safely
            usuario_data = session['usuario']
            if isinstance(usuario_data, dict):
                medico_id = usuario_data.get('id')
            else:
                # Fallback - find medico by name
                from models import Medico
                medico = Medico.query.filter_by(nome=str(usuario_data)).first()
                medico_id = medico.id if medico else 1
            
            # Create appointment
            agendamento = Agendamento(
                data=data,
                paciente=paciente,
                motivo=motivo,
                id_paciente=paciente_id,
                id_medico=medico_id
            )
            
            db.session.add(agendamento)
            db.session.commit()
            
            flash('Agendamento criado com sucesso!', 'success')
            logging.info(f'Appointment created for patient: {paciente} on {data}')
            
        except Exception as e:
            logging.error(f'Appointment creation error: {e}')
            flash('Erro ao criar agendamento.', 'error')
    
    try:
        # Get appointments with filters
        filtro_data = request.args.get('data')
        filtro_paciente = sanitizar_entrada(request.args.get('paciente', ''))
        
        query = Agendamento.query.filter_by(id_medico=session['usuario']['id'])
        
        if filtro_data:
            query = query.filter_by(data=filtro_data)
        
        if filtro_paciente:
            query = query.filter(Agendamento.paciente.like(f'%{filtro_paciente}%'))
        
        agendamentos = query.order_by(Agendamento.data.desc(), Agendamento.created_at.desc()).limit(50).all()
        
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
    if 'usuario' not in session and 'admin_usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        agendamento = Agendamento.query.filter_by(id=id, id_medico=session['usuario']['id']).first()
        if agendamento:
            db.session.delete(agendamento)
            db.session.commit()
            flash('Agendamento excluído com sucesso!', 'success')
            logging.info(f'Appointment {id} deleted by user {session["usuario"]["id"]}')
        else:
            flash('Agendamento não encontrado.', 'error')
        
    except Exception as e:
        logging.error(f'Delete appointment error: {e}')
        flash('Erro ao excluir agendamento.', 'error')
    
    return render_template('agenda.html')

@agenda_bp.route('/agenda/editar/<int:id>', methods=['POST'])
def editar_agendamento(id):
    """Edit appointment"""
    if 'usuario' not in session and 'admin_usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        data = sanitizar_entrada(request.form.get('data', ''))
        paciente = sanitizar_entrada(request.form.get('paciente', ''))
        motivo = sanitizar_entrada(request.form.get('motivo', ''))
        
        # Validation
        if not paciente or not data:
            flash('Nome do paciente e data são obrigatórios.', 'error')
            return render_template('agenda.html')
        
        if not validar_data(data):
            flash('Data inválida. Use o formato AAAA-MM-DD.', 'error')
            return render_template('agenda.html')
        
        # Update appointment
        agendamento = Agendamento.query.filter_by(id=id, id_medico=session['usuario']['id']).first()
        if agendamento:
            agendamento.data = data
            agendamento.paciente = paciente
            agendamento.motivo = motivo
            db.session.commit()
            flash('Agendamento atualizado com sucesso!', 'success')
            logging.info(f'Appointment {id} updated by user {session["usuario"]["id"]}')
        else:
            flash('Agendamento não encontrado.', 'error')
        
    except Exception as e:
        logging.error(f'Edit appointment error: {e}')
        flash('Erro ao editar agendamento.', 'error')
    
    return render_template('agenda.html')
