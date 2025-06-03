from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import Administrador, LogSistema, BackupConfig, Medico, Paciente, Receita, ExameLab, ExameImg
from app import db
from datetime import datetime, timedelta
import os
import zipfile
import shutil
import subprocess
import logging
import json
from utils.security import require_admin, log_admin_action
from utils.backup import create_backup, restore_backup, schedule_backup
from utils.forms import sanitizar_entrada

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        usuario = sanitizar_entrada(request.form.get('usuario', ''))
        senha = request.form.get('senha', '')
        
        if not usuario or not senha:
            flash('Usuario e senha são obrigatórios.', 'error')
            return render_template('admin/login.html')
        
        admin = Administrador.query.filter_by(usuario=usuario, ativo=True).first()
        
        if admin and check_password_hash(admin.senha, senha):
            session['admin'] = {
                'id': admin.id,
                'usuario': admin.usuario,
                'nome': admin.nome
            }
            
            # Update last access
            admin.ultimo_acesso = datetime.utcnow()
            db.session.commit()
            
            # Log login
            log_admin_action('login', admin.usuario, f'Login realizado com sucesso', request.remote_addr)
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            # Log failed login
            log_admin_action('login_failed', usuario, f'Tentativa de login falhada', request.remote_addr)
            flash('Credenciais inválidas.', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def admin_logout():
    """Admin logout"""
    if 'admin' in session:
        log_admin_action('logout', session['admin']['usuario'], 'Logout realizado')
        session.pop('admin', None)
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/dashboard')
@require_admin
def dashboard():
    """Admin dashboard"""
    # System statistics
    stats = {
        'total_medicos': Medico.query.count(),
        'total_pacientes': Paciente.query.count(),
        'total_receitas': Receita.query.count(),
        'total_exames_lab': ExameLab.query.count(),
        'total_exames_img': ExameImg.query.count(),
        'receitas_hoje': Receita.query.filter(
            Receita.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
        ).count(),
        'backup_config': BackupConfig.query.first()
    }
    
    # Recent logs
    recent_logs = LogSistema.query.order_by(LogSistema.timestamp.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_logs=recent_logs)

@admin_bp.route('/estatisticas-neurais')
@require_admin
def estatisticas_neurais():
    """Neural statistics for admin"""
    from routes.estatisticas_neurais import get_neural_statistics
    stats = get_neural_statistics()
    return render_template('admin/estatisticas_neurais.html', **stats)

@admin_bp.route('/backup')
@require_admin
def backup_management():
    """Backup management page"""
    config = BackupConfig.query.first()
    if not config:
        # Create default config
        config = BackupConfig(
            frequencia='daily',
            horario='02:00',
            retencao_dias=30
        )
        db.session.add(config)
        db.session.commit()
    
    # List existing backups
    backup_dir = 'backups'
    backups = []
    if os.path.exists(backup_dir):
        for file in os.listdir(backup_dir):
            if file.endswith('.sql'):
                file_path = os.path.join(backup_dir, file)
                stat = os.stat(file_path)
                backups.append({
                    'nome': file,
                    'tamanho': round(stat.st_size / 1024 / 1024, 2),  # MB
                    'data': datetime.fromtimestamp(stat.st_mtime)
                })
    
    backups.sort(key=lambda x: x['data'], reverse=True)
    
    return render_template('admin/backup.html', config=config, backups=backups)

@admin_bp.route('/backup/create', methods=['POST'])
@require_admin
def create_backup_now():
    """Create backup immediately"""
    try:
        backup_file = create_backup()
        log_admin_action('backup', session['admin']['usuario'], f'Backup manual criado: {backup_file}')
        flash('Backup criado com sucesso!', 'success')
    except Exception as e:
        logging.error(f'Backup error: {e}')
        flash('Erro ao criar backup.', 'error')
    
    return redirect(url_for('admin.backup_management'))

@admin_bp.route('/backup/config', methods=['POST'])
@require_admin
def update_backup_config():
    """Update backup configuration"""
    try:
        config = BackupConfig.query.first()
        config.frequencia = request.form.get('frequencia')
        config.horario = request.form.get('horario')
        config.retencao_dias = int(request.form.get('retencao_dias'))
        config.ativo = 'ativo' in request.form
        
        db.session.commit()
        
        # Reschedule backup
        schedule_backup(config)
        
        log_admin_action('backup_config', session['admin']['usuario'], 'Configuração de backup atualizada')
        flash('Configuração de backup atualizada!', 'success')
    except Exception as e:
        logging.error(f'Backup config error: {e}')
        flash('Erro ao atualizar configuração.', 'error')
    
    return redirect(url_for('admin.backup_management'))

@admin_bp.route('/system-update')
@require_admin
def system_update():
    """System update page"""
    return render_template('admin/system_update.html')

@admin_bp.route('/system-update/upload', methods=['POST'])
@require_admin
def upload_update():
    """Upload and apply system update"""
    if 'update_file' not in request.files:
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('admin.system_update'))
    
    file = request.files['update_file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('admin.system_update'))
    
    if not file.filename.endswith('.zip'):
        flash('Apenas arquivos ZIP são aceitos.', 'error')
        return redirect(url_for('admin.system_update'))
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        upload_path = os.path.join('updates', filename)
        os.makedirs('updates', exist_ok=True)
        file.save(upload_path)
        
        # Process update
        result = process_system_update(upload_path)
        
        if result['success']:
            log_admin_action('system_update', session['admin']['usuario'], f'Atualização aplicada: {filename}')
            flash('Atualização aplicada com sucesso!', 'success')
        else:
            flash(f'Erro na atualização: {result["error"]}', 'error')
            
    except Exception as e:
        logging.error(f'Update error: {e}')
        flash('Erro ao processar atualização.', 'error')
    
    return redirect(url_for('admin.system_update'))

@admin_bp.route('/logs')
@require_admin
def system_logs():
    """System logs page"""
    page = request.args.get('page', 1, type=int)
    tipo = request.args.get('tipo', '')
    
    query = LogSistema.query
    if tipo:
        query = query.filter(LogSistema.tipo == tipo)
    
    logs = query.order_by(LogSistema.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('admin/logs.html', logs=logs, tipo_filter=tipo)

@admin_bp.route('/users')
@require_admin
def user_management():
    """User management page"""
    medicos = Medico.query.all()
    admins = Administrador.query.all()
    return render_template('admin/users.html', medicos=medicos, admins=admins)

@admin_bp.route('/create-admin', methods=['POST'])
@require_admin
def create_admin():
    """Create new admin user"""
    try:
        usuario = sanitizar_entrada(request.form.get('usuario'))
        nome = sanitizar_entrada(request.form.get('nome'))
        email = sanitizar_entrada(request.form.get('email'))
        senha = request.form.get('senha')
        
        # Check if user exists
        if Administrador.query.filter_by(usuario=usuario).first():
            flash('Usuário já existe.', 'error')
            return redirect(url_for('admin.user_management'))
        
        # Create admin
        admin = Administrador(
            usuario=usuario,
            nome=nome,
            email=email,
            senha=generate_password_hash(senha)
        )
        
        db.session.add(admin)
        db.session.commit()
        
        log_admin_action('create_admin', session['admin']['usuario'], f'Administrador criado: {usuario}')
        flash('Administrador criado com sucesso!', 'success')
        
    except Exception as e:
        logging.error(f'Create admin error: {e}')
        flash('Erro ao criar administrador.', 'error')
    
    return redirect(url_for('admin.user_management'))

def process_system_update(zip_path):
    """Process system update from ZIP file"""
    try:
        # Extract ZIP
        extract_path = os.path.join('updates', 'temp')
        os.makedirs(extract_path, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # Look for update.json manifest
        manifest_path = os.path.join(extract_path, 'update.json')
        if not os.path.exists(manifest_path):
            return {'success': False, 'error': 'Arquivo update.json não encontrado'}
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Validate manifest
        required_fields = ['version', 'files', 'backup_required']
        if not all(field in manifest for field in required_fields):
            return {'success': False, 'error': 'Manifest inválido'}
        
        # Create backup if required
        if manifest.get('backup_required', True):
            create_backup()
        
        # Apply updates
        for file_info in manifest['files']:
            source = os.path.join(extract_path, file_info['source'])
            target = file_info['target']
            
            if os.path.exists(source):
                # Create target directory if needed
                os.makedirs(os.path.dirname(target), exist_ok=True)
                
                # Copy file
                shutil.copy2(source, target)
        
        # Run post-update script if exists
        script_path = os.path.join(extract_path, 'post_update.py')
        if os.path.exists(script_path):
            subprocess.run(['python', script_path], cwd=extract_path)
        
        # Cleanup
        shutil.rmtree(extract_path)
        os.remove(zip_path)
        
        return {'success': True}
        
    except Exception as e:
        logging.error(f'Update processing error: {e}')
        return {'success': False, 'error': str(e)}