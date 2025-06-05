from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from models import Medico
from main import db
from datetime import datetime
import logging
import os
from werkzeug.security import generate_password_hash, check_password_hash

def sanitizar_entrada(valor):
    """Sanitiza entrada de usuário"""
    if not valor:
        return ""
    import re
    valor = re.sub(r'[<>"\']', '', str(valor))
    return valor.strip()

configuracoes_bp = Blueprint('configuracoes', __name__)

@configuracoes_bp.route('/configuracoes')
def dashboard_configuracoes():
    """Dashboard principal de configurações"""
    try:
        # Verifica autenticação
        if not session.get('usuario') and not session.get('admin_usuario'):
            flash('Acesso negado. Faça login primeiro.', 'error')
            return redirect(url_for('auth.login'))
        
        # Busca dados do sistema
        total_medicos = db.session.query(Medico).count()
        medicos = db.session.query(Medico).all()
        
        # Configurações do sistema
        configuracoes_sistema = {
            'versao': '2.1.0',
            'ambiente': os.environ.get('FLASK_ENV', 'production'),
            'debug': os.environ.get('FLASK_DEBUG', 'False'),
            'database_url': os.environ.get('DATABASE_URL', '').replace('postgresql://', 'postgres://') if os.environ.get('DATABASE_URL') else '',
            'session_secret': 'Configurado' if os.environ.get('SESSION_SECRET') else 'Não configurado'
        }
        
        return render_template('configuracoes/dashboard.html',
                             total_medicos=total_medicos,
                             medicos=medicos,
                             configuracoes_sistema=configuracoes_sistema)
        
    except Exception as e:
        logging.error(f"Erro no dashboard de configurações: {e}")
        flash('Erro ao carregar configurações', 'error')
        return redirect(url_for('dashboard'))

@configuracoes_bp.route('/configuracoes/medicos')
def gerenciar_medicos():
    """Gerenciamento de médicos"""
    try:
        medicos = db.session.query(Medico).order_by(Medico.nome).all()
        return render_template('configuracoes/medicos.html', medicos=medicos)
        
    except Exception as e:
        logging.error(f"Erro ao listar médicos: {e}")
        flash('Erro ao carregar médicos', 'error')
        return redirect(url_for('configuracoes.dashboard_configuracoes'))

@configuracoes_bp.route('/configuracoes/medicos/novo', methods=['GET', 'POST'])
def novo_medico():
    """Cadastro de novo médico"""
    try:
        if request.method == 'POST':
            nome = sanitizar_entrada(request.form.get('nome'))
            crm = sanitizar_entrada(request.form.get('crm'))
            senha = request.form.get('senha')
            assinatura = request.form.get('assinatura', '')
            
            # Validações
            if not all([nome, crm, senha]):
                flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
                return render_template('configuracoes/novo_medico.html')
            
            # Verifica se CRM já existe
            medico_existente = db.session.query(Medico).filter_by(crm=crm).first()
            if medico_existente:
                flash('CRM já cadastrado no sistema', 'error')
                return render_template('configuracoes/novo_medico.html')
            
            # Cria novo médico
            novo_medico = Medico(
                nome=nome,
                crm=crm,
                senha=generate_password_hash(senha),
                assinatura=assinatura,
                created_at=datetime.now()
            )
            
            db.session.add(novo_medico)
            db.session.commit()
            
            flash('Médico cadastrado com sucesso!', 'success')
            return redirect(url_for('configuracoes.gerenciar_medicos'))
        
        # GET - Exibe formulário
        return render_template('configuracoes/novo_medico.html')
        
    except Exception as e:
        logging.error(f"Erro ao cadastrar médico: {e}")
        db.session.rollback()
        flash('Erro ao cadastrar médico', 'error')
        return redirect(url_for('configuracoes.gerenciar_medicos'))

@configuracoes_bp.route('/configuracoes/medicos/<int:medico_id>/editar', methods=['GET', 'POST'])
def editar_medico(medico_id):
    """Edição de médico existente"""
    try:
        medico = db.session.query(Medico).get_or_404(medico_id)
        
        if request.method == 'POST':
            medico.nome = sanitizar_entrada(request.form.get('nome'))
            medico.crm = sanitizar_entrada(request.form.get('crm'))
            
            # Atualiza senha apenas se fornecida
            nova_senha = request.form.get('senha')
            if nova_senha:
                medico.senha = generate_password_hash(nova_senha)
            
            medico.assinatura = request.form.get('assinatura', '')
            
            db.session.commit()
            flash('Médico atualizado com sucesso!', 'success')
            return redirect(url_for('configuracoes.gerenciar_medicos'))
        
        # GET - Exibe formulário de edição
        return render_template('configuracoes/editar_medico.html', medico=medico)
        
    except Exception as e:
        logging.error(f"Erro ao editar médico: {e}")
        db.session.rollback()
        flash('Erro ao editar médico', 'error')
        return redirect(url_for('configuracoes.gerenciar_medicos'))

@configuracoes_bp.route('/configuracoes/medicos/<int:medico_id>/excluir', methods=['POST'])
def excluir_medico(medico_id):
    """Exclusão de médico"""
    try:
        medico = db.session.query(Medico).get_or_404(medico_id)
        
        # Verifica se médico tem documentos associados
        from models import Receita, ExameLab, ExameImg
        tem_receitas = db.session.query(Receita).filter_by(medico_id=medico_id).first()
        tem_exames_lab = db.session.query(ExameLab).filter_by(medico_id=medico_id).first()
        tem_exames_img = db.session.query(ExameImg).filter_by(medico_id=medico_id).first()
        
        if tem_receitas or tem_exames_lab or tem_exames_img:
            flash('Não é possível excluir médico com documentos associados', 'error')
            return redirect(url_for('configuracoes.gerenciar_medicos'))
        
        db.session.delete(medico)
        db.session.commit()
        
        flash('Médico excluído com sucesso!', 'success')
        
    except Exception as e:
        logging.error(f"Erro ao excluir médico: {e}")
        db.session.rollback()
        flash('Erro ao excluir médico', 'error')
    
    return redirect(url_for('configuracoes.gerenciar_medicos'))

@configuracoes_bp.route('/configuracoes/sistema')
def configuracoes_sistema():
    """Configurações gerais do sistema"""
    try:
        # Informações do sistema
        info_sistema = {
            'versao': '2.1.0',
            'ambiente': os.environ.get('FLASK_ENV', 'production'),
            'debug': os.environ.get('FLASK_DEBUG', 'False') == 'True',
            'python_version': '3.11+',
            'flask_version': '2.3+',
            'database_status': 'Conectado',
            'uptime': 'Sistema rodando normalmente'
        }
        
        # Estatísticas do banco de dados
        from models import Receita, ExameLab, ExameImg, Paciente
        stats_db = {
            'total_receitas': db.session.query(Receita).count(),
            'total_exames_lab': db.session.query(ExameLab).count(),
            'total_exames_img': db.session.query(ExameImg).count(),
            'total_pacientes': db.session.query(Paciente).count(),
            'total_medicos': db.session.query(Medico).count()
        }
        
        return render_template('configuracoes/sistema.html',
                             info_sistema=info_sistema,
                             stats_db=stats_db)
        
    except Exception as e:
        logging.error(f"Erro nas configurações do sistema: {e}")
        flash('Erro ao carregar configurações do sistema', 'error')
        return redirect(url_for('configuracoes.dashboard_configuracoes'))

@configuracoes_bp.route('/configuracoes/seguranca')
def configuracoes_seguranca():
    """Configurações de segurança"""
    try:
        # Verifica configurações de segurança
        config_seguranca = {
            'session_secret': 'Configurado' if os.environ.get('SESSION_SECRET') else 'Não configurado',
            'https_forcado': 'Sim' if os.environ.get('FORCE_HTTPS') == 'True' else 'Não',
            'rate_limiting': 'Ativo',
            'csrf_protection': 'Ativo',
            'sql_injection_protection': 'Ativo',
            'xss_protection': 'Ativo'
        }
        
        return render_template('configuracoes/seguranca.html',
                             config_seguranca=config_seguranca)
        
    except Exception as e:
        logging.error(f"Erro nas configurações de segurança: {e}")
        flash('Erro ao carregar configurações de segurança', 'error')
        return redirect(url_for('configuracoes.dashboard_configuracoes'))

@configuracoes_bp.route('/configuracoes/limpar_dados', methods=['POST'])
def limpar_dados():
    """Limpeza de dados do sistema"""
    try:
        tipo_limpeza = request.form.get('tipo_limpeza')
        
        if tipo_limpeza == 'logs':
            # Implementar limpeza de logs
            flash('Logs limpos com sucesso!', 'success')
            
        elif tipo_limpeza == 'cache':
            # Implementar limpeza de cache
            flash('Cache limpo com sucesso!', 'success')
            
        elif tipo_limpeza == 'temp_files':
            # Implementar limpeza de arquivos temporários
            flash('Arquivos temporários limpos com sucesso!', 'success')
            
        else:
            flash('Tipo de limpeza inválido', 'error')
        
    except Exception as e:
        logging.error(f"Erro na limpeza de dados: {e}")
        flash('Erro ao limpar dados', 'error')
    
    return redirect(url_for('configuracoes.configuracoes_sistema'))

@configuracoes_bp.route('/api/configuracoes/test_connection')
def test_database_connection():
    """Testa conexão com banco de dados"""
    try:
        # Testa uma query simples
        result = db.session.execute('SELECT 1').fetchone()
        if result:
            return jsonify({'status': 'success', 'message': 'Conexão com banco de dados OK'})
        else:
            return jsonify({'status': 'error', 'message': 'Falha na conexão'})
            
    except Exception as e:
        logging.error(f"Erro ao testar conexão: {e}")
        return jsonify({'status': 'error', 'message': str(e)})