from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Medico
from app import db
from werkzeug.security import check_password_hash
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        crm = request.form.get('crm', '').strip()
        senha = request.form.get('senha', '')
        
        if not nome or not crm or not senha:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('login.html')
        
        try:
            medico = Medico.query.filter_by(nome=nome, crm=crm).first()
            
            if medico and medico.senha and check_password_hash(medico.senha, senha):
                session['usuario'] = {
                    'id': medico.id,
                    'nome': medico.nome,
                    'crm': medico.crm
                }
                flash(f'Bem-vindo, {medico.nome}!', 'success')
                logging.info(f'Login successful for user: {nome} (CRM: {crm})')
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash('Credenciais inválidas. Verifique nome, CRM e senha.', 'error')
                logging.warning(f'Failed login attempt for: {nome} (CRM: {crm})')
                
        except Exception as e:
            logging.error(f'Login error: {e}')
            flash('Erro interno. Tente novamente.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    user_name = session.get('usuario', {}).get('nome', 'Unknown')
    session.clear()
    flash('Logout realizado com sucesso.', 'info')
    logging.info(f'User logged out: {user_name}')
    return redirect(url_for('auth.login'))
