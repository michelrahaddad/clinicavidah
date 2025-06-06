"""
Script de diagnóstico completo do banco de dados
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import db
from models import Medico, Paciente, Receita, ExameLab, ExameImg, AtestadoMedico
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnosticar_banco():
    """Diagnóstica completamente o estado do banco"""
    
    try:
        logger.info("=== DIAGNÓSTICO COMPLETO DO BANCO DE DADOS ===")
        
        # Verificar conexão
        logger.info("1. Testando conexão com banco...")
        result = db.session.execute("SELECT 1").scalar()
        logger.info(f"Conexão OK: {result}")
        
        # Verificar tabelas
        logger.info("2. Verificando estrutura das tabelas...")
        tables = ['medicos', 'pacientes', 'receitas', 'exames_lab', 'exames_img', 'atestados_medicos']
        
        for table in tables:
            try:
                count = db.session.execute(f"SELECT COUNT(*) FROM {table}").scalar()
                logger.info(f"Tabela {table}: {count} registros")
            except Exception as e:
                logger.error(f"Erro na tabela {table}: {e}")
        
        # Verificar dados específicos do Dr. Michel
        logger.info("3. Verificando dados do Dr. Michel...")
        michel = db.session.query(Medico).filter_by(crm='183299-SP').first()
        if michel:
            logger.info(f"Dr. Michel encontrado: ID={michel.id}, Nome={michel.nome}")
            
            # Contar documentos do Dr. Michel
            receitas_count = db.session.query(Receita).filter_by(id_medico=michel.id).count()
            exames_lab_count = db.session.query(ExameLab).filter_by(id_medico=michel.id).count()
            exames_img_count = db.session.query(ExameImg).filter_by(id_medico=michel.id).count()
            
            logger.info(f"Receitas do Dr. Michel: {receitas_count}")
            logger.info(f"Exames Lab do Dr. Michel: {exames_lab_count}")
            logger.info(f"Exames Img do Dr. Michel: {exames_img_count}")
        else:
            logger.error("Dr. Michel NÃO encontrado no banco!")
        
        # Verificar colunas específicas
        logger.info("4. Verificando colunas críticas...")
        try:
            receita_sample = db.session.query(Receita).first()
            if receita_sample:
                logger.info(f"Receita sample - data_criacao: {getattr(receita_sample, 'data_criacao', 'CAMPO NÃO EXISTE')}")
                logger.info(f"Receita sample - id_medico: {receita_sample.id_medico}")
                logger.info(f"Receita sample - nome_paciente: {receita_sample.nome_paciente}")
        except Exception as e:
            logger.error(f"Erro ao verificar receita: {e}")
        
        # Testar queries específicas do dashboard
        logger.info("5. Testando queries do dashboard...")
        try:
            from sqlalchemy import func
            total_receitas = db.session.query(func.count(Receita.id)).scalar()
            logger.info(f"Total receitas (query dashboard): {total_receitas}")
            
            total_pacientes = db.session.query(func.count(Paciente.id)).scalar()
            logger.info(f"Total pacientes (query dashboard): {total_pacientes}")
            
        except Exception as e:
            logger.error(f"Erro nas queries do dashboard: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        logger.info("=== DIAGNÓSTICO CONCLUÍDO ===")
        
    except Exception as e:
        logger.error(f"ERRO CRÍTICO no diagnóstico: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    from app_modular_fixed import app
    with app.app_context():
        diagnosticar_banco()
