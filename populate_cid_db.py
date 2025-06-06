#!/usr/bin/env python3
"""
Script para popular o banco de dados CID-10 com códigos médicos comuns
"""

from app import app, db
from models import Cid10
import logging

def populate_cid10_database():
    """Populate CID-10 database with common medical conditions"""
    try:
        with app.app_context():
            # Check if already populated
            if Cid10.query.count() > 0:
                logging.info("CID-10 database already populated")
                return True
            
            # Common CID-10 codes for medical practice
            cid_codes = [
                # Cardiovascular diseases
                {"codigo": "I10.0", "descricao": "Hipertensão arterial", "categoria": "Doenças cardiovasculares"},
                {"codigo": "I25.0", "descricao": "Aterosclerose coronariana", "categoria": "Doenças cardiovasculares"},
                {"codigo": "I48.0", "descricao": "Fibrilação atrial", "categoria": "Doenças cardiovasculares"},
                {"codigo": "I50.0", "descricao": "Insuficiência cardíaca", "categoria": "Doenças cardiovasculares"},
                
                # Endocrine diseases
                {"codigo": "E11.9", "descricao": "Diabetes mellitus tipo 2", "categoria": "Doenças endócrinas"},
                {"codigo": "E10.9", "descricao": "Diabetes mellitus tipo 1", "categoria": "Doenças endócrinas"},
                {"codigo": "E03.9", "descricao": "Hipotireoidismo", "categoria": "Doenças endócrinas"},
                {"codigo": "E05.9", "descricao": "Hipertireoidismo", "categoria": "Doenças endócrinas"},
                {"codigo": "E78.0", "descricao": "Hipercolesterolemia", "categoria": "Doenças endócrinas"},
                
                # Respiratory diseases
                {"codigo": "J44.1", "descricao": "DPOC com exacerbação aguda", "categoria": "Doenças respiratórias"},
                {"codigo": "J45.9", "descricao": "Asma", "categoria": "Doenças respiratórias"},
                {"codigo": "J18.9", "descricao": "Pneumonia", "categoria": "Doenças respiratórias"},
                
                # Musculoskeletal diseases
                {"codigo": "M79.3", "descricao": "Fibromialgia", "categoria": "Doenças musculoesqueléticas"},
                {"codigo": "M25.5", "descricao": "Dor articular", "categoria": "Doenças musculoesqueléticas"},
                
                # Mental health
                {"codigo": "F32.9", "descricao": "Episódio depressivo", "categoria": "Transtornos mentais"},
                {"codigo": "F41.1", "descricao": "Transtorno de ansiedade generalizada", "categoria": "Transtornos mentais"},
                
                # General symptoms
                {"codigo": "R06.0", "descricao": "Dispneia", "categoria": "Sintomas gerais"},
                {"codigo": "R51.0", "descricao": "Cefaleia", "categoria": "Sintomas gerais"},
                {"codigo": "R10.4", "descricao": "Dor abdominal", "categoria": "Sintomas gerais"},
                {"codigo": "R50.9", "descricao": "Febre", "categoria": "Sintomas gerais"},
                
                # Digestive diseases
                {"codigo": "K21.9", "descricao": "Doença do refluxo gastroesofágico", "categoria": "Doenças digestivas"},
                {"codigo": "K59.0", "descricao": "Constipação", "categoria": "Doenças digestivas"},
                
                # Neurological diseases
                {"codigo": "G43.9", "descricao": "Enxaqueca", "categoria": "Doenças neurológicas"},
                {"codigo": "G25.3", "descricao": "Mioclonia", "categoria": "Doenças neurológicas"},
                
                # Infections
                {"codigo": "A09.0", "descricao": "Gastroenterite infecciosa", "categoria": "Doenças infecciosas"},
                {"codigo": "B34.9", "descricao": "Infecção viral", "categoria": "Doenças infecciosas"},
            ]
            
            # Insert CID codes
            for cid_data in cid_codes:
                cid = Cid10(
                    codigo=cid_data["codigo"],
                    descricao=cid_data["descricao"],
                    categoria=cid_data["categoria"]
                )
                db.session.add(cid)
            
            db.session.commit()
            logging.info(f"Successfully populated CID-10 database with {len(cid_codes)} codes")
            print(f"✓ Banco CID-10 populado com {len(cid_codes)} códigos")
            return True
            
    except Exception as e:
        logging.error(f'Error populating CID-10 database: {e}')
        print(f"✗ Erro ao popular banco CID-10: {e}")
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    populate_cid10_database()