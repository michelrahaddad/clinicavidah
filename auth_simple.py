"""
Sistema de autenticação simplificado
"""
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from core.database import db
from models import Medico
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

auth_simple = Blueprint('auth', __name__)

@auth_simple.route('/login', methods=['GET', 'POST'])
def login():
    """Login simplificado"""
    
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST method
    try:
        from core.database import db
        from models import Medico
        
        nome = request.form.get('nome', '').strip()
        crm = request.form.get('crm', '').strip()
        senha = request.form.get('senha', '').strip()
        
        logger.info(f"Tentativa de login - Nome: '{nome}', CRM: '{crm}'")
        
        if not nome or not senha:
            flash('Nome e senha são obrigatórios', 'error')
            return render_template('login.html')
        
        # Buscar médico no banco
        medico = db.session.query(Medico).filter_by(nome=nome, crm=crm).first()
        
        if medico and check_password_hash(medico.senha, senha):
            # Login bem-sucedido
            session['usuario'] = {
                'id': medico.id,
                'nome': medico.nome,
                'crm': medico.crm,
                'tipo': 'medico'
            }
            logger.info(f"Login bem-sucedido para {nome}")
            return redirect(url_for('dashboard.index'))
        else:
            flash('Credenciais inválidas', 'error')
            return render_template('login.html')
            
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        flash('Erro interno do sistema', 'error')
        return render_template('login.html')

@auth_simple.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    return redirect(url_for('auth.login'))