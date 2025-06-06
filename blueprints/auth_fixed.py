"""
Blueprint de autenticação do Sistema Médico VIDAH - Versão Corrigida
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def require_auth():
    """Decorator para verificar autenticação"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'usuario' not in session:
                flash('Você precisa fazer login para acessar esta página', 'error')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_doctor(f):
    """Decorator específico para médicos"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash('Você precisa fazer login para acessar esta página', 'error')
            return redirect(url_for('auth.login'))
        
        user_type = session.get('usuario_tipo', 'medico')
        if user_type not in ['medico', 'admin']:
            flash('Acesso negado', 'error')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuário (médico ou administrador)"""
    
    if request.method == 'POST':
        try:
            # Importações tardias para evitar circular imports
            from core.database import db
            from models import Medico
            
            nome = request.form.get('nome', '').strip()
            crm = request.form.get('crm', '').strip()
            senha = request.form.get('senha', '')
            
            if not nome or not senha:
                flash('Nome e senha são obrigatórios', 'error')
                return render_template('login.html')
            
            # Verificar se é administrador hardcoded
            if nome == 'admin' and senha == 'admin123':
                session['usuario'] = nome
                session['usuario_tipo'] = 'admin'
                session['admin_usuario'] = nome
                session.permanent = True
                
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard.index'))
            
            # Verificar médico se CRM foi fornecido
            if crm:
                medico = db.session.query(Medico).filter_by(nome=nome, crm=crm).first()
                if medico and check_password_hash(medico.senha, senha):
                    session['usuario'] = nome
                    session['usuario_tipo'] = 'medico'
                    session.permanent = True
                    
                    flash('Login realizado com sucesso!', 'success')
                    return redirect(url_for('dashboard.index'))
                
                # Verificar se médico existe mas senha está incorreta
                if medico:
                    flash('Senha incorreta', 'error')
                else:
                    flash('Usuário não encontrado', 'error')
            else:
                flash('CRM é obrigatório para médicos', 'error')
                
        except Exception as e:
            flash('Erro interno do servidor', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    user = session.get('usuario', 'Usuário')
    session.clear()
    flash(f'Logout realizado com sucesso, {user}!', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de novo médico"""
    
    if request.method == 'POST':
        try:
            # Importações tardias para evitar circular imports
            from core.database import db
            from models import Medico
            
            nome = request.form.get('nome', '').strip()
            crm = request.form.get('crm', '').strip()
            especialidade = request.form.get('especialidade', '').strip()
            senha = request.form.get('senha', '')
            confirmar_senha = request.form.get('confirmar_senha', '')
            
            # Validações básicas
            if not all([nome, crm, especialidade, senha, confirmar_senha]):
                flash('Todos os campos são obrigatórios', 'error')
                return render_template('auth/register.html')
            
            if senha != confirmar_senha:
                flash('Senhas não coincidem', 'error')
                return render_template('auth/register.html')
            
            if len(senha) < 6:
                flash('Senha deve ter pelo menos 6 caracteres', 'error')
                return render_template('auth/register.html')
            
            # Verificar se médico já existe
            existing = db.session.query(Medico).filter_by(nome=nome, crm=crm).first()
            if existing:
                flash('Médico já cadastrado com este nome e CRM', 'error')
                return render_template('auth/register.html')
            
            # Criar novo médico
            medico = Medico()
            medico.nome = nome
            medico.crm = crm
            medico.especialidade = especialidade
            medico.senha = generate_password_hash(senha)
            
            db.session.add(medico)
            db.session.commit()
            
            flash('Médico cadastrado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar médico', 'error')
    
    return render_template('auth/register.html')


@auth_bp.route('/profile')
@require_doctor
def profile():
    """Perfil do usuário logado"""
    try:
        # Importações tardias para evitar circular imports
        from core.database import db
        from models import Medico
        
        user = session.get('usuario')
        user_type = session.get('usuario_tipo', 'medico')
        
        if user_type == 'admin':
            return render_template('auth/profile.html', 
                                 user={'nome': user, 'tipo': 'Administrador'})
        
        # Buscar dados do médico
        medico = db.session.query(Medico).filter_by(nome=user).first()
        if medico:
            return render_template('auth/profile.html', user=medico, user_type=user_type)
        else:
            flash('Dados do usuário não encontrados', 'error')
            return redirect(url_for('dashboard.index'))
            
    except Exception as e:
        flash('Erro ao carregar perfil', 'error')
        return redirect(url_for('dashboard.index'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@require_doctor
def change_password():
    """Alterar senha do usuário"""
    
    if request.method == 'POST':
        try:
            # Importações tardias para evitar circular imports
            from core.database import db
            from models import Medico
            
            user = session.get('usuario')
            user_type = session.get('usuario_tipo', 'medico')
            
            if user_type == 'admin':
                flash('Alteração de senha não disponível para administradores', 'error')
                return redirect(url_for('auth.profile'))
            
            senha_atual = request.form.get('senha_atual', '')
            nova_senha = request.form.get('nova_senha', '')
            confirmar_senha = request.form.get('confirmar_senha', '')
            
            # Validações
            if not all([senha_atual, nova_senha, confirmar_senha]):
                flash('Todos os campos são obrigatórios', 'error')
                return render_template('auth/change_password.html')
            
            if nova_senha != confirmar_senha:
                flash('Nova senha e confirmação não coincidem', 'error')
                return render_template('auth/change_password.html')
            
            if len(nova_senha) < 6:
                flash('Nova senha deve ter pelo menos 6 caracteres', 'error')
                return render_template('auth/change_password.html')
            
            # Verificar senha atual
            medico = db.session.query(Medico).filter_by(nome=user).first()
            if not medico or not check_password_hash(medico.senha, senha_atual):
                flash('Senha atual incorreta', 'error')
                return render_template('auth/change_password.html')
            
            # Atualizar senha
            medico.senha = generate_password_hash(nova_senha)
            db.session.commit()
            
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao alterar senha', 'error')
    
    return render_template('auth/change_password.html')