from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import Admin, Medico
from main import db
from werkzeug.security import check_password_hash
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/')
def index():
    """Redirect to login page"""
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        crm = request.form.get('crm', '').strip()
        senha = request.form.get('senha', '')
        
        if not nome or not senha:
            flash('Nome e senha são obrigatórios.', 'error')
            return render_template('login.html')
        
        try:
            # Verificar se é administrador
            if not crm:  # Sem CRM = administrador
                admin = Admin.query.filter_by(nome=nome).first()
                
                if admin and admin.senha and check_password_hash(admin.senha, senha):
                    # Login simples como administrador
                    session.clear()
                    session['usuario'] = admin.nome
                    session['admin'] = True
                    session['user_id'] = admin.id
                    session.permanent = True
                    
                    flash(f'Bem-vindo, {admin.nome}!', 'success')
                    return redirect('/prontuario')
                else:
                    flash('Credenciais de administrador inválidas.', 'error')
            
            # Verificar se é médico
            else:
                medico = Medico.query.filter_by(nome=nome, crm=crm).first()
                
                if medico and medico.senha and check_password_hash(medico.senha, senha):
                    session.clear()
                    session['usuario'] = medico.nome
                    session['medico'] = True
                    session['user_id'] = medico.id
                    session['crm'] = medico.crm
                    session.permanent = True
                    
                    flash(f'Bem-vindo, Dr. {medico.nome}!', 'success')
                    return redirect('/prontuario')
                else:
                    flash('Credenciais de médico inválidas.', 'error')
        
        except Exception as e:
            logging.error(f'Login error: {e}')
            flash('Erro interno. Tente novamente.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('auth.login'))