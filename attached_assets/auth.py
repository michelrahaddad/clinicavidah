from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.forms import LoginForm
from utils.db import get_db_connection
from werkzeug.security import check_password_hash
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    form = LoginForm()
    
    if form.validate_on_submit():
        nome = form.nome.data.strip() if form.nome.data else ""
        crm = form.crm.data.strip() if form.crm.data else ""
        senha = form.senha.data if form.senha.data else ""
        
        if not nome or not crm or not senha:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('login.html', form=form)
        
        try:
            conn = get_db_connection()
            medico = conn.execute(
                "SELECT * FROM medicos WHERE nome = ? AND crm = ?", 
                (nome, crm)
            ).fetchone()
            conn.close()
            
            if medico and medico['senha'] and check_password_hash(medico['senha'], senha):
                session['usuario'] = {
                    'id': medico['id'],
                    'nome': medico['nome'],
                    'crm': medico['crm']
                }
                flash(f'Bem-vindo, {medico["nome"]}!', 'success')
                logging.info(f'Login successful for user: {nome} (CRM: {crm})')
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash('Credenciais inválidas. Verifique nome, CRM e senha.', 'error')
                logging.warning(f'Failed login attempt for: {nome} (CRM: {crm})')
                
        except Exception as e:
            logging.error(f'Login error: {e}')
            flash('Erro interno. Tente novamente.', 'error')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    user_name = session.get('usuario', {}).get('nome', 'Unknown')
    session.clear()
    flash('Logout realizado com sucesso.', 'info')
    logging.info(f'User logged out: {user_name}')
    return redirect(url_for('auth.login'))
