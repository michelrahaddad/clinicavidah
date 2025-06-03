from flask import Blueprint, render_template, session, redirect, url_for
from utils.db import get_dashboard_stats
import logging

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Display main dashboard"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        stats = get_dashboard_stats()
        user_name = session['usuario'] if isinstance(session['usuario'], str) else session['usuario']['nome']
        
        logging.info(f'Dashboard accessed by: {user_name}')
        
        return render_template('dashboard.html', 
                             usuario=session['usuario'],
                             **stats)
    except Exception as e:
        logging.error(f'Dashboard error: {e}')
        return redirect(url_for('auth.login'))
