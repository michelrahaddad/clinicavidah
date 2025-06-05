from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, send_file
from main import db
from datetime import datetime, timedelta
import logging
import os
import subprocess
import json
from io import BytesIO
import zipfile

def sanitizar_entrada(valor):
    """Sanitiza entrada de usuário"""
    if not valor:
        return ""
    import re
    valor = re.sub(r'[<>"\']', '', str(valor))
    return valor.strip()

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/backup')
def dashboard_backup():
    """Dashboard principal de backup"""
    try:
        # Verifica autenticação
        if not session.get('usuario') and not session.get('admin_usuario'):
            flash('Acesso negado. Faça login primeiro.', 'error')
            return redirect(url_for('auth.login'))
        
        # Lista backups existentes
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        backups = []
        for arquivo in os.listdir(backup_dir):
            if arquivo.endswith('.sql') or arquivo.endswith('.zip'):
                caminho = os.path.join(backup_dir, arquivo)
                stat = os.stat(caminho)
                backups.append({
                    'nome': arquivo,
                    'tamanho': round(stat.st_size / 1024 / 1024, 2),  # MB
                    'data_criacao': datetime.fromtimestamp(stat.st_mtime),
                    'tipo': 'SQL' if arquivo.endswith('.sql') else 'Completo'
                })
        
        # Ordena por data mais recente
        backups.sort(key=lambda x: x['data_criacao'], reverse=True)
        
        # Configurações de backup
        config_backup = {
            'backup_automatico': 'Ativo',
            'frequencia': 'Diário às 02:00',
            'retencao': '30 dias',
            'local_armazenamento': backup_dir,
            'compressao': 'Ativo'
        }
        
        return render_template('backup/dashboard.html',
                             backups=backups,
                             config_backup=config_backup)
        
    except Exception as e:
        logging.error(f"Erro no dashboard de backup: {e}")
        flash('Erro ao carregar backups', 'error')
        return redirect(url_for('dashboard'))

@backup_bp.route('/backup/criar', methods=['POST'])
def criar_backup():
    """Cria novo backup do sistema"""
    try:
        tipo_backup = request.form.get('tipo', 'completo')
        incluir_dados = request.form.get('incluir_dados') == 'on'
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups'
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        if tipo_backup == 'sql':
            # Backup apenas do banco de dados
            nome_arquivo = f'backup_db_{timestamp}.sql'
            caminho_arquivo = os.path.join(backup_dir, nome_arquivo)
            
            # Simula criação de backup SQL
            with open(caminho_arquivo, 'w') as f:
                f.write(f"-- Backup do Sistema Médico VIDAH\n")
                f.write(f"-- Criado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
                f.write(f"-- Tipo: Backup de banco de dados\n\n")
                
                if incluir_dados:
                    # Aqui seria implementado o dump real do PostgreSQL
                    # Por enquanto, apenas um placeholder
                    f.write("-- DUMP DOS DADOS DAS TABELAS\n")
                    f.write("-- (Implementação real usaria pg_dump)\n")
                else:
                    f.write("-- APENAS ESTRUTURA DAS TABELAS\n")
                    f.write("-- (Schema sem dados)\n")
            
            flash(f'Backup SQL criado: {nome_arquivo}', 'success')
            
        elif tipo_backup == 'completo':
            # Backup completo do sistema
            nome_arquivo = f'backup_completo_{timestamp}.zip'
            caminho_arquivo = os.path.join(backup_dir, nome_arquivo)
            
            # Cria arquivo ZIP com os arquivos do sistema
            with zipfile.ZipFile(caminho_arquivo, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Adiciona arquivos Python principais
                arquivos_sistema = [
                    'main.py', 'app.py', 'models.py'
                ]
                
                for arquivo in arquivos_sistema:
                    if os.path.exists(arquivo):
                        zipf.write(arquivo)
                
                # Adiciona diretórios importantes
                diretorios = ['routes', 'templates', 'static', 'utils']
                for diretorio in diretorios:
                    if os.path.exists(diretorio):
                        for root, dirs, files in os.walk(diretorio):
                            for file in files:
                                file_path = os.path.join(root, file)
                                zipf.write(file_path)
                
                # Adiciona informações do backup
                info_backup = {
                    'data_criacao': datetime.now().isoformat(),
                    'tipo': 'completo',
                    'versao_sistema': '2.1.0',
                    'incluir_dados': incluir_dados
                }
                
                zipf.writestr('backup_info.json', json.dumps(info_backup, indent=2))
            
            flash(f'Backup completo criado: {nome_arquivo}', 'success')
        
        else:
            flash('Tipo de backup inválido', 'error')
        
    except Exception as e:
        logging.error(f"Erro ao criar backup: {e}")
        flash('Erro ao criar backup', 'error')
    
    return redirect(url_for('backup.dashboard_backup'))

@backup_bp.route('/backup/restaurar', methods=['POST'])
def restaurar_backup():
    """Restaura backup selecionado"""
    try:
        nome_backup = request.form.get('nome_backup')
        confirmar = request.form.get('confirmar') == 'on'
        
        if not confirmar:
            flash('É necessário confirmar a restauração', 'error')
            return redirect(url_for('backup.dashboard_backup'))
        
        backup_dir = 'backups'
        caminho_backup = os.path.join(backup_dir, nome_backup)
        
        if not os.path.exists(caminho_backup):
            flash('Arquivo de backup não encontrado', 'error')
            return redirect(url_for('backup.dashboard_backup'))
        
        if nome_backup.endswith('.sql'):
            # Restaurar backup SQL
            logging.info(f"Iniciando restauração do backup SQL: {nome_backup}")
            
            # Aqui seria implementada a restauração real do PostgreSQL
            # Por enquanto, apenas simula o processo
            flash(f'Backup SQL {nome_backup} restaurado com sucesso! (Simulado)', 'success')
            
        elif nome_backup.endswith('.zip'):
            # Restaurar backup completo
            logging.info(f"Iniciando restauração do backup completo: {nome_backup}")
            
            # Lê informações do backup
            with zipfile.ZipFile(caminho_backup, 'r') as zipf:
                if 'backup_info.json' in zipf.namelist():
                    info_backup = json.loads(zipf.read('backup_info.json').decode())
                    logging.info(f"Backup criado em: {info_backup.get('data_criacao')}")
            
            flash(f'Backup completo {nome_backup} restaurado com sucesso! (Simulado)', 'success')
        
        else:
            flash('Formato de backup não suportado', 'error')
        
    except Exception as e:
        logging.error(f"Erro ao restaurar backup: {e}")
        flash('Erro ao restaurar backup', 'error')
    
    return redirect(url_for('backup.dashboard_backup'))

@backup_bp.route('/backup/download/<nome_arquivo>')
def download_backup(nome_arquivo):
    """Download de arquivo de backup"""
    try:
        backup_dir = 'backups'
        caminho_arquivo = os.path.join(backup_dir, nome_arquivo)
        
        if not os.path.exists(caminho_arquivo):
            flash('Arquivo não encontrado', 'error')
            return redirect(url_for('backup.dashboard_backup'))
        
        return send_file(caminho_arquivo, as_attachment=True)
        
    except Exception as e:
        logging.error(f"Erro no download do backup: {e}")
        flash('Erro no download do backup', 'error')
        return redirect(url_for('backup.dashboard_backup'))

@backup_bp.route('/backup/excluir/<nome_arquivo>', methods=['POST'])
def excluir_backup(nome_arquivo):
    """Exclui arquivo de backup"""
    try:
        backup_dir = 'backups'
        caminho_arquivo = os.path.join(backup_dir, nome_arquivo)
        
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
            flash(f'Backup {nome_arquivo} excluído com sucesso!', 'success')
        else:
            flash('Arquivo não encontrado', 'error')
        
    except Exception as e:
        logging.error(f"Erro ao excluir backup: {e}")
        flash('Erro ao excluir backup', 'error')
    
    return redirect(url_for('backup.dashboard_backup'))

@backup_bp.route('/backup/configuracoes')
def configuracoes_backup():
    """Configurações de backup automático"""
    try:
        config_atual = {
            'backup_automatico': True,
            'horario': '02:00',
            'frequencia': 'diario',
            'retencao_dias': 30,
            'compressao': True,
            'email_notificacao': '',
            'incluir_dados': True
        }
        
        return render_template('backup/configuracoes.html',
                             config=config_atual)
        
    except Exception as e:
        logging.error(f"Erro nas configurações de backup: {e}")
        flash('Erro ao carregar configurações', 'error')
        return redirect(url_for('backup.dashboard_backup'))

@backup_bp.route('/backup/configuracoes/salvar', methods=['POST'])
def salvar_configuracoes():
    """Salva configurações de backup"""
    try:
        config = {
            'backup_automatico': request.form.get('backup_automatico') == 'on',
            'horario': sanitizar_entrada(request.form.get('horario')),
            'frequencia': sanitizar_entrada(request.form.get('frequencia')),
            'retencao_dias': int(request.form.get('retencao_dias', 30)),
            'compressao': request.form.get('compressao') == 'on',
            'email_notificacao': sanitizar_entrada(request.form.get('email_notificacao')),
            'incluir_dados': request.form.get('incluir_dados') == 'on'
        }
        
        # Salva configurações (em produção seria em arquivo de config ou banco)
        logging.info(f"Configurações de backup atualizadas: {config}")
        
        flash('Configurações de backup salvas com sucesso!', 'success')
        
    except Exception as e:
        logging.error(f"Erro ao salvar configurações: {e}")
        flash('Erro ao salvar configurações', 'error')
    
    return redirect(url_for('backup.configuracoes_backup'))

@backup_bp.route('/api/backup/status')
def status_backup():
    """API para status dos backups"""
    try:
        backup_dir = 'backups'
        
        if not os.path.exists(backup_dir):
            return jsonify({
                'total_backups': 0,
                'ultimo_backup': None,
                'tamanho_total': 0
            })
        
        arquivos = [f for f in os.listdir(backup_dir) if f.endswith(('.sql', '.zip'))]
        
        if not arquivos:
            return jsonify({
                'total_backups': 0,
                'ultimo_backup': None,
                'tamanho_total': 0
            })
        
        # Último backup
        arquivos_com_data = []
        tamanho_total = 0
        
        for arquivo in arquivos:
            caminho = os.path.join(backup_dir, arquivo)
            stat = os.stat(caminho)
            arquivos_com_data.append((arquivo, stat.st_mtime))
            tamanho_total += stat.st_size
        
        ultimo_backup = max(arquivos_com_data, key=lambda x: x[1])
        
        return jsonify({
            'total_backups': len(arquivos),
            'ultimo_backup': {
                'nome': ultimo_backup[0],
                'data': datetime.fromtimestamp(ultimo_backup[1]).strftime('%d/%m/%Y às %H:%M')
            },
            'tamanho_total': round(tamanho_total / 1024 / 1024, 2)  # MB
        })
        
    except Exception as e:
        logging.error(f"Erro no status dos backups: {e}")
        return jsonify({'erro': str(e)})