from main import db
from models import RelatorioMedico, AtestadoMedico, FormularioAltoCusto
import logging

def create_relatorio_medico(data):
    """Create medical report record"""
    try:
        relatorio = RelatorioMedico()
        for key, value in data.items():
            setattr(relatorio, key, value)
        db.session.add(relatorio)
        db.session.commit()
        return relatorio
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error creating medical report: {e}')
        raise

def create_atestado_medico(data):
    """Create medical certificate record"""
    try:
        atestado = AtestadoMedico()
        for key, value in data.items():
            setattr(atestado, key, value)
        db.session.add(atestado)
        db.session.commit()
        return atestado
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error creating medical certificate: {e}')
        raise

def create_formulario_alto_custo(data):
    """Create high-cost form record"""
    try:
        formulario = FormularioAltoCusto()
        for key, value in data.items():
            setattr(formulario, key, value)
        db.session.add(formulario)
        db.session.commit()
        return formulario
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error creating high-cost form: {e}')
        raise