from flask import Blueprint, jsonify, request, session
from models import Paciente, Receita, ExameLab, ExameImg, Prontuario, Cid10
from app import db
from sqlalchemy import func, or_
import csv
import logging
from utils.security import rate_limit, require_auth, audit_log

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/buscar_pacientes')
@rate_limit(max_requests=50, per_minutes=5)
@require_auth
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
            Paciente.email,
            Paciente.telefone,
            func.count(Prontuario.id).label('total_registros')
        ).outerjoin(Prontuario).filter(
            Paciente.nome.ilike(f'%{query}%')
        ).group_by(Paciente.id, Paciente.nome, Paciente.email, Paciente.telefone).limit(10).all()
        
        result = []
        for paciente in pacientes:
            result.append({
                'id': paciente.id,
                'nome': paciente.nome,
                'email': paciente.email,
                'telefone': paciente.telefone,
                'total_registros': paciente.total_registros or 0
            })
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f'Error searching patients: {e}')
        return jsonify([]), 500

@api_bp.route('/prontuario_paciente/<int:paciente_id>')
def prontuario_paciente(paciente_id):
    """Get patient medical records"""
    if 'usuario' not in session:
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

@api_bp.route('/medicamentos', methods=['GET', 'POST'])
def buscar_medicamentos():
    """Search medications from database"""
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('termo', '').strip() if data else ''
    else:
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

@api_bp.route('/record_details/<string:tipo>/<int:record_id>')
def record_details(tipo, record_id):
    """Get detailed record information"""
    if 'usuario' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if tipo == 'receita':
            record = Receita.query.get_or_404(record_id)
            return jsonify({
                'id': record.id,
                'nome_paciente': record.nome_paciente,
                'medicamentos': record.medicamentos,
                'posologias': record.posologias,
                'duracoes': record.duracoes,
                'vias': record.vias,
                'medico_nome': record.medico_nome,
                'data': record.data
            })
        elif tipo == 'exame_lab':
            record = ExameLab.query.get_or_404(record_id)
            return jsonify({
                'id': record.id,
                'nome_paciente': record.nome_paciente,
                'exames': record.exames,
                'medico_nome': record.medico_nome,
                'data': record.data
            })
        elif tipo == 'exame_img':
            record = ExameImg.query.get_or_404(record_id)
            return jsonify({
                'id': record.id,
                'nome_paciente': record.nome_paciente,
                'exames': record.exames,
                'medico_nome': record.medico_nome,
                'data': record.data
            })
        else:
            return jsonify({'error': 'Invalid record type'}), 400
            
    except Exception as e:
        logging.error(f'Error loading record details: {e}')
        return jsonify({'error': 'Record not found'}), 404

@api_bp.route('/exames_laboratoriais')
def buscar_exames_lab():
    """Get common lab exams organized by categories"""
    try:
        exames_por_categoria = {
            "Hematologia": [
                "Hemograma completo",
                "VHS (Velocidade de hemossedimentação)",
                "Coagulograma (TAP/TTPA)",
                "Tempo de sangramento",
                "Contagem de plaquetas"
            ],
            "Bioquímica": [
                "Glicemia de jejum",
                "Colesterol total e frações",
                "Triglicerídeos",
                "Ureia",
                "Creatinina",
                "Ácido úrico",
                "TGO (AST)",
                "TGP (ALT)",
                "Bilirrubinas",
                "Proteínas totais e frações",
                "HbA1c (Hemoglobina glicada)",
                "Ferro sérico",
                "Ferritina",
                "Proteína C reativa (PCR)"
            ],
            "Endocrinologia": [
                "TSH",
                "T4 livre",
                "Cortisol",
                "Testosterona total",
                "Testosterona livre",
                "FSH",
                "Estradiol",
                "Progesterona sérica",
                "Insulina",
                "Prolactina"
            ],
            "Urologia/Nefrologia": [
                "Exame de urina (EAS)",
                "Urina 1",
                "Urocultura",
                "PSA",
                "Clearance de creatinina",
                "Proteinúria 24h"
            ],
            "Gastroenterologia": [
                "Exame de fezes",
                "Parasitológico de fezes",
                "Coprocultura",
                "Sangue oculto nas fezes",
                "Elastase fecal"
            ],
            "Oncologia/Marcadores": [
                "PSA (Antígeno prostático específico)",
                "CEA",
                "CA 19-9",
                "CA 125",
                "AFP (Alfa-fetoproteína)",
                "Beta HCG"
            ],
            "Imunologia/Reumatologia": [
                "FAN (Fator antinuclear)",
                "Fator reumatoide",
                "Anti-CCP",
                "Complemento C3 e C4",
                "Anti-DNA"
            ],
            "Sorologias Virais": [
                "HBsAg",
                "Anti-HBs",
                "HCV",
                "Anti-HCV",
                "HIV (Anti-HIV)",
                "HTLV I/II",
                "Citomegalovírus IgG e IgM"
            ],
            "Sorologias Bacterianas/Parasitárias": [
                "VDRL",
                "FTA-ABS",
                "Sorologia Chagas",
                "Sorologia Toxoplasmose IgG e IgM",
                "Sorologia Rubéola IgG e IgM",
                "Sorologia para Hepatite A"
            ],
            "Tireoide": [
                "TSH",
                "T4 livre",
                "T3",
                "Anti-TPO",
                "Anti-tireoglobulina",
                "Tireoglobulina"
            ],
            "Vitaminas": [
                "Vitamina B12",
                "Vitamina D",
                "Ácido fólico",
                "Vitamina A",
                "Vitamina E"
            ]
        }
        
        # Flatten all exams into a single list for search functionality
        exames_comuns = []
        for categoria, exames in exames_por_categoria.items():
            exames_comuns.extend(exames)
        
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
            "Angiotomografia de coronárias",
            "Angiotomografia de aorta total",
            "Angiotomografia cerebral",
            "Angiotomografia abdominal",
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

@api_bp.route('/update_record_date', methods=['POST'])
def update_record_date():
    """Update record date"""
    if 'usuario' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        record_id = data.get('id')
        tipo = data.get('tipo')
        new_date = data.get('data')
        
        if not all([record_id, tipo, new_date]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Update the appropriate table based on type
        if tipo == 'receita':
            record = Receita.query.get_or_404(record_id)
        elif tipo == 'exame_lab':
            record = ExameLab.query.get_or_404(record_id)
        elif tipo == 'exame_img':
            record = ExameImg.query.get_or_404(record_id)
        else:
            return jsonify({'error': 'Invalid record type'}), 400
        
        # Update the date
        record.data = new_date
        db.session.commit()
        
        logging.info(f'Record date updated: {tipo} {record_id} to {new_date}')
        return jsonify({'success': True})
        
    except Exception as e:
        logging.error(f'Error updating record date: {e}')
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/buscar_cid10')
@require_auth
@rate_limit(50)
def buscar_cid10():
    """Search CID-10 codes by code or description"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    try:
        # Search by code or description
        results = Cid10.query.filter(
            or_(
                Cid10.codigo.ilike(f'%{query}%'),
                Cid10.descricao.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        cid_list = []
        for cid in results:
            cid_list.append({
                'codigo': cid.codigo,
                'descricao': cid.descricao,
                'categoria': cid.categoria
            })
        
        return jsonify(cid_list)
        
    except Exception as e:
        logging.error(f'Error searching CID-10: {e}')
        return jsonify([]), 500