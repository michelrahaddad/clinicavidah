from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from models import Consulta, Paciente, Medico
from main import db
from datetime import datetime, timedelta
import logging

def sanitizar_entrada(valor):
    """Sanitiza entrada de usuário"""
    if not valor:
        return ""
    import re
    valor = re.sub(r'[<>"\']', '', str(valor))
    return valor.strip()

consultas_bp = Blueprint('consultas', __name__)

@consultas_bp.route('/consultas')
def listar_consultas():
    """Lista todas as consultas agendadas"""
    try:
        # Verifica autenticação
        if not session.get('usuario') and not session.get('admin_usuario'):
            flash('Acesso negado. Faça login primeiro.', 'error')
            return redirect(url_for('auth.login'))
        
        # Obtém filtros da URL
        filtro_status = request.args.get('status', '')
        filtro_medico = request.args.get('medico', '')
        filtro_data = request.args.get('data', '')
        
        # Consulta base
        query = db.session.query(Consulta).join(Paciente).join(Medico)
        
        # Aplica filtros
        if filtro_status:
            query = query.filter(Consulta.status == filtro_status)
        
        if filtro_medico:
            query = query.filter(Medico.nome.ilike(f'%{filtro_medico}%'))
        
        if filtro_data:
            try:
                data_filtro = datetime.strptime(filtro_data, '%Y-%m-%d').date()
                query = query.filter(Consulta.data_consulta == data_filtro)
            except:
                pass
        
        # Ordena por data
        consultas = query.order_by(Consulta.data_consulta.desc(), Consulta.horario.desc()).all()
        
        # Busca médicos para filtro
        medicos = db.session.query(Medico).all()
        
        return render_template('consultas/listar.html', 
                             consultas=consultas,
                             medicos=medicos,
                             filtro_status=filtro_status,
                             filtro_medico=filtro_medico,
                             filtro_data=filtro_data)
        
    except Exception as e:
        logging.error(f"Erro ao listar consultas: {e}")
        flash('Erro ao carregar consultas', 'error')
        return redirect(url_for('dashboard'))

@consultas_bp.route('/consultas/nova', methods=['GET', 'POST'])
def nova_consulta():
    """Agenda nova consulta"""
    try:
        if request.method == 'POST':
            # Coleta dados do formulário
            paciente_nome = sanitizar_entrada(request.form.get('paciente_nome'))
            medico_id = request.form.get('medico_id')
            data_consulta = request.form.get('data_consulta')
            horario = request.form.get('horario')
            tipo_consulta = sanitizar_entrada(request.form.get('tipo_consulta'))
            observacoes = sanitizar_entrada(request.form.get('observacoes'))
            
            # Validações
            if not all([paciente_nome, medico_id, data_consulta, horario]):
                flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
                return redirect(url_for('consultas.nova_consulta'))
            
            # Busca ou cria paciente
            paciente = db.session.query(Paciente).filter_by(nome=paciente_nome).first()
            if not paciente:
                paciente = Paciente(
                    nome=paciente_nome,
                    data_nascimento=datetime.now().date(),
                    created_at=datetime.now()
                )
                db.session.add(paciente)
                db.session.flush()
            
            # Cria consulta
            consulta = Consulta(
                paciente_id=paciente.id,
                medico_id=medico_id,
                data_consulta=datetime.strptime(data_consulta, '%Y-%m-%d').date(),
                horario=datetime.strptime(horario, '%H:%M').time(),
                tipo_consulta=tipo_consulta,
                status='agendada',
                observacoes=observacoes,
                created_at=datetime.now()
            )
            
            db.session.add(consulta)
            db.session.commit()
            
            flash('Consulta agendada com sucesso!', 'success')
            return redirect(url_for('consultas.listar_consultas'))
        
        # GET - Exibe formulário
        medicos = db.session.query(Medico).all()
        return render_template('consultas/nova.html', medicos=medicos)
        
    except Exception as e:
        logging.error(f"Erro ao agendar consulta: {e}")
        db.session.rollback()
        flash('Erro ao agendar consulta', 'error')
        return redirect(url_for('consultas.listar_consultas'))

@consultas_bp.route('/consultas/<int:consulta_id>/editar', methods=['GET', 'POST'])
def editar_consulta(consulta_id):
    """Edita consulta existente"""
    try:
        consulta = db.session.query(Consulta).get_or_404(consulta_id)
        
        if request.method == 'POST':
            # Atualiza dados da consulta
            consulta.data_consulta = datetime.strptime(request.form.get('data_consulta'), '%Y-%m-%d').date()
            consulta.horario = datetime.strptime(request.form.get('horario'), '%H:%M').time()
            consulta.tipo_consulta = sanitizar_entrada(request.form.get('tipo_consulta'))
            consulta.status = request.form.get('status')
            consulta.observacoes = sanitizar_entrada(request.form.get('observacoes'))
            
            db.session.commit()
            flash('Consulta atualizada com sucesso!', 'success')
            return redirect(url_for('consultas.listar_consultas'))
        
        # GET - Exibe formulário de edição
        medicos = db.session.query(Medico).all()
        return render_template('consultas/editar.html', 
                             consulta=consulta, 
                             medicos=medicos)
        
    except Exception as e:
        logging.error(f"Erro ao editar consulta: {e}")
        db.session.rollback()
        flash('Erro ao editar consulta', 'error')
        return redirect(url_for('consultas.listar_consultas'))

@consultas_bp.route('/consultas/<int:consulta_id>/cancelar', methods=['POST'])
def cancelar_consulta(consulta_id):
    """Cancela consulta"""
    try:
        consulta = db.session.query(Consulta).get_or_404(consulta_id)
        consulta.status = 'cancelada'
        
        db.session.commit()
        flash('Consulta cancelada com sucesso!', 'success')
        
    except Exception as e:
        logging.error(f"Erro ao cancelar consulta: {e}")
        db.session.rollback()
        flash('Erro ao cancelar consulta', 'error')
    
    return redirect(url_for('consultas.listar_consultas'))

@consultas_bp.route('/api/consultas/horarios/<int:medico_id>/<data>')
def horarios_disponiveis(medico_id, data):
    """API para buscar horários disponíveis"""
    try:
        data_consulta = datetime.strptime(data, '%Y-%m-%d').date()
        
        # Horários padrão do consultório
        horarios_padrao = [
            '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
            '11:00', '11:30', '14:00', '14:30', '15:00', '15:30',
            '16:00', '16:30', '17:00', '17:30'
        ]
        
        # Busca horários já ocupados
        ocupados = db.session.query(Consulta.horario).filter_by(
            medico_id=medico_id,
            data_consulta=data_consulta,
            status='agendada'
        ).all()
        
        horarios_ocupados = [h.horario.strftime('%H:%M') for h in ocupados]
        horarios_livres = [h for h in horarios_padrao if h not in horarios_ocupados]
        
        return jsonify({'horarios': horarios_livres})
        
    except Exception as e:
        logging.error(f"Erro ao buscar horários: {e}")
        return jsonify({'horarios': []})