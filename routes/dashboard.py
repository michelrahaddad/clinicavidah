from flask import Blueprint, render_template, session, redirect, url_for
from utils.db import get_dashboard_stats
import logging

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Display main dashboard with authentication bypass for testing"""
    # Simplified authentication for testing - allow admin access
    logging.info(f"Dashboard access attempt - session: {dict(session)}")
    
    # Allow access if admin_usuario exists in session
    if 'admin_usuario' in session:
        logging.info(f"Admin dashboard access granted for: {session.get('admin_usuario')}")
    elif 'usuario' in session:
        logging.info(f"User dashboard access granted for: {session.get('usuario')}")
    else:
        logging.warning("No valid session found - redirecting to login")
        return redirect(url_for('auth.login'))
    try:
        # Handle both admin and doctor sessions safely
        usuario_data = session.get('usuario')
        admin_data = session.get('admin_data')
        
        if admin_data:
            # Admin session
            user_name = admin_data.get('nome', 'Admin')
            medico_id = None
        elif usuario_data:
            # Doctor session
            if isinstance(usuario_data, dict):
                user_name = usuario_data.get('nome', 'Unknown')
                medico_id = usuario_data.get('id')
            else:
                # Handle string session data
                user_name = str(usuario_data)
                medico_id = None
        else:
            return redirect(url_for('auth.login'))
        
        stats = get_dashboard_stats(medico_id)
        
        logging.info(f'Dashboard accessed by: {user_name}')
        
        return render_template('dashboard_simple.html', 
                             usuario=usuario_data or admin_data,
                             **stats)
    except Exception as e:
        logging.error(f'Dashboard error: {e}')
        return redirect(url_for('auth.login'))
