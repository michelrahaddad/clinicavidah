from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Medico, Administrador
from main import db
from werkzeug.security import check_password_hash
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Redirect to login page"""
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user authentication - restored to 11:00 AM working state"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        logging.info(f"Login attempt - Username: {username}")
        
        # Check for admin login (admin/admin123)
        if username.lower() == 'admin' and password == 'admin123':
            session.clear()
            session['user_id'] = 'admin'
            session['user_name'] = 'Administrador'
            session['user_type'] = 'admin'
            session['is_admin'] = True
            logging.info("Admin login successful")
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        
        # Check for doctor login by name or CRM
        if username and password:
            try:
                # Search for doctor by name (contains) or exact CRM match
                medico = db.session.query(Medico).filter(
                    db.or_(
                        Medico.nome.ilike(f'%{username}%'),
                        Medico.crm == username
                    )
                ).first()
                
                if medico and check_password_hash(medico.senha, password):
                    session.clear()
                    session['user_id'] = medico.id
                    session['user_name'] = medico.nome
                    session['user_crm'] = medico.crm
                    session['user_type'] = 'medico'
                    session['is_admin'] = False
                    logging.info(f"Doctor login successful: {medico.nome}")
                    flash('Login realizado com sucesso!', 'success')
                    return redirect(url_for('dashboard.dashboard'))
                else:
                    logging.warning(f"Failed login attempt for: {username}")
                    flash('Usuário ou senha incorretos!', 'error')
                    
            except Exception as e:
                logging.error(f"Database error during login: {e}")
                flash('Erro interno do sistema. Tente novamente.', 'error')
        else:
            flash('Preencha todos os campos!', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('auth.login'))