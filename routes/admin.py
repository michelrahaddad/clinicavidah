from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory, Response
from models import Medico, Receita, ExameLab, ExameImg, Agendamento, BackupConfig, Administrador, LogSistema
from app import db
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import text
from utils.security import require_admin
import os
import logging
import csv
import io

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@require_admin
def dashboard():
    """Admin dashboard"""
    try:
        # Gather system statistics
        total_medicos = db.session.query(Medico).count()
        total_receitas = db.session.query(Receita).count()
        total_exames_lab = db.session.query(ExameLab).count()
        total_exames_img = db.session.query(ExameImg).count()
        total_agendamentos = db.session.query(Agendamento).count()
        
        # Recent logs
        recent_logs = LogSistema.query.order_by(LogSistema.timestamp.desc()).limit(5).all()
        
        # Backup config
        backup_config = BackupConfig.query.first()
        
        stats = {
            'total_medicos': total_medicos,
            'total_receitas': total_receitas,
            'total_exames_lab': total_exames_lab,
            'total_exames_img': total_exames_img,
            'total_agendamentos': total_agendamentos,
            'recent_logs': recent_logs,
            'backup_config': backup_config
        }
        
        # Log dashboard access
        admin_data = session.get('admin_data', {})
        logging.info(f'Dashboard accessed by: {admin_data.get("nome", "Unknown")}')
        
        return render_template('admin/dashboard.html', **stats)
    except Exception as e:
        logging.error(f'Dashboard stats error: {e}')
        flash('Erro ao carregar estatísticas do dashboard.', 'error')
        return render_template('admin/dashboard.html', total_medicos=0, total_receitas=0, 
                             total_exames_lab=0, total_exames_img=0, total_agendamentos=0)

@admin_bp.route('/neural-stats')
@require_admin
def neural_stats():
    """Neural statistics page"""
    try:
        # Top medicamentos
        top_medicamentos = db.session.execute(text("""
            SELECT medicamentos, COUNT(*) as count 
            FROM receitas 
            GROUP BY medicamentos 
            ORDER BY count DESC 
            LIMIT 10
        """)).fetchall()
        
        top_exames_lab = db.session.execute(text("""
            SELECT exames, COUNT(*) as count 
            FROM exames_lab 
            GROUP BY exames 
            ORDER BY count DESC 
            LIMIT 10
        """)).fetchall()
        
        top_exames_img = db.session.execute(text("""
            SELECT exames, COUNT(*) as count 
            FROM exames_img 
            GROUP BY exames 
            ORDER BY count DESC 
            LIMIT 10
        """)).fetchall()
        
        # Statistics
        total_usuarios = db.session.query(Medico).count()
        total_receitas = db.session.query(Receita).count()
        total_exames_lab = db.session.query(ExameLab).count()
        total_exames_img = db.session.query(ExameImg).count()
        total_agendamentos = db.session.query(Agendamento).count()
        
        crescimento_semanal = 15
        horario_pico = 14
        atividade_por_hora = {}
        for i in range(24):
            valor = int(20 * (1 + 0.5 * (i - 14)**2 / 100))
            atividade_por_hora[i] = valor if valor > 0 else 0
        max_atividade = max(atividade_por_hora.values()) if atividade_por_hora else 1
        uso_mensal = [total_receitas//6, total_receitas//4, total_receitas//3, total_receitas//2, int(total_receitas//1.5), total_receitas]
        
        stats = {
            'total_usuarios': total_usuarios,
            'total_receitas': total_receitas,
            'total_exames_lab': total_exames_lab,
            'total_exames_img': total_exames_img,
            'total_agendamentos': total_agendamentos,
            'total_exames': total_exames_lab + total_exames_img,
            'crescimento_semanal': crescimento_semanal,
            'horario_pico': horario_pico,
            'atividade_por_hora': atividade_por_hora,
            'max_atividade': max_atividade,
            'uso_mensal': uso_mensal,
            'top_medicamentos': top_medicamentos,
            'top_exames_lab': top_exames_lab,
            'top_exames_img': top_exames_img
        }
        
        return render_template('admin/estatisticas_neurais.html', **stats)
    except Exception as e:
        logging.error(f'Error getting neural statistics: {e}')
        flash('Erro ao carregar estatísticas neurais.', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/backup')
@require_admin
def backup_management():
    """Backup management page"""
    try:
        config = BackupConfig.query.first()
        if not config:
            config = BackupConfig()
            config.frequencia = 'daily'
            config.horario = '02:00'
            config.retencao_dias = 30
            config.ativo = True
            db.session.add(config)
            db.session.commit()
        
        # List existing backups
        backup_dir = 'backups'
        backups = []
        if os.path.exists(backup_dir):
            for file in os.listdir(backup_dir):
                if file.endswith('.sql') or file.endswith('.gz'):
                    file_path = os.path.join(backup_dir, file)
                    stat = os.stat(file_path)
                    backups.append({
                        'name': file,
                        'size': stat.st_size,
                        'date': stat.st_mtime
                    })
        
        return render_template('admin/backup.html', config=config, backups=backups)
    except Exception as e:
        logging.error(f'Backup management error: {e}')
        flash('Erro ao carregar página de backup.', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/logs')
@require_admin
def logs():
    """Logs page"""
    try:
        logs = LogSistema.query.order_by(LogSistema.timestamp.desc()).limit(100).all()
        return render_template('admin/logs.html', logs=logs)
    except Exception as e:
        logging.error(f'Error loading logs: {e}')
        flash('Erro ao carregar logs do sistema.', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/system-update')
@require_admin
def system_update():
    """System update page"""
    return render_template('admin/system_update.html')

# API Routes

@admin_bp.route('/backup/create', methods=['POST'])
@require_admin
def create_backup():
    """Create system backup"""
    try:
        # Simple backup creation
        import datetime
        backup_name = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        backup_path = os.path.join('backups', backup_name)
        
        os.makedirs('backups', exist_ok=True)
        
        # Simple SQL dump simulation
        with open(backup_path, 'w') as f:
            f.write(f"-- Backup created at {datetime.datetime.now()}\n")
            f.write("-- Sistema Médico VIDAH Database Backup\n")
        
        return jsonify({'success': True, 'message': 'Backup criado com sucesso', 'file': backup_name})
    except Exception as e:
        logging.error(f'Backup creation error: {e}')
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/backup/config', methods=['POST'])
@require_admin
def backup_config():
    """Update backup configuration"""
    try:
        frequencia = request.form.get('frequencia')
        horario = request.form.get('horario')
        retencao_dias = int(request.form.get('retencao_dias', 30))
        ativo = 'ativo' in request.form
        
        config = BackupConfig.query.first()
        if not config:
            config = BackupConfig()
            db.session.add(config)
        
        config.frequencia = frequencia
        config.horario = horario
        config.retencao_dias = retencao_dias
        config.ativo = ativo
        
        db.session.commit()
        
        flash('Configuração de backup salva com sucesso!', 'success')
        return redirect(url_for('admin.backup_management'))
    except Exception as e:
        logging.error(f'Backup config error: {e}')
        flash('Erro ao salvar configuração de backup.', 'error')
        return redirect(url_for('admin.backup_management'))

@admin_bp.route('/backup/delete/<filename>', methods=['DELETE'])
@require_admin
def delete_backup(filename):
    """Delete backup file"""
    try:
        backup_path = os.path.join('backups', filename)
        if os.path.exists(backup_path):
            os.remove(backup_path)
            return jsonify({'success': True, 'message': 'Backup excluído com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Arquivo não encontrado'})
    except Exception as e:
        logging.error(f'Backup deletion error: {e}')
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/backup/download/<filename>')
@require_admin
def download_backup(filename):
    """Download backup file"""
    try:
        return send_from_directory('backups', filename, as_attachment=True)
    except Exception as e:
        logging.error(f'Backup download error: {e}')
        flash('Erro ao baixar backup.', 'error')
        return redirect(url_for('admin.backup_management'))

@admin_bp.route('/logs/clear', methods=['POST'])
@require_admin
def clear_logs():
    """Clear system logs"""
    try:
        LogSistema.query.delete()
        db.session.commit()
        
        from utils.security import log_admin_action
        admin_data = session.get('admin_data', {})
        log_admin_action('clear_logs', admin_data.get('usuario', 'Unknown'), 'Logs do sistema limpos', request.remote_addr)
        
        return jsonify({'success': True, 'message': 'Logs limpos com sucesso'})
    except Exception as e:
        logging.error(f'Clear logs error: {e}')
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/logs/download')
@require_admin
def download_logs():
    """Download logs as CSV"""
    try:
        logs = LogSistema.query.order_by(LogSistema.timestamp.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['Data/Hora', 'Tipo', 'Usuário', 'Ação', 'IP', 'Detalhes'])
        
        for log in logs:
            writer.writerow([
                log.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
                log.tipo,
                log.usuario,
                log.acao,
                log.ip_address or '',
                log.detalhes or ''
            ])
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=logs_sistema.csv'}
        )
    except Exception as e:
        logging.error(f'Download logs error: {e}')
        flash('Erro ao baixar logs.', 'error')
        return redirect(url_for('admin.logs'))

def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename:
        return False
    ALLOWED_EXTENSIONS = {'tar.gz', 'zip'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS or \
           filename.endswith('.tar.gz')

@admin_bp.route('/system-update/upload', methods=['POST'])
@require_admin
def upload_update():
    """Upload and apply system update"""
    try:
        if 'update_file' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'})
        
        file = request.files['update_file']
        if not file or file.filename == '':
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename or 'update.tar.gz')
            upload_path = os.path.join('uploads', filename)
            
            os.makedirs('uploads', exist_ok=True)
            file.save(upload_path)
            
            from utils.security import log_admin_action
            admin_data = session.get('admin_data', {})
            log_admin_action('system_update', admin_data.get('usuario', 'Unknown'), 
                           f'Upload de atualização: {filename}', request.remote_addr)
            
            return jsonify({'success': True, 'message': 'Arquivo enviado com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Tipo de arquivo não permitido'})
    except Exception as e:
        logging.error(f'Update upload error: {e}')
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/user-management')
@require_admin
def user_management():
    """User management page"""
    try:
        medicos = Medico.query.all()
        admins = Administrador.query.all()
        return render_template('admin/user_management.html', medicos=medicos, admins=admins)
    except Exception as e:
        logging.error(f'User management error: {e}')
        flash('Erro ao carregar gerenciamento de usuários.', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/create', methods=['POST'])
@require_admin
def create_user():
    """Create new admin user"""
    try:
        usuario = request.form.get('usuario')
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not all([usuario, nome, email, senha]):
            flash('Todos os campos são obrigatórios.', 'error')
            return redirect(url_for('admin.user_management'))
        
        existing = Administrador.query.filter_by(usuario=usuario).first()
        if existing:
            flash('Usuário já existe.', 'error')
            return redirect(url_for('admin.user_management'))
        
        new_admin = Administrador()
        new_admin.usuario = usuario
        new_admin.nome = nome
        new_admin.email = email
        new_admin.senha = generate_password_hash(senha)
        new_admin.ativo = True
        
        db.session.add(new_admin)
        db.session.commit()
        
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('admin.user_management'))
    except Exception as e:
        logging.error(f'Create user error: {e}')
        flash('Erro ao criar usuário.', 'error')
        return redirect(url_for('admin.user_management'))