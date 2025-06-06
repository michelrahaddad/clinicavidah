"""
Rotas médicas completas do Sistema VIDAH
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from core.database import db
from models import Paciente, Receita, ExameLab, ExameImg, Medico, AtestadoMedico
from datetime import datetime
import json
from core.logging_config import medical_logger, log_user_action, log_database_operation


medical_bp = Blueprint('medical', __name__, url_prefix='/medical')

@medical_bp.route('/receitas')
    log_user_action(session["usuario"], "VIEW_RECEITAS")
def receitas():
    """Lista todas as receitas do médico"""
    if 'usuario' not in session:
        return redirect('/auth/login')
    
    user = session['usuario']
    medico = db.session.query(Medico).filter_by(nome=user['nome']).first()
    
    if medico:
        receitas = db.session.query(Receita).filter_by(id_medico=medico.id).order_by(Receita.data_criacao.desc()).all()
    else:
        receitas = []
    
    return render_template('medical/receitas.html', receitas=receitas)

@medical_bp.route('/receitas/nova', methods=['GET', 'POST'])
def nova_receita():
    """Cria nova receita médica"""
    if 'usuario' not in session:
        return redirect('/auth/login')
    
    if request.method == 'POST':
        try:
            user = session['usuario']
            medico = db.session.query(Medico).filter_by(nome=user['nome']).first()
            
            receita = Receita()
            receita.nome_paciente = request.form.get('paciente_nome')
            receita.medicamentos = request.form.get('medicamentos')
            receita.posologias = request.form.get('posologias')
            receita.duracoes = request.form.get('duracoes')
            receita.vias = request.form.get('vias')
            receita.medico_nome = medico.nome
            receita.data = datetime.now().strftime('%d/%m/%Y')
            receita.data_criacao = datetime.now()
            receita.id_medico = medico.id
            
            # Buscar ou criar paciente
            paciente = db.session.query(Paciente).filter_by(nome=receita.nome_paciente).first()
            if paciente:
                receita.id_paciente = paciente.id
            else:
                # Criar paciente básico
                novo_paciente = Paciente()
                novo_paciente.nome = receita.nome_paciente
                novo_paciente.cpf = '000.000.000-00'  # Temporário
                novo_paciente.idade = 0
                novo_paciente.endereco = 'A definir'
                novo_paciente.cidade_uf = 'A definir'
                db.session.add(novo_paciente)
                db.session.flush()
                receita.id_paciente = novo_paciente.id
            
            db.session.add(receita)
    medical_logger.info(f"New receita created for patient: {receita.nome_paciente}"); log_database_operation("INSERT", "receitas", session["usuario"], f"Receita for {receita.nome_paciente}")
            db.session.commit()
            
            flash('Receita criada com sucesso!', 'success')
            return redirect('/medical/receitas')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar receita: {str(e)}', 'error')
    
    return render_template('medical/nova_receita.html')

@medical_bp.route('/exames-lab')
    log_user_action(session["usuario"], "VIEW_EXAMES_LAB")
def exames_lab():
    """Lista exames laboratoriais"""
    if 'usuario' not in session:
        return redirect('/auth/login')
    
    user = session['usuario']
    medico = db.session.query(Medico).filter_by(nome=user['nome']).first()
    
    if medico:
        exames = db.session.query(ExameLab).filter_by(id_medico=medico.id).order_by(ExameLab.created_at.desc()).all()
    else:
        exames = []
    
    return render_template('medical/exames_lab.html', exames=exames)

@medical_bp.route('/pacientes')
    log_user_action(session["usuario"], "VIEW_PACIENTES")
def pacientes():
    """Lista todos os pacientes"""
    if 'usuario' not in session:
        return redirect('/auth/login')
    
    pacientes = db.session.query(Paciente).order_by(Paciente.nome).all()
    return render_template('medical/pacientes.html', pacientes=pacientes)

@medical_bp.route('/api/pacientes')
def api_pacientes():
    """API para busca de pacientes (autocomplete)"""
    if 'usuario' not in session:
        return jsonify([])
    
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    pacientes = db.session.query(Paciente).filter(
        Paciente.nome.ilike(f'%{query}%')
    ).limit(10).all()
    
    result = []
    for p in pacientes:
        result.append({
            'id': p.id,
            'nome': p.nome,
            'cpf': p.cpf,
            'idade': p.idade
        })
    
    return jsonify(result)
