"""
Blueprint do Dashboard - Sistema Médico VIDAH (Versão Corrigida)
Painel principal com estatísticas e acesso rápido
"""
from flask import Blueprint, render_template, session, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
from sqlalchemy import func
import calendar
import logging
import traceback

# Import database and models
from core.database import db
from models import Paciente, Receita, ExameLab, ExameImg, Medico, AtestadoMedico

logger = logging.getLogger(__name__)

def sanitize_input(text):
    """Sanitiza entrada do usuário"""
    if not text:
        return ""
    import re
    return re.sub(r'[<>"\']', '', str(text))

def require_auth():
    """Decorator para verificar autenticação"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if 'usuario' not in session:
                return redirect('/auth/login')
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# Blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@require_auth()
def index():
    """Dashboard principal do sistema"""
    try:
        logger.info("=== CARREGANDO DASHBOARD ===")
        user = session.get('usuario')
        logger.info(f"Usuario da sessão: {user}")
        
        if not user:
            logger.warning("Usuário não encontrado na sessão")
            return redirect('/auth/login')
        
        user_type = user.get('tipo', 'medico')
        logger.info(f"Tipo de usuário: {user_type}")
        
        # Calcular estatísticas
        stats = get_dashboard_statistics(user_type, user)
        logger.info(f"Estatísticas calculadas: {stats}")
        
        # Atividades recentes
        activities = get_recent_activities(user_type, user)
        logger.info(f"Atividades encontradas: {len(activities)}")
        
        # Dados para gráficos
        chart_data = get_chart_data(user_type, user)
        logger.info(f"Dados do gráfico: {chart_data}")
        
        logger.info(f"Dashboard loaded for {user} ({user_type})")
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             activities=activities,
                             chart_data=chart_data,
                             user=user)
                             
    except Exception as e:
        logger.error(f"Erro crítico no dashboard: {e}")
        logger.error(traceback.format_exc())
        # Retornar dashboard com dados vazios em caso de erro
        return render_template('dashboard.html', 
                             stats={}, 
                             activities=[],
                             chart_data={},
                             user=session.get('usuario', {}))

@dashboard_bp.route('/api/stats')
@require_auth()
def api_stats():
    """API para estatísticas do dashboard"""
    try:
        user = session.get('usuario')
        user_type = user.get('tipo', 'medico')
        stats = get_dashboard_statistics(user_type, user)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Erro na API de stats: {e}")
        return jsonify({})

@dashboard_bp.route('/api/activities')
@require_auth()
def api_activities():
    """API para atividades recentes"""
    try:
        user = session.get('usuario')
        user_type = user.get('tipo', 'medico')
        activities = get_recent_activities(user_type, user)
        return jsonify(activities)
    except Exception as e:
        logger.error(f"Erro na API de atividades: {e}")
        return jsonify([])

def get_dashboard_statistics(user_type, user):
    """Calcula estatísticas para o dashboard"""
    stats = {}
    
    logger.info(f"=== CALCULANDO ESTATÍSTICAS ===")
    logger.info(f"User type: {user_type}")
    logger.info(f"User data: {user}")
    
    try:
        if user_type == 'medico':
            # Buscar médico no banco
            medico = db.session.query(Medico).filter_by(nome=user['nome']).first()
            logger.info(f"Médico encontrado: {medico.nome if medico else 'None'}")
            
            if medico:
                # Estatísticas do médico específico
                logger.debug("Contando receitas...")
                stats['total_receitas'] = db.session.query(func.count(Receita.id)).filter_by(id_medico=medico.id).scalar() or 0
                logger.debug(f"Receitas: {stats['total_receitas']}")
                
                logger.debug("Contando exames lab...")
                stats['total_exames_lab'] = db.session.query(func.count(ExameLab.id)).filter_by(id_medico=medico.id).scalar() or 0
                logger.debug(f"Exames Lab: {stats['total_exames_lab']}")
                
                logger.debug("Contando exames img...")
                stats['total_exames_img'] = db.session.query(func.count(ExameImg.id)).filter_by(id_medico=medico.id).scalar() or 0
                logger.debug(f"Exames Img: {stats['total_exames_img']}")
                
                logger.debug("Contando atestados...")
                stats['total_atestados'] = db.session.query(func.count(AtestadoMedico.id)).filter_by(id_medico=medico.id).scalar() or 0
                logger.debug(f"Atestados: {stats['total_atestados']}")
                
                # Contar pacientes únicos
                logger.debug("Contando pacientes únicos...")
                pacientes_ids = db.session.query(Receita.id_paciente).filter_by(id_medico=medico.id).distinct().all()
                stats['total_pacientes'] = len(pacientes_ids)
                logger.debug(f"Pacientes únicos: {stats['total_pacientes']}")
                
            else:
                logger.warning("Médico não encontrado - retornando estatísticas zeradas")
                stats = {
                    'total_receitas': 0,
                    'total_exames_lab': 0,
                    'total_exames_img': 0,
                    'total_atestados': 0,
                    'total_pacientes': 0
                }
        
        elif user_type == 'admin':
            # Estatísticas gerais para administradores
            logger.debug("Calculando estatísticas de admin...")
            stats['total_receitas'] = db.session.query(func.count(Receita.id)).scalar() or 0
            stats['total_exames_lab'] = db.session.query(func.count(ExameLab.id)).scalar() or 0
            stats['total_exames_img'] = db.session.query(func.count(ExameImg.id)).scalar() or 0
            stats['total_atestados'] = db.session.query(func.count(AtestadoMedico.id)).scalar() or 0
            stats['total_pacientes'] = db.session.query(func.count(Paciente.id)).scalar() or 0
            stats['total_medicos'] = db.session.query(func.count(Medico.id)).scalar() or 0
        
        # Adicionar estatísticas do mês atual
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)
        
        if user_type == 'medico' and medico:
            stats['receitas_mes'] = db.session.query(func.count(Receita.id)).filter(
                Receita.id_medico == medico.id,
                Receita.data_criacao >= month_start
            ).scalar() or 0
        else:
            stats['receitas_mes'] = db.session.query(func.count(Receita.id)).filter(
                Receita.data_criacao >= month_start
            ).scalar() or 0
        
        logger.info(f"Estatísticas finais: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"=== ERRO CRÍTICO NO CÁLCULO DE ESTATÍSTICAS ===")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        logger.error(f"Mensagem: {str(e)}")
        logger.error(f"Traceback completo:")
        logger.error(traceback.format_exc())
        logger.error(f"User type: {user_type}")
        logger.error(f"User data: {user}")
        
        # Retornar estatísticas zeradas em caso de erro
        return {
            'total_receitas': 0,
            'total_exames_lab': 0,
            'total_exames_img': 0,
            'total_atestados': 0,
            'total_pacientes': 0,
            'receitas_mes': 0
        }

def get_monthly_count(model, user_type, user, month_ago):
    """Conta registros do último mês"""
    try:
        now = datetime.now()
        target_month = now.month - month_ago
        target_year = now.year
        
        if target_month <= 0:
            target_month += 12
            target_year -= 1
        
        month_start = datetime(target_year, target_month, 1)
        month_end = datetime(target_year, target_month, calendar.monthrange(target_year, target_month)[1])
        
        if user_type == 'medico':
            medico = db.session.query(Medico).filter_by(nome=user['nome']).first()
            if medico:
                return db.session.query(func.count(model.id)).filter(
                    model.id_medico == medico.id,
                    model.data_criacao >= month_start,
                    model.data_criacao <= month_end
                ).scalar() or 0
        else:
            return db.session.query(func.count(model.id)).filter(
                model.data_criacao >= month_start,
                model.data_criacao <= month_end
            ).scalar() or 0
        
        return 0
    except Exception as e:
        logger.error(f"Erro ao contar registros mensais: {e}")
        return 0

def get_recent_activities(user_type, user):
    """Busca atividades recentes do usuário"""
    try:
        activities = []
        
        if user_type == 'medico':
            medico = db.session.query(Medico).filter_by(nome=user['nome']).first()
            if medico:
                # Receitas recentes
                receitas = db.session.query(Receita).filter_by(id_medico=medico.id)\
                    .order_by(Receita.data_criacao.desc()).limit(5).all()
                
                for receita in receitas:
                    activities.append({
                        'tipo': 'Receita',
                        'descricao': f'Receita para {receita.nome_paciente}',
                        'data': receita.data_criacao.strftime('%d/%m/%Y %H:%M') if receita.data_criacao else receita.data,
                        'icon': 'fa-prescription-bottle-alt'
                    })
                
                # Exames recentes
                exames = db.session.query(ExameLab).filter_by(id_medico=medico.id)\
                    .order_by(ExameLab.created_at.desc()).limit(3).all()
                
                for exame in exames:
                    activities.append({
                        'tipo': 'Exame Lab',
                        'descricao': f'Exame para {exame.nome_paciente}',
                        'data': exame.created_at.strftime('%d/%m/%Y %H:%M') if hasattr(exame, 'created_at') and exame.created_at else exame.data,
                        'icon': 'fa-flask'
                    })
        
        # Ordenar por data (mais recentes primeiro)
        activities.sort(key=lambda x: x['data'], reverse=True)
        return activities[:10]
        
    except Exception as e:
        logger.error(f"Erro ao buscar atividades: {e}")
        return []

def get_chart_data(user_type, user):
    """Dados para gráficos do dashboard"""
    try:
        chart_data = {
            'labels': [],
            'receitas': [],
            'exames': []
        }
        
        # Últimos 6 meses
        for i in range(5, -1, -1):
            now = datetime.now()
            month = now.month - i
            year = now.year
            
            if month <= 0:
                month += 12
                year -= 1
            
            month_name = calendar.month_name[month][:3]  # Jan, Feb, etc
            chart_data['labels'].append(month_name)
            
            # Contar receitas do mês
            receitas_count = get_monthly_count(Receita, user_type, user, i)
            chart_data['receitas'].append(receitas_count)
            
            # Contar exames do mês (lab + img)
            exames_lab_count = get_monthly_count(ExameLab, user_type, user, i)
            exames_img_count = get_monthly_count(ExameImg, user_type, user, i)
            chart_data['exames'].append(exames_lab_count + exames_img_count)
        
        return chart_data
        
    except Exception as e:
        logger.error(f"Erro ao gerar dados do gráfico: {e}")
        return {'labels': [], 'receitas': [], 'exames': []}