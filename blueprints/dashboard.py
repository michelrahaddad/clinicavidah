"""
Blueprint do Dashboard - Sistema Médico VIDAH
Painel principal com estatísticas e acesso rápido
"""
from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from functools import wraps

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
        logger.error(f"Dashboard error for {user}: {str(e)}")
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
    
    try:
        # Data de hoje e última semana
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        if user_type == 'admin':
            # Estatísticas administrativas
            stats['total_receitas'] = db.session.query(func.count(Receita.id)).scalar() or 0
            stats['total_exames_lab'] = db.session.query(func.count(ExamesLab.id)).scalar() or 0
            stats['total_exames_img'] = db.session.query(func.count(ExamesImg.id)).scalar() or 0
            stats['total_atestados'] = db.session.query(func.count(Atestado.id)).scalar() or 0
            stats['total_pacientes'] = db.session.query(func.count(Paciente.id)).scalar() or 0
            stats['total_medicos'] = db.session.query(func.count(Medico.id)).scalar() or 0
            
            # Atividades da semana
            stats['receitas_semana'] = db.session.query(func.count(Receita.id)).filter(
                func.date(Receita.data_criacao) >= week_ago
            ).scalar() or 0
            
            stats['exames_semana'] = (
                db.session.query(func.count(ExamesLab.id)).filter(
                    func.date(ExamesLab.data_criacao) >= week_ago
                ).scalar() or 0
            ) + (
                db.session.query(func.count(ExamesImg.id)).filter(
                    func.date(ExamesImg.data_criacao) >= week_ago
                ).scalar() or 0
            )
            
        else:
            # Estatísticas do médico
            medico = db.session.query(Medico).filter_by(nome=user).first()
            if medico:
                stats['total_receitas'] = db.session.query(func.count(Receita.id)).filter_by(medico=user).scalar() or 0
                stats['total_exames_lab'] = db.session.query(func.count(ExamesLab.id)).filter_by(medico=user).scalar() or 0
                stats['total_exames_img'] = db.session.query(func.count(ExamesImg.id)).filter_by(medico=user).scalar() or 0
                stats['total_atestados'] = db.session.query(func.count(Atestado.id)).filter_by(medico=user).scalar() or 0
                
                # Pacientes únicos atendidos
                stats['total_pacientes'] = db.session.query(func.count(func.distinct(Receita.nome_paciente))).filter_by(medico=user).scalar() or 0
                
                # Atividades da semana
                stats['receitas_semana'] = db.session.query(func.count(Receita.id)).filter(
                    Receita.medico == user,
                    func.date(Receita.data_criacao) >= week_ago
                ).scalar() or 0
                
                stats['exames_semana'] = (
                    db.session.query(func.count(ExamesLab.id)).filter(
                        ExamesLab.medico == user,
                        func.date(ExamesLab.data_criacao) >= week_ago
                    ).scalar() or 0
                ) + (
                    db.session.query(func.count(ExamesImg.id)).filter(
                        ExamesImg.medico == user,
                        func.date(ExamesImg.data_criacao) >= week_ago
                    ).scalar() or 0
                )
        
        # Calcular tendências
        stats['receitas_mes'] = get_monthly_count(Receita, user_type, user, month_ago)
        stats['exames_mes'] = get_monthly_count(ExamesLab, user_type, user, month_ago) + get_monthly_count(ExamesImg, user_type, user, month_ago)
        
    except Exception as e:
        logger.error(f"Error calculating stats: {str(e)}")
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
        # Receitas recentes
        receitas_query = db.session.query(Receita).order_by(desc(Receita.data_criacao)).limit(5)
        if user_type != 'admin':
            receitas_query = receitas_query.filter_by(medico=user)
        
        for receita in receitas_query:
            activities.append({
                'type': 'receita',
                'title': f'Receita para {sanitize_input(receita.nome_paciente)}',
                'description': f'Medicamentos: {len(receita.medicamentos.split(",")) if receita.medicamentos else 0}',
                'date': receita.data_criacao.strftime('%d/%m/%Y %H:%M') if receita.data_criacao else '',
                'icon': 'fas fa-prescription-bottle-alt',
                'color': 'primary'
            })
        
        # Exames recentes
        exames_query = db.session.query(ExamesLab).order_by(desc(ExamesLab.data_criacao)).limit(3)
        if user_type != 'admin':
            exames_query = exames_query.filter_by(medico=user)
        
        for exame in exames_query:
            activities.append({
                'type': 'exame_lab',
                'title': f'Exame laboratorial para {sanitize_input(exame.nome_paciente)}',
                'description': f'Exames: {len(exame.exames_solicitados.split(",")) if exame.exames_solicitados else 0}',
                'date': exame.data_criacao.strftime('%d/%m/%Y %H:%M') if exame.data_criacao else '',
                'icon': 'fas fa-vial',
                'color': 'success'
            })
        
        # Ordenar por data
        activities.sort(key=lambda x: x['date'], reverse=True)
        
    except Exception as e:
        logger.error(f"Error getting activities: {str(e)}")
    
    return activities[:10]  # Limitar a 10 atividades


def get_chart_data(user_type, user):
    """Dados para gráficos do dashboard"""
    chart_data = {}
    
    try:
        # Dados dos últimos 7 dias
        days = []
        receitas_data = []
        exames_data = []
        
        for i in range(6, -1, -1):
            day = datetime.now().date() - timedelta(days=i)
            days.append(day.strftime('%d/%m'))
            
            # Contar receitas do dia
            receitas_count = db.session.query(func.count(Receita.id)).filter(
                func.date(Receita.data_criacao) == day
            )
            if user_type != 'admin':
                receitas_count = receitas_count.filter_by(medico=user)
            receitas_data.append(receitas_count.scalar() or 0)
            
            # Contar exames do dia
            exames_count = (
                db.session.query(func.count(ExamesLab.id)).filter(
                    func.date(ExamesLab.data_criacao) == day
                ).scalar() or 0
            ) + (
                db.session.query(func.count(ExamesImg.id)).filter(
                    func.date(ExamesImg.data_criacao) == day
                ).scalar() or 0
            )
            
            if user_type != 'admin':
                exames_count = (
                    db.session.query(func.count(ExamesLab.id)).filter(
                        ExamesLab.medico == user,
                        func.date(ExamesLab.data_criacao) == day
                    ).scalar() or 0
                ) + (
                    db.session.query(func.count(ExamesImg.id)).filter(
                        ExamesImg.medico == user,
                        func.date(ExamesImg.data_criacao) == day
                    ).scalar() or 0
                )
            
            exames_data.append(exames_count)
        
        chart_data = {
            'labels': days,
            'receitas': receitas_data,
            'exames': exames_data
        }
        
    except Exception as e:
        logger.error(f"Error getting chart data: {str(e)}")
        chart_data = {
            'labels': [],
            'receitas': [],
            'exames': []
        }
    
    return chart_data