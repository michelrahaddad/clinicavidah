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
        # Handle both admin and doctor sessions
        if 'admin_data' in session:
            # Admin access
            medico_nome = session['admin_data']['nome']
            medico_id = None  # Admin sees all stats
        elif 'usuario' in session:
            # Doctor access
            usuario_data = session['usuario']
            if isinstance(usuario_data, dict):
                medico_id = usuario_data.get('id')
                medico_nome = usuario_data.get('nome')
            else:
                # Handle string session data
                medico_nome = str(usuario_data)
                medico_id = None
        else:
            return redirect(url_for('auth.login'))
        
        # Get comprehensive statistics
        stats = get_dashboard_stats(medico_id)
        
        logging.info(f'Neural statistics accessed by: {medico_nome}')
        
        return render_template('estatisticas_neurais.html', 
                             medico_nome=medico_nome,
                             **stats)
                             
    except Exception as e:
        logging.error(f'Neural statistics error: {e}')
        return redirect(url_for('dashboard.dashboard'))