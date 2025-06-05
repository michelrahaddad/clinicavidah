from app import db
from models import Cid10
import logging

def populate_cid10_database():
    """Populate CID-10 database with common medical conditions"""
    try:
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
            {"codigo": "J44.0", "descricao": "DPOC com exacerbação aguda", "categoria": "Doenças respiratórias"},
            {"codigo": "J45.9", "descricao": "Asma brônquica", "categoria": "Doenças respiratórias"},
            {"codigo": "J18.9", "descricao": "Pneumonia", "categoria": "Doenças respiratórias"},
            {"codigo": "J06.9", "descricao": "Infecção das vias aéreas superiores", "categoria": "Doenças respiratórias"},
            
            # Gastrointestinal diseases
            {"codigo": "K59.0", "descricao": "Constipação intestinal", "categoria": "Doenças digestivas"},
            {"codigo": "K21.9", "descricao": "Doença do refluxo gastroesofágico", "categoria": "Doenças digestivas"},
            {"codigo": "K25.9", "descricao": "Úlcera gástrica", "categoria": "Doenças digestivas"},
            {"codigo": "K80.2", "descricao": "Cálculo da vesícula biliar", "categoria": "Doenças digestivas"},
            
            # Mental and behavioral disorders
            {"codigo": "F32.9", "descricao": "Episódio depressivo", "categoria": "Transtornos mentais"},
            {"codigo": "F41.9", "descricao": "Transtorno de ansiedade", "categoria": "Transtornos mentais"},
            {"codigo": "F43.2", "descricao": "Transtorno de adaptação", "categoria": "Transtornos mentais"},
            {"codigo": "F51.0", "descricao": "Insônia", "categoria": "Transtornos mentais"},
            
            # Musculoskeletal diseases
            {"codigo": "M54.5", "descricao": "Dor lombar", "categoria": "Doenças musculoesqueléticas"},
            {"codigo": "M25.5", "descricao": "Dor articular", "categoria": "Doenças musculoesqueléticas"},
            {"codigo": "M79.3", "descricao": "Fibromialgia", "categoria": "Doenças musculoesqueléticas"},
            {"codigo": "M06.9", "descricao": "Artrite reumatoide", "categoria": "Doenças musculoesqueléticas"},
            
            # Neurological diseases
            {"codigo": "G43.9", "descricao": "Enxaqueca", "categoria": "Doenças neurológicas"},
            {"codigo": "G44.2", "descricao": "Cefaleia tensional", "categoria": "Doenças neurológicas"},
            {"codigo": "G47.0", "descricao": "Distúrbios do sono", "categoria": "Doenças neurológicas"},
            
            # Skin diseases
            {"codigo": "L30.9", "descricao": "Dermatite", "categoria": "Doenças da pele"},
            {"codigo": "L40.9", "descricao": "Psoríase", "categoria": "Doenças da pele"},
            {"codigo": "L20.9", "descricao": "Dermatite atópica", "categoria": "Doenças da pele"},
            
            # Genitourinary diseases
            {"codigo": "N39.0", "descricao": "Infecção do trato urinário", "categoria": "Doenças geniturinárias"},
            {"codigo": "N18.9", "descricao": "Doença renal crônica", "categoria": "Doenças geniturinárias"},
            {"codigo": "N20.0", "descricao": "Cálculo renal", "categoria": "Doenças geniturinárias"},
            
            # Eye diseases
            {"codigo": "H52.1", "descricao": "Miopia", "categoria": "Doenças do olho"},
            {"codigo": "H25.9", "descricao": "Catarata", "categoria": "Doenças do olho"},
            {"codigo": "H40.9", "descricao": "Glaucoma", "categoria": "Doenças do olho"},
            
            # Infectious diseases
            {"codigo": "A09.9", "descricao": "Gastroenterite infecciosa", "categoria": "Doenças infecciosas"},
            {"codigo": "B34.9", "descricao": "Infecção viral", "categoria": "Doenças infecciosas"},
            {"codigo": "J00.0", "descricao": "Resfriado comum", "categoria": "Doenças infecciosas"},
            
            # Injuries and external causes
            {"codigo": "S72.0", "descricao": "Fratura do fêmur", "categoria": "Lesões e traumatismos"},
            {"codigo": "S62.5", "descricao": "Fratura do polegar", "categoria": "Lesões e traumatismos"},
            {"codigo": "S83.5", "descricao": "Entorse do joelho", "categoria": "Lesões e traumatismos"},
            
            # Pregnancy related
            {"codigo": "O80.0", "descricao": "Parto normal", "categoria": "Gravidez e parto"},
            {"codigo": "O21.9", "descricao": "Vômitos na gravidez", "categoria": "Gravidez e parto"},
            
            # General symptoms
            {"codigo": "R50.9", "descricao": "Febre", "categoria": "Sintomas gerais"},
            {"codigo": "R06.0", "descricao": "Dispneia", "categoria": "Sintomas gerais"},
            {"codigo": "R51.0", "descricao": "Cefaleia", "categoria": "Sintomas gerais"},
            {"codigo": "R10.4", "descricao": "Dor abdominal", "categoria": "Sintomas gerais"},
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
        return True
        
    except Exception as e:
        logging.error(f"Error populating CID-10 database: {e}")
        db.session.rollback()
        return False