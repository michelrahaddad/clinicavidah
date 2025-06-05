from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Medico, Administrador
from app import db
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
    """Handle user login"""
    if request.method == 'GET':
        return render_template('login_simple.html')
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        crm = request.form.get('crm', '').strip()
        senha = request.form.get('senha', '')
        
        if not nome or not senha:
            flash('Nome e senha são obrigatórios.', 'error')
            return render_template('login.html')
        
        try:
            logging.info(f'Login attempt - Nome: {nome}, CRM: {crm}')
            
            # Primeiro, verificar se é administrador (usando nome como usuário)
            admin = Administrador.query.filter_by(usuario=nome, ativo=True).first()
            logging.info(f'Admin query result: {admin is not None}')
            
            if admin:
                logging.info(f'Admin found: {admin.nome}, checking password...')
                senha_valida = check_password_hash(admin.senha, senha)
                logging.info(f'Password validation: {senha_valida}')
                
                if senha_valida:
                    # Limpar sessão completamente
                    session.clear()
                    
                    # Login como administrador
                    session['admin'] = True
                    session['admin_data'] = {
                        'id': admin.id,
                        'usuario': admin.usuario,
                        'nome': admin.nome,
                        'email': admin.email
                    }
                    session['usuario'] = admin.nome
                    session.permanent = True
                    
                    # Update last access
                    try:
                        admin.ultimo_acesso = datetime.utcnow()
                        db.session.commit()
                    except Exception as e:
                        logging.warning(f'Failed to update last access: {e}')
                    
                    flash(f'Bem-vindo, Administrador {admin.nome}!', 'success')
                    logging.info(f'Admin login successful for: {nome}')
                    
                    # Redirecionamento robusto para dashboard
                    from flask import make_response
                    response = make_response(redirect('/dashboard', code=302))
                    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
                    return response
                else:
                    logging.warning(f'Invalid password for admin: {nome}')
            
            # Se não é admin, verificar se é médico (CRM obrigatório para médicos)
            if crm:  # Se CRM foi fornecido, tentar login como médico
                medico = Medico.query.filter_by(nome=nome, crm=crm).first()
                
                if medico and medico.senha and check_password_hash(medico.senha, senha):
                    session['usuario'] = medico.nome
                    session['medico_data'] = {
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
            else:
                flash('Para acessar como médico, é necessário informar o CRM.', 'error')
                
        except Exception as e:
            logging.error(f'Login error: {e}')
            flash('Erro interno. Tente novamente.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    user_name = session.get('usuario', 'Unknown')
    session.clear()
    flash('Logout realizado com sucesso.', 'info')
    logging.info(f'User logged out: {user_name}')
    return redirect(url_for('auth.login'))
