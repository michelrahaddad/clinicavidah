"""
Sistema de autenticação simplificado
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from core.database import db
from models import Medico
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login simplificado"""
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            crm = request.form.get('crm', '').strip()
            senha = request.form.get('senha', '')
            
            logger.info(f"Tentativa de login: {nome}, CRM: {crm}")
            
            # Buscar médico no banco
            medico = db.session.query(Medico).filter_by(nome=nome, crm=crm).first()
            logger.info(f"Médico encontrado: {medico.nome if medico else None}")
            
            if medico and check_password_hash(medico.senha, senha):
                session['usuario'] = {
                    'id': medico.id,
                    'nome': medico.nome,
                    'crm': medico.crm,
                    'tipo': 'medico'
                }
                logger.info(f"Login bem-sucedido para {nome}")
                return redirect(url_for('dashboard.index'))
            else:
                flash('Credenciais inválidas', 'error')
                return render_template('login.html')
                
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            flash('Erro interno no sistema', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Logout realizado com sucesso', 'success')
    return redirect(url_for('auth.login'))