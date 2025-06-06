"""
Blueprint de autenticação do Sistema Médico VIDAH
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from models import Medico, Admin
from app import db
from validators.base import StringValidator, ValidationError
from validators.medical import get_validator
from core.logging import get_logger, log_action

logger = get_logger('auth')
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
@log_action('user_login_attempt')
def login():
    """Página de login para médicos e administradores"""
    if request.method == 'POST':
        try:
            # Validar dados de entrada
            name_validator = StringValidator(min_length=2, max_length=100)
            crm_validator = StringValidator(min_length=6, max_length=20)
            
            nome = name_validator.validate(request.form.get('nome'), 'nome')
            crm = crm_validator.validate(request.form.get('crm'), 'crm')
            
            logger.info(f"Login attempt - Nome: {nome}, CRM: {crm}")
            
            # Verificar se é administrador
            admin = Admin.query.filter_by(nome=nome).first()
            if admin and admin.crm == crm:
                session['admin_usuario'] = nome
                session['usuario_tipo'] = 'admin'
                session.permanent = True
                
                logger.info(f"Admin login successful: {nome}")
                flash('Login de administrador realizado com sucesso!', 'success')
                return redirect(url_for('main.dashboard'))
            
            # Verificar médico
            medico = Medico.query.filter_by(nome=nome, crm=crm).first()
            if medico:
                session['usuario'] = nome
                session['usuario_tipo'] = 'medico'
                session['medico_id'] = medico.id
                session.permanent = True
                
                logger.info(f"Doctor login successful: {nome} (CRM: {crm})")
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('main.dashboard'))
            
            logger.warning(f"Login failed for: {nome} (CRM: {crm})")
            flash('Nome ou CRM incorretos', 'error')
            
        except ValidationError as e:
            logger.warning(f"Login validation error: {e.message}")
            flash(f'Erro de validação: {e.message}', 'error')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('Erro interno do sistema', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@log_action('user_logout')
def logout():
    """Logout do usuário"""
    user = session.get('usuario') or session.get('admin_usuario')
    if user:
        logger.info(f"User logout: {user}")
    
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
@log_action('doctor_registration')
def register():
    """Registro de novos médicos (apenas para admins)"""
    if not session.get('admin_usuario'):
        flash('Acesso negado. Apenas administradores podem cadastrar médicos.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            # Validar dados do médico
            validator = get_validator('patient')  # Usar validador base
            data = {
                'nome': request.form.get('nome'),
                'crm': request.form.get('crm'),
                'especialidade': request.form.get('especialidade'),
                'email': request.form.get('email'),
                'telefone': request.form.get('telefone')
            }
            
            validated_data = validator.validate(data)
            
            # Verificar se CRM já existe
            existing_doctor = Medico.query.filter_by(crm=validated_data['crm']).first()
            if existing_doctor:
                flash('CRM já cadastrado no sistema', 'error')
                return render_template('register_doctor.html')
            
            # Criar novo médico
            new_doctor = Medico(
                nome=validated_data['nome'],
                crm=validated_data['crm'],
                especialidade=validated_data.get('especialidade', ''),
                email=validated_data.get('email', ''),
                telefone=validated_data.get('telefone', '')
            )
            
            db.session.add(new_doctor)
            db.session.commit()
            
            logger.info(f"New doctor registered: {validated_data['nome']} (CRM: {validated_data['crm']})")
            flash('Médico cadastrado com sucesso!', 'success')
            return redirect(url_for('main.dashboard'))
            
        except ValidationError as e:
            logger.warning(f"Doctor registration validation error: {e.message}")
            flash(f'Erro de validação: {e.message}', 'error')
        except Exception as e:
            logger.error(f"Doctor registration error: {str(e)}")
            flash('Erro ao cadastrar médico', 'error')
            db.session.rollback()
    
    return render_template('register_doctor.html')


@auth_bp.route('/profile', methods=['GET', 'POST'])
@log_action('profile_access')
def profile():
    """Perfil do usuário logado"""
    if not (session.get('usuario') or session.get('admin_usuario')):
        return redirect(url_for('auth.login'))
    
    user_name = session.get('usuario') or session.get('admin_usuario')
    user_type = session.get('usuario_tipo', 'medico')
    
    if user_type == 'admin':
        user = Admin.query.filter_by(nome=user_name).first()
    else:
        user = Medico.query.filter_by(nome=user_name).first()
    
    if not user:
        flash('Usuário não encontrado', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            # Atualizar dados do perfil
            if hasattr(user, 'especialidade'):
                user.especialidade = request.form.get('especialidade', user.especialidade)
            if hasattr(user, 'email'):
                user.email = request.form.get('email', user.email)
            if hasattr(user, 'telefone'):
                user.telefone = request.form.get('telefone', user.telefone)
            
            db.session.commit()
            logger.info(f"Profile updated for: {user_name}")
            flash('Perfil atualizado com sucesso!', 'success')
            
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            flash('Erro ao atualizar perfil', 'error')
            db.session.rollback()
    
    return render_template('profile.html', user=user, user_type=user_type)


@auth_bp.route('/check_session')
def check_session():
    """API para verificar status da sessão"""
    is_logged_in = bool(session.get('usuario') or session.get('admin_usuario'))
    user_type = session.get('usuario_tipo', 'guest')
    user_name = session.get('usuario') or session.get('admin_usuario')
    
    return jsonify({
        'logged_in': is_logged_in,
        'user_type': user_type,
        'user_name': user_name,
        'session_id': session.get('_id', 'unknown')
    })


# Middleware para verificar autenticação
def require_auth(user_types=None):
    """Decorador para verificar autenticação"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not (session.get('usuario') or session.get('admin_usuario')):
                if request.is_json:
                    return jsonify({'error': 'Autenticação necessária'}), 401
                flash('Acesso negado. Faça login primeiro.', 'error')
                return redirect(url_for('auth.login'))
            
            if user_types:
                current_type = session.get('usuario_tipo', 'medico')
                if current_type not in user_types:
                    if request.is_json:
                        return jsonify({'error': 'Permissão insuficiente'}), 403
                    flash('Permissão insuficiente', 'error')
                    return redirect(url_for('main.dashboard'))
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_admin(func):
    """Decorador específico para administradores"""
    return require_auth(['admin'])(func)


def require_doctor(func):
    """Decorador específico para médicos"""
    return require_auth(['medico', 'admin'])(func)