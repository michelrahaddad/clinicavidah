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

def insert_patient_if_not_exists(nome_paciente):
    """Insert patient if not exists and return patient ID"""
    paciente = Paciente.query.filter_by(nome=nome_paciente).first()
    if not paciente:
        paciente = Paciente(nome=nome_paciente)
        db.session.add(paciente)
        db.session.flush()
    return paciente.id

def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_pacientes = Paciente.query.count()
        total_receitas = Receita.query.count()
        total_exames_lab = ExameLab.query.count()
        total_exames_img = ExameImg.query.count()
        total_agendamentos = Agendamento.query.count()
        
        return {
            'total_pacientes': total_pacientes,
            'total_receitas': total_receitas,
            'total_exames_lab': total_exames_lab,
            'total_exames_img': total_exames_img,
            'total_agendamentos': total_agendamentos
        }
    except Exception as e:
        logging.error(f'Dashboard stats error: {e}')
        return {
            'total_pacientes': 0,
            'total_receitas': 0,
            'total_exames_lab': 0,
            'total_exames_img': 0,
            'total_agendamentos': 0
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
