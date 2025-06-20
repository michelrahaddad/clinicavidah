import logging
from datetime import datetime
from models import Medico, Paciente, Receita, ExameLab, ExameImg, Agendamento, Prontuario
from app import db
from werkzeug.security import generate_password_hash
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Get PostgreSQL database connection"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return conn

def insert_patient_if_not_exists(nome_paciente, cpf=None, email=None, telefone=None):
    """Insert patient if not exists and return patient ID"""
    # Normalize the name for comparison
    nome_normalizado = nome_paciente.strip().title()
    
    # Check for existing patient by name (case-insensitive) or CPF
    paciente = None
    if cpf:
        # First check by CPF if provided
        paciente = Paciente.query.filter_by(cpf=cpf).first()
    
    if not paciente:
        # Check by normalized name
        paciente = db.session.query(Paciente).filter(
            db.func.lower(db.func.trim(Paciente.nome)) == nome_normalizado.lower()
        ).first()
    
    if not paciente:
        # Create new patient with required fields
        paciente = Paciente()
        paciente.nome = nome_normalizado
        paciente.cpf = cpf or "000.000.000-00"  # Default CPF if not provided
        paciente.idade = 0  # Default age
        paciente.endereco = "Não informado"  # Default address
        paciente.cidade_uf = "Não informado/XX"  # Default city/state
        paciente.email = email
        paciente.telefone = telefone
        
        db.session.add(paciente)
        db.session.flush()
    return paciente.id

def get_dashboard_stats(medico_id=None):
    """Get dashboard statistics for specific doctor or all doctors"""
    try:
        from flask import session
        
        # If no medico_id provided, get from session
        if not medico_id and 'usuario' in session:
            usuario_data = session['usuario']
            if isinstance(usuario_data, dict):
                medico_id = usuario_data.get('id')
            else:
                medico_id = None
        
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
        
        # Get detailed statistics
        detailed_stats = get_detailed_statistics(medico_id)
        
        return {
            'total_pacientes': total_pacientes,
            'total_receitas': total_receitas,
            'total_exames_lab': total_exames_lab,
            'total_exames_img': total_exames_img,
            'total_geral_pacientes': total_geral_pacientes,
            'total_geral_receitas': total_geral_receitas,
            'total_geral_exames_lab': total_geral_exames_lab,
            'total_geral_exames_img': total_geral_exames_img,
            'monthly_evolution': monthly_data,
            'detailed_stats': detailed_stats
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
            'monthly_evolution': {'months': [], 'receitas': [], 'exames_lab': [], 'exames_img': []},
            'detailed_stats': {'medicamentos': [], 'exames_lab': [], 'exames_img': []}
        }

def get_detailed_statistics(medico_id=None):
    """Get detailed statistics by medication, lab exams, and imaging exams"""
    try:
        from models import Receita, ExameLab, ExameImg
        from sqlalchemy import func, text
        
        # Analyze medications from prescriptions
        medicamentos_stats = []
        exames_lab_stats = []
        exames_img_stats = []
        
        # Get medication frequency (for specific doctor or all doctors)
        if medico_id:
            receitas = db.session.query(Receita).filter(Receita.id_medico == medico_id).all()
        else:
            # Admin access - get all prescriptions
            receitas = db.session.query(Receita).all()
        
        # Count medications
        medicamentos_count = {}
        for receita in receitas:
            try:
                medicamentos_list = receita.medicamentos.split('\n')
                for med in medicamentos_list:
                    med = med.strip()
                    if med and len(med) > 2:
                        # Clean medication name
                        med_clean = med.split('(')[0].strip()
                        if med_clean:
                            medicamentos_count[med_clean] = medicamentos_count.get(med_clean, 0) + 1
            except:
                continue
        
        # Get top 10 medications
        medicamentos_sorted = sorted(medicamentos_count.items(), key=lambda x: x[1], reverse=True)[:10]
        medicamentos_stats = [{'nome': med[0], 'quantidade': med[1]} for med in medicamentos_sorted]
        
        # Get lab exams frequency (for specific doctor or all doctors)
        if medico_id:
            exames_lab = db.session.query(ExameLab).filter(ExameLab.id_medico == medico_id).all()
        else:
            # Admin access - get all lab exams
            exames_lab = db.session.query(ExameLab).all()
        
        exames_lab_count = {}
        for exame in exames_lab:
            try:
                exames_list = exame.exames.split('\n')
                for exam in exames_list:
                    exam = exam.strip()
                    if exam and len(exam) > 2:
                        # Clean exam name
                        exam_clean = exam.split('(')[0].strip()
                        if exam_clean:
                            exames_lab_count[exam_clean] = exames_lab_count.get(exam_clean, 0) + 1
            except:
                continue
        
        # Get top 10 lab exams
        exames_lab_sorted = sorted(exames_lab_count.items(), key=lambda x: x[1], reverse=True)[:10]
        exames_lab_stats = [{'nome': exam[0], 'quantidade': exam[1]} for exam in exames_lab_sorted]
        
        # Get imaging exams frequency (for specific doctor or all doctors)
        if medico_id:
            exames_img = db.session.query(ExameImg).filter(ExameImg.id_medico == medico_id).all()
        else:
            # Admin access - get all imaging exams
            exames_img = db.session.query(ExameImg).all()
        
        exames_img_count = {}
        for exame in exames_img:
            try:
                exames_list = exame.exames.split('\n')
                for exam in exames_list:
                    exam = exam.strip()
                    if exam and len(exam) > 2:
                        # Clean exam name
                        exam_clean = exam.split('(')[0].strip()
                        if exam_clean:
                            exames_img_count[exam_clean] = exames_img_count.get(exam_clean, 0) + 1
            except:
                continue
        
        # Get top 10 imaging exams
        exames_img_sorted = sorted(exames_img_count.items(), key=lambda x: x[1], reverse=True)[:10]
        exames_img_stats = [{'nome': exam[0], 'quantidade': exam[1]} for exam in exames_img_sorted]
        
        return {
            'medicamentos': medicamentos_stats,
            'exames_lab': exames_lab_stats,
            'exames_img': exames_img_stats
        }
        
    except Exception as e:
        logging.error(f'Detailed statistics error: {e}')
        try:
            db.session.rollback()
        except:
            pass
        return {
            'medicamentos': [],
            'exames_lab': [],
            'exames_img': []
        }

def get_monthly_evolution(medico_id=None):
    """Get monthly evolution data for the last 12 months"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, extract
        from models import Receita, ExameLab, ExameImg
        
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
        try:
            db.session.rollback()
        except:
            pass
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
