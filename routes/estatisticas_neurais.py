from flask import Blueprint, render_template, session, redirect, url_for
from utils.db import get_dashboard_stats
import logging

estatisticas_neurais_bp = Blueprint('estatisticas_neurais', __name__)

@estatisticas_neurais_bp.route('/estatisticas_neurais')
def estatisticas_neurais():
    """Display detailed neural statistics page"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        medico_id = session['usuario']['id']
        medico_nome = session['usuario']['nome']
        
        # Get comprehensive statistics
        stats = get_dashboard_stats(medico_id)
        
        logging.info(f'Neural statistics accessed by: {medico_nome}')
        
        return render_template('estatisticas_neurais.html', 
                             medico_nome=medico_nome,
                             **stats)
                             
    except Exception as e:
        logging.error(f'Neural statistics error: {e}')
        return redirect(url_for('dashboard.dashboard'))