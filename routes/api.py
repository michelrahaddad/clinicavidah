from flask import Blueprint, jsonify, request, session
from models import Paciente, Receita, ExameLab, ExameImg, Prontuario
from app import db
from sqlalchemy import func, or_
import csv
import logging

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/buscar_pacientes')
def buscar_pacientes():
    """Search patients by name"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    try:
        # Search patients by name (case insensitive)
        pacientes = db.session.query(
            Paciente.id,
            Paciente.nome,
            func.count(Prontuario.id).label('total_registros')
        ).outerjoin(Prontuario).filter(
            Paciente.nome.ilike(f'%{query}%')
        ).group_by(Paciente.id, Paciente.nome).limit(10).all()
        
        result = []
        for paciente in pacientes:
            result.append({
                'id': paciente.id,
                'nome': paciente.nome,
                'total_registros': paciente.total_registros or 0
            })
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f'Error searching patients: {e}')
        return jsonify([]), 500

@api_bp.route('/prontuario_paciente/<int:paciente_id>')
def prontuario_paciente(paciente_id):
    """Get patient medical records"""
    if 'medico_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        records = []
        
        # Get prescriptions
        receitas = Receita.query.filter_by(id_paciente=paciente_id).all()
        for receita in receitas:
            records.append({
                'id': receita.id,
                'tipo': 'receita',
                'data': receita.data,
                'medicamentos': receita.medicamentos,
                'posologias': receita.posologias,
                'duracoes': receita.duracoes,
                'vias': receita.vias
            })
        
        # Get lab exams
        exames_lab = ExameLab.query.filter_by(id_paciente=paciente_id).all()
        for exame in exames_lab:
            records.append({
                'id': exame.id,
                'tipo': 'exame_lab',
                'data': exame.data,
                'exames': exame.exames
            })
        
        # Get imaging exams
        exames_img = ExameImg.query.filter_by(id_paciente=paciente_id).all()
        for exame in exames_img:
            records.append({
                'id': exame.id,
                'tipo': 'exame_img',
                'data': exame.data,
                'exames': exame.exames
            })
        
        return jsonify(records)
        
    except Exception as e:
        logging.error(f'Error loading patient records: {e}')
        return jsonify([]), 500

@api_bp.route('/medicamentos')
def buscar_medicamentos():
    """Search medications from database"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    try:
        medicamentos = []
        
        # Read medications from CSV file
        with open('data/medicamentos.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                nome = row.get('Nome', '')
                principio = row.get('Princípio Ativo', '')
                posologia = row.get('Posologia', '')
                via = row.get('Via de Administração', 'Oral')
                
                # Search in name or active ingredient
                if (query.lower() in nome.lower() or 
                    query.lower() in principio.lower()):
                    medicamentos.append({
                        'nome': nome,
                        'principio_ativo': principio,
                        'posologia_sugerida': posologia,
                        'via_administracao': via
                    })
                
                # Limit results
                if len(medicamentos) >= 20:
                    break
        
        return jsonify(medicamentos)
        
    except Exception as e:
        logging.error(f'Error searching medications: {e}')
        return jsonify([])

@api_bp.route('/exames_laboratoriais')
def buscar_exames_lab():
    """Get common lab exams"""
    try:
        exames_comuns = [
            "Hemograma completo",
            "Glicemia de jejum",
            "Colesterol total e frações",
            "Triglicerídeos",
            "Ureia e Creatinina",
            "Ácido úrico",
            "TGO (AST) e TGP (ALT)",
            "Bilirrubinas",
            "Proteínas totais e frações",
            "TSH e T4 livre",
            "Exame de urina (EAS)",
            "Urocultura",
            "Proteína C reativa (PCR)",
            "VHS (Velocidade de hemossedimentação)",
            "Ferro sérico e ferritina",
            "Vitamina B12",
            "Vitamina D",
            "HbA1c (Hemoglobina glicada)",
            "Cortisol",
            "Testosterona",
            "PSA (Antígeno prostático específico)",
            "Beta HCG",
            "Parasitológico de fezes",
            "Coprocultura",
            "Hepatite B e C",
            "HIV",
            "VDRL",
            "Toxoplasmose IgG e IgM",
            "Rubéola IgG e IgM",
            "Citomegalovírus IgG e IgM"
        ]
        
        query = request.args.get('q', '').strip().lower()
        
        if query:
            # Filter exams based on search query
            exames_filtrados = [exame for exame in exames_comuns if query in exame.lower()]
            return jsonify(exames_filtrados[:15])
        
        return jsonify(exames_comuns[:15])
        
    except Exception as e:
        logging.error(f'Error getting lab exams: {e}')
        return jsonify([])

@api_bp.route('/exames_imagem')
def buscar_exames_img():
    """Get common imaging exams"""
    try:
        exames_comuns = [
            "Radiografia de tórax",
            "Radiografia de abdome",
            "Radiografia de coluna lombar",
            "Radiografia de coluna cervical",
            "Radiografia de joelho",
            "Radiografia de quadril",
            "Ultrassom de abdome total",
            "Ultrassom pélvico",
            "Ultrassom de tireoide",
            "Ultrassom obstétrico",
            "Ultrassom doppler de carótidas",
            "Ultrassom doppler de membros inferiores",
            "Tomografia de crânio",
            "Tomografia de tórax",
            "Tomografia de abdome e pelve",
            "Ressonância magnética de crânio",
            "Ressonância magnética de coluna lombar",
            "Ressonância magnética de joelho",
            "Mamografia bilateral",
            "Densitometria óssea",
            "Ecocardiograma",
            "Eletrocardiograma (ECG)",
            "Holter 24 horas",
            "MAPA (Monitorização ambulatorial da pressão arterial)",
            "Teste ergométrico",
            "Endoscopia digestiva alta",
            "Colonoscopia",
            "Retossigmoidoscopia"
        ]
        
        query = request.args.get('q', '').strip().lower()
        
        if query:
            # Filter exams based on search query
            exames_filtrados = [exame for exame in exames_comuns if query in exame.lower()]
            return jsonify(exames_filtrados[:15])
        
        return jsonify(exames_comuns[:15])
        
    except Exception as e:
        logging.error(f'Error getting imaging exams: {e}')
        return jsonify([])