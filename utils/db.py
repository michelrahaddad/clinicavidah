import sqlite3
import logging
from datetime import datetime
from models import Medico, Paciente, Receita, ExameLab, ExameImg, Agendamento, Prontuario
from app import db
from werkzeug.security import generate_password_hash
import os

def get_db_connection():
    """Get database connection for legacy compatibility"""
    # This is for backward compatibility with uploaded files
    # Modern code should use SQLAlchemy models directly
    conn = sqlite3.connect('vidah_medical.db')
    conn.row_factory = sqlite3.Row
    return conn

def insert_patient_if_not_exists(nome_paciente, email=None, telefone=None):
    """Insert patient if not exists and return patient ID"""
    paciente = Paciente.query.filter_by(nome=nome_paciente).first()
    if not paciente:
        paciente = Paciente(
            nome=nome_paciente,
            email=email,
            telefone=telefone
        )
        db.session.add(paciente)
        db.session.flush()
    return paciente.id

def get_dashboard_stats(medico_id=None):
    """Get dashboard statistics for specific doctor or all doctors"""
    try:
        from flask import session
        
        # If no medico_id provided, get from session
        if not medico_id and 'usuario' in session:
            medico_id = session['usuario']['id']
        
        if medico_id:
            # Statistics for specific doctor
            total_pacientes = db.session.query(Paciente.id).join(
                Receita, Paciente.id == Receita.id_paciente
            ).filter(Receita.id_medico == medico_id).distinct().count()
            
            total_receitas = Receita.query.filter_by(id_medico=medico_id).count()
            total_exames_lab = ExameLab.query.filter_by(id_medico=medico_id).count()
            total_exames_img = ExameImg.query.filter_by(id_medico=medico_id).count()
            
            # Get total statistics (all doctors combined)
            total_geral_pacientes = Paciente.query.count()
            total_geral_receitas = Receita.query.count()
            total_geral_exames_lab = ExameLab.query.count()
            total_geral_exames_img = ExameImg.query.count()
        else:
            # Fallback to general statistics
            total_pacientes = Paciente.query.count()
            total_receitas = Receita.query.count()
            total_exames_lab = ExameLab.query.count()
            total_exames_img = ExameImg.query.count()
            
            total_geral_pacientes = total_pacientes
            total_geral_receitas = total_receitas
            total_geral_exames_lab = total_exames_lab
            total_geral_exames_img = total_exames_img
        
        # Get monthly evolution data
        monthly_data = get_monthly_evolution(medico_id)
        
        return {
            'total_pacientes': total_pacientes,
            'total_receitas': total_receitas,
            'total_exames_lab': total_exames_lab,
            'total_exames_img': total_exames_img,
            'total_geral_pacientes': total_geral_pacientes,
            'total_geral_receitas': total_geral_receitas,
            'total_geral_exames_lab': total_geral_exames_lab,
            'total_geral_exames_img': total_geral_exames_img,
            'monthly_evolution': monthly_data
        }
    except Exception as e:
        logging.error(f'Dashboard stats error: {e}')
        return {
            'total_pacientes': 0,
            'total_receitas': 0,
            'total_exames_lab': 0,
            'total_exames_img': 0,
            'total_geral_pacientes': 0,
            'total_geral_receitas': 0,
            'total_geral_exames_lab': 0,
            'total_geral_exames_img': 0,
            'monthly_evolution': {'months': [], 'receitas': [], 'exames_lab': [], 'exames_img': []}
        }

def get_monthly_evolution(medico_id=None):
    """Get monthly evolution data for the last 12 months"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, extract
        
        # Get last 12 months
        current_date = datetime.now()
        months_data = []
        receitas_data = []
        exames_lab_data = []
        exames_img_data = []
        
        for i in range(11, -1, -1):
            # Calculate the month
            month_date = current_date - timedelta(days=30 * i)
            month_year = month_date.strftime('%Y-%m')
            month_name = month_date.strftime('%b/%y')
            months_data.append(month_name)
            
            # Query data for this month
            if medico_id:
                # Receitas count for this month
                receitas_count = db.session.query(func.count(Receita.id)).filter(
                    Receita.id_medico == medico_id,
                    extract('year', func.to_date(Receita.data, 'YYYY-MM-DD')) == month_date.year,
                    extract('month', func.to_date(Receita.data, 'YYYY-MM-DD')) == month_date.month
                ).scalar() or 0
                
                # Exames Lab count for this month
                exames_lab_count = db.session.query(func.count(ExameLab.id)).filter(
                    ExameLab.id_medico == medico_id,
                    extract('year', func.to_date(ExameLab.data, 'YYYY-MM-DD')) == month_date.year,
                    extract('month', func.to_date(ExameLab.data, 'YYYY-MM-DD')) == month_date.month
                ).scalar() or 0
                
                # Exames Img count for this month
                exames_img_count = db.session.query(func.count(ExameImg.id)).filter(
                    ExameImg.id_medico == medico_id,
                    extract('year', func.to_date(ExameImg.data, 'YYYY-MM-DD')) == month_date.year,
                    extract('month', func.to_date(ExameImg.data, 'YYYY-MM-DD')) == month_date.month
                ).scalar() or 0
            else:
                # General data for all doctors
                receitas_count = db.session.query(func.count(Receita.id)).filter(
                    extract('year', func.to_date(Receita.data, 'YYYY-MM-DD')) == month_date.year,
                    extract('month', func.to_date(Receita.data, 'YYYY-MM-DD')) == month_date.month
                ).scalar() or 0
                
                exames_lab_count = db.session.query(func.count(ExameLab.id)).filter(
                    extract('year', func.to_date(ExameLab.data, 'YYYY-MM-DD')) == month_date.year,
                    extract('month', func.to_date(ExameLab.data, 'YYYY-MM-DD')) == month_date.month
                ).scalar() or 0
                
                exames_img_count = db.session.query(func.count(ExameImg.id)).filter(
                    extract('year', func.to_date(ExameImg.data, 'YYYY-MM-DD')) == month_date.year,
                    extract('month', func.to_date(ExameImg.data, 'YYYY-MM-DD')) == month_date.month
                ).scalar() or 0
            
            receitas_data.append(receitas_count)
            exames_lab_data.append(exames_lab_count)
            exames_img_data.append(exames_img_count)
        
        return {
            'months': months_data,
            'receitas': receitas_data,
            'exames_lab': exames_lab_data,
            'exames_img': exames_img_data
        }
        
    except Exception as e:
        logging.error(f'Monthly evolution error: {e}')
        return {
            'months': [],
            'receitas': [],
            'exames_lab': [],
            'exames_img': []
        }

def init_database():
    """Initialize database with sample data"""
    try:
        # Check if we already have a doctor
        if Medico.query.count() == 0:
            # Create a default doctor for testing
            senha_hash = generate_password_hash('123456')
            medico = Medico(
                nome='Dr. João Silva',
                crm='123456-SP',
                senha=senha_hash
            )
            db.session.add(medico)
            db.session.commit()
            logging.info('Default doctor created: Dr. João Silva (CRM: 123456-SP, Password: 123456)')
            
    except Exception as e:
        logging.error(f'Database initialization error: {e}')
