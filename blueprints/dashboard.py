"""
Blueprint do Dashboard - Sistema Médico VIDAH
Painel principal com estatísticas e acesso rápido
"""
from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from functools import wraps
import logging

# Import database and models
from core.database import db
from models import Paciente, Receita, ExameLab, ExameImg, Medico, AtestadoMedico


import logging
import traceback

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)


def sanitize_input(text):
    """Sanitiza entrada do usuário"""
    if not text:
        return ""
    return str(text).strip()


dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def require_auth():
    """Decorator para verificar autenticação"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'usuario' not in session:
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@dashboard_bp.route('/')
@require_auth()
def index():
    """Dashboard principal do sistema"""
    user = session.get('usuario') or session.get('admin_usuario')
    user_type = session.get('usuario_tipo', 'medico')
    
    if not user:
        return redirect(url_for('auth.login'))
    
    try:
        # Estatísticas gerais
        stats = get_dashboard_statistics(user_type, user)
        
        # Atividades recentes
        recent_activities = get_recent_activities(user_type, user)
        
        # Dados para gráficos
        chart_data = get_chart_data(user_type, user)
        
        logger.info(f"Dashboard loaded for {user} ({user_type})")
        
        return render_template('dashboard.html', 
                             stats=stats,
                             recent_activities=recent_activities,
                             chart_data=chart_data,
                             user=user,
                             user_type=user_type)
                             
    except Exception as e:
        print(f"Dashboard error for {user}: {str(e)}")
        return render_template('dashboard.html',
                             stats={},
                             recent_activities=[],
                             chart_data={},
                             user=user,
                             user_type=user_type,
                             error="Erro ao carregar dashboard")


@dashboard_bp.route('/api/stats')
@require_auth()
def api_stats():
    """API para estatísticas do dashboard"""
    user = session.get('usuario') or session.get('admin_usuario')
    user_type = session.get('usuario_tipo', 'medico')
    
    try:
        stats = get_dashboard_statistics(user_type, user)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats API error: {str(e)}")
        return jsonify({'error': 'Erro ao carregar estatísticas'}), 500


@dashboard_bp.route('/api/activities')
@require_auth()
def api_activities():
    """API para atividades recentes"""
    user = session.get('usuario') or session.get('admin_usuario')
    user_type = session.get('usuario_tipo', 'medico')
    
    try:
        activities = get_recent_activities(user_type, user)
        return jsonify(activities)
    except Exception as e:
        logger.error(f"Activities API error: {str(e)}")
        return jsonify({'error': 'Erro ao carregar atividades'}), 500


def get_dashboard_statistics(user_type, user):
    """Calcula estatísticas para o dashboard"""
    stats = {}
    
    logger.info(f"=== INICIANDO CÁLCULO DE ESTATÍSTICAS ===")
    logger.info(f"User type: {user_type}")
    logger.info(f"User data: {user}")
    logger.info(f"User type is dict: {isinstance(user, dict)}")
    
    try:
        # Data de hoje e última semana
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        if user_type == 'admin':
            # Estatísticas administrativas
            stats['total_receitas'] = logger.debug("Executando query: contagem de receitas")
        db.session.query(func.count(Receita.id)).scalar() or 0
        logger.debug(f"Resultado da query: {result}")
            stats['total_exames_lab'] = logger.debug("Executando query: contagem de exames lab")
        db.session.query(func.count(ExameLab.id)).scalar() or 0
        logger.debug(f"Resultado da query: {result}")
            stats['total_exames_img'] = logger.debug("Executando query: contagem de exames img")
        db.session.query(func.count(ExameImg.id)).scalar() or 0
        logger.debug(f"Resultado da query: {result}")
            stats['total_atestados'] = db.session.query(func.count(AtestadoMedico.id)).scalar() or 0
            stats['total_pacientes'] = logger.debug("Executando query: contagem de pacientes")
        db.session.query(func.count(Paciente.id)).scalar() or 0
        logger.debug(f"Resultado da query: {result}")
            stats['total_medicos'] = logger.debug("Executando query: contagem de médicos")
        db.session.query(func.count(Medico.id)).scalar() or 0
        logger.debug(f"Resultado da query: {result}")
            
            # Atividades da semana
            stats['receitas_semana'] = logger.debug("Executando query: contagem de receitas")
        result = db.session.query(func.count(Receita.id)).filter(
                func.date(Receita.data_criacao) >= week_ago
            ).scalar() or 0
            
            stats['exames_semana'] = (
                logger.debug("Executando query: contagem de exames lab")
        result = db.session.query(func.count(ExameLab.id)).filter(
                    func.date(ExameLab.created_at) >= week_ago
                ).scalar() or 0
            ) + (
                logger.debug("Executando query: contagem de exames img")
        result = db.session.query(func.count(ExameImg.id)).filter(
                    func.date(ExameImg.created_at) >= week_ago
                ).scalar() or 0
            )
            
        else:
            # Estatísticas do médico - corrigindo query com user sendo dict
            user_name = user.get('nome') if isinstance(user, dict) else user
            medico = db.session.query(Medico).filter_by(nome=user_name).first()
            if medico:
                stats['total_receitas'] = logger.debug("Executando query: contagem de receitas")
        result = db.session.query(func.count(Receita.id)).filter_by(id_medico=medico.id).scalar() or 0
                stats['total_exames_lab'] = logger.debug("Executando query: contagem de exames lab")
        result = db.session.query(func.count(ExameLab.id)).filter_by(id_medico=medico.id).scalar() or 0
                stats['total_exames_img'] = logger.debug("Executando query: contagem de exames img")
        result = db.session.query(func.count(ExameImg.id)).filter_by(id_medico=medico.id).scalar() or 0
                stats['total_atestados'] = db.session.query(func.count(AtestadoMedico.id)).filter_by(id_medico=medico.id).scalar() or 0
                
                # Pacientes únicos atendidos
                stats['total_pacientes'] = db.session.query(func.count(func.distinct(Receita.nome_paciente))).filter_by(id_medico=medico.id).scalar() or 0
                
                # Atividades da semana
                stats['receitas_semana'] = logger.debug("Executando query: contagem de receitas")
        result = db.session.query(func.count(Receita.id)).filter(
                    Receita.id_medico == medico.id,
                    func.date(Receita.data_criacao) >= week_ago
                ).scalar() or 0
                
                stats['exames_semana'] = (
                    logger.debug("Executando query: contagem de exames lab")
        result = db.session.query(func.count(ExameLab.id)).filter(
                        ExameLab.id_medico == medico.id,
                        func.date(ExameLab.created_at) >= week_ago
                    ).scalar() or 0
                ) + (
                    logger.debug("Executando query: contagem de exames img")
        result = db.session.query(func.count(ExameImg.id)).filter(
                        ExameImg.id_medico == medico.id,
                        func.date(ExameImg.created_at) >= week_ago
                    ).scalar() or 0
                )
        
        # Calcular tendências
        stats['receitas_mes'] = get_monthly_count(Receita, user_type, user, month_ago)
        stats['exames_mes'] = get_monthly_count(ExameLab, user_type, user, month_ago) + get_monthly_count(ExameImg, user_type, user, month_ago)
        
    except Exception as e:
        logger.error(f"=== ERRO CRÍTICO NO CÁLCULO DE ESTATÍSTICAS ===")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        logger.error(f"Mensagem: {str(e)}")
        logger.error(f"Traceback completo:")
        logger.error(traceback.format_exc())
        logger.error(f"User type: {user_type}")
        logger.error(f"User data: {user}")
        stats = {
            'total_receitas': 0,
            'total_exames_lab': 0,
            'total_exames_img': 0,
            'total_atestados': 0,
            'total_pacientes': 0,
            'receitas_semana': 0,
            'exames_semana': 0
        }
    
    return stats


def get_monthly_count(model, user_type, user, month_ago):
    """Conta registros do último mês"""
    try:
        query = db.session.query(func.count(model.id))
        
        if user_type != 'admin' and hasattr(model, 'medico'):
            query = query.filter(model.medico == user)
        
        if hasattr(model, 'data_criacao'):
            query = query.filter(func.date(model.data_criacao) >= month_ago)
        
        return query.scalar() or 0
    except:
        return 0


def get_recent_activities(user_type, user):
    """Busca atividades recentes do usuário"""
    activities = []
    
    try:
        if user_type == 'admin':
            # Atividades administrativas
            receitas = db.session.query(Receita).order_by(Receita.data_criacao.desc()).limit(5).all()
            for receita in receitas:
                activities.append({
                    'tipo': 'Receita',
                    'descricao': f'Receita para {receita.nome_paciente}',
                    'data': receita.data_criacao.strftime('%d/%m/%Y %H:%M') if receita.data_criacao else receita.data,
                    'medico': receita.medico_nome
                })
        else:
            # Atividades do médico
            user_name = user.get('nome') if isinstance(user, dict) else user
            medico = db.session.query(Medico).filter_by(nome=user_name).first()
            
            if medico:
                receitas = db.session.query(Receita).filter_by(id_medico=medico.id).order_by(Receita.data_criacao.desc()).limit(5).all()
                for receita in receitas:
                    activities.append({
                        'tipo': 'Receita',
                        'descricao': f'Receita para {receita.nome_paciente}',
                        'data': receita.data_criacao.strftime('%d/%m/%Y %H:%M') if receita.data_criacao else receita.data,
                        'medico': receita.medico_nome
                    })
                
                # Adicionar exames
                exames_lab = db.session.query(ExameLab).filter_by(id_medico=medico.id).order_by(ExameLab.created_at.desc()).limit(3).all()
                for exame in exames_lab:
                    activities.append({
                        'tipo': 'Exame Lab',
                        'descricao': f'Exames para {exame.nome_paciente}',
                        'data': exame.created_at.strftime('%d/%m/%Y %H:%M') if exame.created_at else exame.data,
                        'medico': exame.medico_nome
                    })
        
    except Exception as e:
        logger.error(f"Error getting activities: {str(e)}")
    
    return activities[:10]  # Limitar a 10 atividades


def get_chart_data(user_type, user):
    """Dados para gráficos do dashboard"""
    chart_data = {
        'labels': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        'receitas': [0, 0, 0, 0, 0, 0],
        'exames': [0, 0, 0, 0, 0, 0]
    }
    
    try:
        from datetime import datetime, timedelta
        now = datetime.now()
        
        if user_type == 'admin':
            # Dados administrativos dos últimos 6 meses
            for i in range(6):
                month_start = (now.replace(day=1) - timedelta(days=30*i))
                month_end = month_start + timedelta(days=30)
                
                receitas_count = logger.debug("Executando query: contagem de receitas")
        result = db.session.query(func.count(Receita.id)).filter(
                    Receita.data_criacao >= month_start,
                    Receita.data_criacao < month_end
                ).scalar() or 0
                
                exames_count = (
                    logger.debug("Executando query: contagem de exames lab")
        result = db.session.query(func.count(ExameLab.id)).filter(
                        ExameLab.created_at >= month_start,
                        ExameLab.created_at < month_end
                    ).scalar() or 0
                ) + (
                    logger.debug("Executando query: contagem de exames img")
        result = db.session.query(func.count(ExameImg.id)).filter(
                        ExameImg.created_at >= month_start,
                        ExameImg.created_at < month_end
                    ).scalar() or 0
                )
                
                chart_data['receitas'][5-i] = receitas_count
                chart_data['exames'][5-i] = exames_count
        else:
            # Dados do médico
            user_name = user.get('nome') if isinstance(user, dict) else user
            medico = db.session.query(Medico).filter_by(nome=user_name).first()
            
            if medico:
                for i in range(6):
                    month_start = (now.replace(day=1) - timedelta(days=30*i))
                    month_end = month_start + timedelta(days=30)
                    
                    receitas_count = logger.debug("Executando query: contagem de receitas")
        result = db.session.query(func.count(Receita.id)).filter(
                        Receita.id_medico == medico.id,
                        Receita.data_criacao >= month_start,
                        Receita.data_criacao < month_end
                    ).scalar() or 0
                    
                    chart_data['receitas'][5-i] = receitas_count
        
    except Exception as e:
        logger.error(f"Error getting chart data: {str(e)}")
    
    return chart_data