from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from models import db, Receita, Paciente, ExameLab
from datetime import datetime, timedelta
import logging

estatisticas_bp = Blueprint('estatisticas', __name__)

@estatisticas_bp.route('/estatisticas')
def estatisticas():
    """Página de estatísticas neurais"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Dados para estatísticas
        total_pacientes = Paciente.query.count()
        total_receitas = Receita.query.count()
        total_exames = ExameLab.query.count()
        
        # Estatísticas dos últimos 30 dias
        data_limite = datetime.now() - timedelta(days=30)
        receitas_mes = Receita.query.filter(Receita.data_criacao >= data_limite).count()
        
        stats = {
            'total_pacientes': total_pacientes,
            'total_receitas': total_receitas,
            'total_exames': total_exames,
            'receitas_mes': receitas_mes
        }
        
        return render_template('estatisticas.html', stats=stats)
        
    except Exception as e:
        logging.error(f'Erro ao carregar estatísticas: {e}')
        return render_template('estatisticas.html', stats={})

@estatisticas_bp.route('/api/estatisticas')
def api_estatisticas():
    """API para dados de estatísticas"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return jsonify({})
    
    try:
        total_pacientes = Paciente.query.count()
        total_receitas = Receita.query.count()
        
        return jsonify({
            'pacientes': total_pacientes,
            'receitas': total_receitas,
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e)})
