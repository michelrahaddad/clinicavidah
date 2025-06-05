from flask import Blueprint, render_template, redirect, url_for, session, flash
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