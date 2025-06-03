from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Medico, Administrador
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
        
        if not nome or not senha:
            flash('Nome e senha são obrigatórios.', 'error')
            return render_template('login.html')
        
        try:
            # Primeiro, verificar se é administrador (usando nome como usuário)
            admin = Administrador.query.filter_by(usuario=nome, ativo=True).first()
            
            if admin and check_password_hash(admin.senha, senha):
                # Login como administrador
                session['admin'] = {
                    'id': admin.id,
                    'usuario': admin.usuario,
                    'nome': admin.nome
                }
                
                # Update last access
                admin.ultimo_acesso = db.session.query(db.func.now()).scalar()
                db.session.commit()
                
                # Log admin login
                from utils.security import log_admin_action
                log_admin_action('login', admin.usuario, f'Login administrativo realizado', request.remote_addr)
                
                flash(f'Bem-vindo, Administrador {admin.nome}!', 'success')
                logging.info(f'Admin login successful for: {nome}')
                return redirect(url_for('admin.dashboard'))
            
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
