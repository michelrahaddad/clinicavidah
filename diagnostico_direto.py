"""
Diagnóstico direto do banco de dados
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import db
from models import Medico, Paciente, Receita, ExameLab, ExameImg, AtestadoMedico
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnosticar_banco():
    """Diagnóstica completamente o estado do banco"""
    
    try:
        logger.info("=== DIAGNÓSTICO DIRETO DO BANCO ===")
        
        # Verificar conexão
        result = db.session.execute(text("SELECT 1")).scalar()
        logger.info(f"Conexão OK: {result}")
        
        # Contar registros em cada tabela
        tables = {
            'medicos': Medico,
            'pacientes': Paciente, 
            'receitas': Receita,
            'exames_lab': ExameLab,
            'exames_img': ExameImg,
            'atestados_medicos': AtestadoMedico
        }
        
        for table_name, model in tables.items():
            try:
                count = db.session.query(model).count()
                logger.info(f"Tabela {table_name}: {count} registros")
            except Exception as e:
                logger.error(f"Erro na tabela {table_name}: {e}")
        
        # Verificar Dr. Michel especificamente
        michel = db.session.query(Medico).filter_by(crm='183299-SP').first()
        if michel:
            logger.info(f"Dr. Michel encontrado: ID={michel.id}, Nome={michel.nome}")
            
            # Contar documentos do Dr. Michel
            receitas = db.session.query(Receita).filter_by(id_medico=michel.id).count()
            exames_lab = db.session.query(ExameLab).filter_by(id_medico=michel.id).count()
            exames_img = db.session.query(ExameImg).filter_by(id_medico=michel.id).count()
            
            logger.info(f"Receitas do Dr. Michel: {receitas}")
            logger.info(f"Exames Lab do Dr. Michel: {exames_lab}")
            logger.info(f"Exames Img do Dr. Michel: {exames_img}")
            
            # Testar queries do dashboard
            from sqlalchemy import func
            
            total_receitas = db.session.query(func.count(Receita.id)).filter_by(id_medico=michel.id).scalar()
            logger.info(f"Total receitas (func.count): {total_receitas}")
            
            total_pacientes_unicos = db.session.query(Receita.id_paciente).filter_by(id_medico=michel.id).distinct().count()
            logger.info(f"Pacientes únicos: {total_pacientes_unicos}")
            
        else:
            logger.error("Dr. Michel NÃO encontrado!")
        
        # Verificar estrutura das receitas
        receita_sample = db.session.query(Receita).first()
        if receita_sample:
            logger.info(f"Receita sample:")
            logger.info(f"  - ID: {receita_sample.id}")
            logger.info(f"  - Nome paciente: {receita_sample.nome_paciente}")
            logger.info(f"  - ID médico: {receita_sample.id_medico}")
            logger.info(f"  - Data: {receita_sample.data}")
            logger.info(f"  - Data criação: {getattr(receita_sample, 'data_criacao', 'CAMPO NÃO EXISTE')}")
        
        logger.info("=== DIAGNÓSTICO CONCLUÍDO ===")
        
    except Exception as e:
        logger.error(f"ERRO no diagnóstico: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    from app_modular_fixed import app
    with app.app_context():
        diagnosticar_banco()