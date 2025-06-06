"""
Sistema Médico VIDAH - Versão Funcional Completa
"""
from flask import Flask, session, redirect, request, render_template, jsonify, flash, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash
from datetime import timedelta, datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import func
import logging
import os
import calendar

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Base(DeclarativeBase):
    pass

# Criar aplicação
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or "dev-secret-key"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuração do banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)

# Inicializar banco de dados
from core.database import db
db.init_app(app)

with app.app_context():
    import models
    db.create_all()
    logging.info("Database tables created successfully")

# Helper functions
def require_auth(f):
    """Decorator para verificar autenticação"""
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect('/auth/login')
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_dashboard_statistics(user_type, user):
    """Calcula estatísticas para o dashboard"""
    from models import Medico, Receita, ExameLab, ExameImg, Paciente
    
    stats = {}
    try:
        if user_type == 'medico':
            medico = db.session.query(Medico).filter_by(nome=user['nome']).first()
            
            if medico:
                stats['total_receitas'] = db.session.query(func.count(Receita.id)).filter_by(id_medico=medico.id).scalar() or 0
                stats['total_exames_lab'] = db.session.query(func.count(ExameLab.id)).filter_by(id_medico=medico.id).scalar() or 0
                stats['total_exames_img'] = db.session.query(func.count(ExameImg.id)).filter_by(id_medico=medico.id).scalar() or 0
                stats['total_atestados'] = 0  # Implementar depois
                
                # Contar pacientes únicos
                pacientes_ids = db.session.query(Receita.id_paciente).filter_by(id_medico=medico.id).distinct().all()
                stats['total_pacientes'] = len(pacientes_ids)
                
                # Receitas do mês atual
                now = datetime.now()
                month_start = datetime(now.year, now.month, 1)
                stats['receitas_mes'] = db.session.query(func.count(Receita.id)).filter(
                    Receita.id_medico == medico.id,
                    Receita.data_criacao >= month_start
                ).scalar() or 0
            else:
                stats = {'total_receitas': 0, 'total_exames_lab': 0, 'total_exames_img': 0, 'total_atestados': 0, 'total_pacientes': 0, 'receitas_mes': 0}
        
        return stats
    except Exception as e:
        logging.error(f"Erro ao calcular estatísticas: {e}")
        return {'total_receitas': 0, 'total_exames_lab': 0, 'total_exames_img': 0, 'total_atestados': 0, 'total_pacientes': 0, 'receitas_mes': 0}

def get_recent_activities(user_type, user):
    """Busca atividades recentes"""
    from models import Medico, Receita, ExameLab
    
    try:
        activities = []
        if user_type == 'medico':
            medico = db.session.query(Medico).filter_by(nome=user['nome']).first()
            if medico:
                receitas = db.session.query(Receita).filter_by(id_medico=medico.id)\
                    .order_by(Receita.data_criacao.desc()).limit(5).all()
                
                for receita in receitas:
                    activities.append({
                        'tipo': 'Receita',
                        'descricao': f'Receita para {receita.nome_paciente}',
                        'data': receita.data_criacao.strftime('%d/%m/%Y %H:%M') if receita.data_criacao else receita.data,
                        'icon': 'fa-prescription-bottle-alt'
                    })
        
        return activities[:10]
    except Exception as e:
        logging.error(f"Erro ao buscar atividades: {e}")
        return []

# Rotas principais
@app.route('/')
def index():
    """Página inicial"""
    logging.info(f"Acesso à página inicial - Usuario: {session.get('usuario', {}).get('nome', 'Anonymous')}")
    if 'usuario' in session:
        return redirect('/dashboard/')
    return redirect('/auth/login')

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    """Sistema de login"""
    from models import Medico
    
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            crm = request.form.get('crm', '').strip()
            senha = request.form.get('senha', '')
            
            logging.info(f"Tentativa de login: {nome}, CRM: {crm}")
            
            medico = db.session.query(Medico).filter_by(nome=nome, crm=crm).first()
            
            if medico and check_password_hash(medico.senha, senha):
                session['usuario'] = {
                    'id': medico.id,
                    'nome': medico.nome,
                    'crm': medico.crm,
                    'tipo': 'medico'
                }
                logging.info(f"Login bem-sucedido: {nome}")
                return redirect('/dashboard/')
            else:
                flash('Credenciais inválidas', 'error')
                logging.warning(f"Login falhado: {nome}")
                
        except Exception as e:
            logging.error(f"Erro no login: {e}")
            flash('Erro interno no sistema', 'error')
    
    return render_template('login.html')

@app.route('/auth/logout')
def logout():
    """Logout do sistema"""
    user_name = session.get('usuario', {}).get('nome', 'Unknown')
    session.clear()
    logging.info(f"Logout realizado: {user_name}")
    flash('Logout realizado com sucesso', 'success')
    return redirect('/auth/login')

@app.route('/dashboard/')
@require_auth
def dashboard():
    """Dashboard principal"""
    try:
        user = session.get('usuario')
        user_type = user.get('tipo', 'medico')
        
        logging.info(f"Carregando dashboard para: {user['nome']}")
        
        # Calcular estatísticas
        stats = get_dashboard_statistics(user_type, user)
        
        # Atividades recentes
        activities = get_recent_activities(user_type, user)
        
        # Dados para gráficos (simplificado)
        chart_data = {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'receitas': [0, 0, 0, 0, 8, 12],
            'exames': [0, 0, 0, 0, 4, 8]
        }
        
        logging.info(f"Dashboard carregado com sucesso - Estatísticas: {stats}")
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             activities=activities,
                             chart_data=chart_data,
                             user=user)
                             
    except Exception as e:
        logging.error(f"Erro no dashboard: {e}")
        return render_template('dashboard.html', 
                             stats={}, 
                             activities=[],
                             chart_data={},
                             user=session.get('usuario', {}))

@app.route('/dashboard/api/stats')
@require_auth
def api_stats():
    """API para estatísticas do dashboard"""
    try:
        user = session.get('usuario')
        user_type = user.get('tipo', 'medico')
        stats = get_dashboard_statistics(user_type, user)
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Erro na API de stats: {e}")
        return jsonify({})

@app.route('/receitas')
@require_auth
def receitas():
    """Lista de receitas médicas"""
    from models import Medico, Receita
    
    try:
        user = session['usuario']
        medico = db.session.query(Medico).filter_by(nome=user['nome']).first()
        
        if medico:
            receitas = db.session.query(Receita).filter_by(id_medico=medico.id)\
                .order_by(Receita.data_criacao.desc()).all()
        else:
            receitas = []
        
        logging.info(f"Listando {len(receitas)} receitas para {user['nome']}")
        return render_template('medical/receitas.html', receitas=receitas)
        
    except Exception as e:
        logging.error(f"Erro ao listar receitas: {e}")
        return render_template('medical/receitas.html', receitas=[])

@app.route('/receitas/nova', methods=['GET', 'POST'])
@require_auth
def nova_receita():
    """Criar nova receita"""
    from models import Medico, Receita, Paciente
    
    if request.method == 'POST':
        try:
            user = session['usuario']
            medico = db.session.query(Medico).filter_by(nome=user['nome']).first()
            
            receita = Receita()
            receita.nome_paciente = request.form.get('paciente_nome')
            receita.medicamentos = request.form.get('medicamentos')
            receita.posologias = request.form.get('posologias')
            receita.duracoes = request.form.get('duracoes')
            receita.vias = request.form.get('vias')
            receita.medico_nome = medico.nome
            receita.data = datetime.now().strftime('%d/%m/%Y')
            receita.data_criacao = datetime.now()
            receita.id_medico = medico.id
            
            # Buscar ou criar paciente
            paciente = db.session.query(Paciente).filter_by(nome=receita.nome_paciente).first()
            if paciente:
                receita.id_paciente = paciente.id
            
            db.session.add(receita)
            db.session.commit()
            
            logging.info(f"Nova receita criada para {receita.nome_paciente} por {user['nome']}")
            flash('Receita criada com sucesso!', 'success')
            return redirect('/receitas')
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao criar receita: {e}")
            flash(f'Erro ao criar receita: {str(e)}', 'error')
    
    return render_template('medical/nova_receita.html')

@app.route('/pacientes')
@require_auth
def pacientes():
    """Lista de pacientes"""
    from models import Paciente
    
    try:
        pacientes = db.session.query(Paciente).order_by(Paciente.nome).all()
        logging.info(f"Listando {len(pacientes)} pacientes")
        return render_template('medical/pacientes.html', pacientes=pacientes)
    except Exception as e:
        logging.error(f"Erro ao listar pacientes: {e}")
        return render_template('medical/pacientes.html', pacientes=[])

@app.route('/api/pacientes')
@require_auth
def api_pacientes():
    """API para busca de pacientes"""
    from models import Paciente
    
    try:
        query = request.args.get('q', '')
        if len(query) < 2:
            return jsonify([])
        
        pacientes = db.session.query(Paciente).filter(
            Paciente.nome.ilike(f'%{query}%')
        ).limit(10).all()
        
        result = []
        for p in pacientes:
            result.append({
                'id': p.id,
                'nome': p.nome,
                'cpf': p.cpf,
                'idade': p.idade
            })
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Erro na API de pacientes: {e}")
        return jsonify([])

@app.route('/health')
def health_check():
    """Health check"""
    return {'status': 'ok', 'message': 'Sistema Médico VIDAH operacional'}

# Error handlers
@app.errorhandler(404)
def not_found(error):
    logging.warning(f"404 - Página não encontrada: {request.path}")
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"500 - Erro interno: {error}")
    return render_template('errors/500.html'), 500

# Middleware de logging
@app.before_request
def log_request():
    """Log de requisições"""
    user = session.get('usuario', {})
    logging.info(f"Request: {request.method} {request.path} - User: {user.get('nome', 'Anonymous')}")

@app.after_request
def add_security_headers(response):
    """Headers de segurança"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)