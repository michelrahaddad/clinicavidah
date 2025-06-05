from flask import Blueprint, render_template, session, redirect, url_for
from utils.db import get_dashboard_stats
import logging

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Display main dashboard - restored to 11:00 AM working state"""
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Faça login para acessar o sistema.', 'error')
        return redirect(url_for('auth.login'))
    
    # Get user type to determine which dashboard to show
    user_type = session.get('user_type', 'admin')
    is_admin = session.get('is_admin', False)
    
    if is_admin or user_type == 'admin':
        # Admin dashboard with full system statistics
        try:
            stats = get_dashboard_stats()
            return render_template('dashboard_admin.html', 
                                 stats=stats,
                                 user_name=session.get('user_name', 'Administrador'))
        except Exception as e:
            logging.error(f"Error loading admin dashboard: {e}")
            # Fallback stats for admin
            stats = {
                'total_receitas': 0,
                'total_exames_lab': 0,
                'total_exames_img': 0,
                'total_pacientes': 0,
                'total_medicos': 0,
                'receitas_hoje': 0,
                'exames_hoje': 0
            }
            return render_template('dashboard_admin.html', 
                                 stats=stats,
                                 user_name=session.get('user_name', 'Administrador'))
    else:
        # Doctor dashboard with limited view
        try:
            # Get stats specific to this doctor
            medico_id = session.get('user_id')
            stats = {
                'total_receitas': 0,
                'total_exames_lab': 0, 
                'total_exames_img': 0,
                'receitas_hoje': 0,
                'exames_hoje': 0
            }
            return render_template('dashboard_medico.html',
                                 stats=stats,
                                 user_name=session.get('user_name', 'Médico'),
                                 user_crm=session.get('user_crm', ''))
        except Exception as e:
            logging.error(f"Error loading doctor dashboard: {e}")
            stats = {
                'total_receitas': 0,
                'total_exames_lab': 0,
                'total_exames_img': 0,
                'receitas_hoje': 0,
                'exames_hoje': 0
            }
            return render_template('dashboard_medico.html',
                                 stats=stats,
                                 user_name=session.get('user_name', 'Médico'),
                                 user_crm=session.get('user_crm', ''))
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
        
        return render_template('dashboard.html', 
                             usuario=usuario_data or admin_data,
                             **stats)
    except Exception as e:
        logging.error(f'Dashboard error: {e}')
        return redirect(url_for('auth.login'))
