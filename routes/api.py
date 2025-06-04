from flask import Blueprint, jsonify, request, session, make_response, redirect, url_for
from models import Paciente, Receita, ExameLab, ExameImg, Prontuario, Cid10, ExamePersonalizado, Medicamento
from app import db
from sqlalchemy import func, or_, text
import csv
import logging
from utils.security import rate_limit, require_auth, audit_log
from utils.forms import sanitizar_entrada
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/pacientes')
def get_pacientes():
    """API para autocomplete de pacientes"""
    # Permitir acesso se usuário ou admin logado
    if not (session.get('usuario') or session.get('admin_usuario')):
        return jsonify([])
    
    try:
        term = request.args.get('q', '').strip()
        if len(term) < 2:
            return jsonify([])
        
        pacientes = Paciente.query.filter(
            Paciente.nome.ilike(f'%{term}%')
        ).limit(10).all()
        
        result = []
        for p in pacientes:
            result.append({
                'id': p.id,
                'nome': p.nome,
                'cpf': p.cpf or '',
                'idade': str(p.idade) if p.idade else '',
                'endereco': p.endereco or '',
                'cidade': p.cidade_uf or ''
            })
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Erro na API de pacientes: {e}")
        return jsonify([])

@api_bp.route('/medicamentos')
def get_medicamentos():
    """API para autocomplete de medicamentos com dados reais do banco"""
    # Permitir acesso se usuário ou admin logado
    if not (session.get('usuario') or session.get('admin_usuario')):
        return jsonify([])

@api_bp.route('/medicamentos_historico')
def get_medicamentos_historico():
    """API para autocomplete inteligente baseado no histórico de prescrições"""
    # Permitir acesso se usuário ou admin logado
    if not (session.get('usuario') or session.get('admin_usuario')):
        return jsonify([])
    
    try:
        term = request.args.get('q', '').strip().lower()
        if len(term) < 2:
            return jsonify([])
        
        # Obter ID do médico
        usuario_data = session.get('usuario') or session.get('admin_usuario')
        if isinstance(usuario_data, dict):
            medico_id = usuario_data.get('id')
        else:
            # Fallback - usar qualquer médico
            medico_id = 1
        
        # Buscar medicamentos no histórico do médico, ordenados por frequência de uso
        query = """
            SELECT principio_ativo, concentracao, via, frequencia, quantidade, vezes_prescrito
            FROM medicamentos_historico 
            WHERE principio_ativo ILIKE %s AND id_medico = %s
            ORDER BY vezes_prescrito DESC, ultima_prescricao DESC
            LIMIT 10
        """
        
        result = db.session.execute(query, (f'%{term}%', medico_id)).fetchall()
        
        medicamentos = []
        for row in result:
            medicamentos.append({
                'principio_ativo': row[0],
                'concentracao': row[1] or '',
                'via': row[2] or '',
                'frequencia': row[3] or '',
                'quantidade': row[4] or '',
                'vezes_prescrito': row[5] or 0
            })
        
        return jsonify(medicamentos)
    except Exception as e:
        logging.error(f"Erro na API de medicamentos histórico: {e}")
        return jsonify([])

@api_bp.route('/medicamento_dados/<principio_ativo>')
def get_medicamento_dados(principio_ativo):
    """API para obter dados completos de um medicamento baseado no histórico"""
    # Permitir acesso se usuário ou admin logado
    if not (session.get('usuario') or session.get('admin_usuario')):
        return jsonify({})
    
    try:
        # Obter ID do médico
        usuario_data = session.get('usuario') or session.get('admin_usuario')
        if isinstance(usuario_data, dict):
            medico_id = usuario_data.get('id')
        else:
            medico_id = 1
        
        # Buscar o medicamento mais prescrito pelo médico
        query = """
            SELECT concentracao, via, frequencia, quantidade
            FROM medicamentos_historico 
            WHERE principio_ativo ILIKE %s AND id_medico = %s
            ORDER BY vezes_prescrito DESC, ultima_prescricao DESC
            LIMIT 1
        """
        
        result = db.session.execute(query, (principio_ativo.lower(), medico_id)).fetchone()
        
        if result:
            return jsonify({
                'concentracao': result[0] or '',
                'via': result[1] or '',
                'frequencia': result[2] or '',
                'quantidade': result[3] or ''
            })
        else:
            return jsonify({})
    except Exception as e:
        logging.error(f"Erro na API de dados do medicamento: {e}")
        return jsonify({})
    
    try:
        term = request.args.get('q', '').strip()
        
        if len(term) < 2:
            return jsonify([])
        
        # Busca nos medicamentos reais do banco
        medicamentos = Medicamento.query.filter(
            or_(
                Medicamento.nome.ilike(f'%{term}%'),
                Medicamento.principio_ativo.ilike(f'%{term}%')
            )
        ).limit(15).all()
        
        result = []
        for m in medicamentos:
            # Dados padrão
            via_padrao = 'Oral'
            frequencia_padrao = '3x'  # Padrão 3x ao dia
            quantidade_padrao = '30 comprimidos'  # Padrão sempre 30 comprimidos
            
            nome_lower = m.nome.lower()
            principio_lower = m.principio_ativo.lower()
            
            # Mapeamento específico baseado na planilha real
            if 'dipirona' in principio_lower:
                via_padrao = 'Oral'
                frequencia_padrao = '3x'  # A cada 8 horas = 3x ao dia
                quantidade_padrao = '30 comprimidos'
            elif 'paracetamol' in principio_lower:
                via_padrao = 'Oral' 
                frequencia_padrao = '4x'  # A cada 6 horas = 4x ao dia
                quantidade_padrao = '30 comprimidos'
            elif 'losartana' in principio_lower:
                via_padrao = 'Oral'
                frequencia_padrao = '1x'  # 1x ao dia
                quantidade_padrao = '30 comprimidos'
            elif 'omeprazol' in principio_lower:
                via_padrao = 'Oral'
                frequencia_padrao = '1x'  # 1x ao dia em jejum
                quantidade_padrao = '30 comprimidos'
            elif 'metformina' in principio_lower:
                via_padrao = 'Oral'
                frequencia_padrao = '2x'  # 2x ao dia
                quantidade_padrao = '30 comprimidos'
            elif 'amoxicilina' in principio_lower:
                via_padrao = 'Oral'
                frequencia_padrao = '2x'  # De 12 em 12 horas
                quantidade_padrao = '30 comprimidos'
            elif 'ibuprofeno' in principio_lower:
                via_padrao = 'Oral'
                frequencia_padrao = '2x'  # A cada 6-8 horas
                quantidade_padrao = '30 comprimidos'
            elif 'sinvastatina' in principio_lower:
                via_padrao = 'Oral'
                frequencia_padrao = '1x'  # 1x ao dia à noite
                quantidade_padrao = '30 comprimidos'
            elif 'atenolol' in principio_lower:
                via_padrao = 'Oral'
                frequencia_padrao = '1x'  # 1x ao dia
                quantidade_padrao = '30 comprimidos'
            elif 'captopril' in principio_lower:
                via_padrao = 'Oral'
                frequencia_padrao = '3x'  # 2-3x ao dia
                quantidade_padrao = '30 comprimidos'
            
            # Detecta medicamentos injetáveis
            if 'injetável' in nome_lower or 'ampola' in nome_lower:
                if 'endovenosa' in nome_lower or 'iv' in nome_lower:
                    via_padrao = 'Endovenosa'
                else:
                    via_padrao = 'Intramuscular'
                quantidade_padrao = '1 ampola'
            elif 'sublingual' in nome_lower:
                via_padrao = 'Sublingual'
            elif 'tópic' in nome_lower or 'pomada' in nome_lower:
                via_padrao = 'Tópica'
                quantidade_padrao = '1 tubo'
            elif 'inalat' in nome_lower or 'spray' in nome_lower:
                via_padrao = 'Nasal'
                quantidade_padrao = '1 frasco'
            
            result.append({
                'id': m.id,
                'nome': m.nome,
                'principio_ativo': m.principio_ativo,
                'concentracao': m.concentracao or '500mg',  # Padrão se não tiver
                'via_padrao': via_padrao,
                'frequencia_padrao': frequencia_padrao,
                'quantidade_padrao': quantidade_padrao,
                'tipo': m.tipo
            })
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Erro na API de medicamentos: {e}")
        return jsonify([])

@api_bp.route('/buscar_pacientes')
@rate_limit(max_requests=50, per_minutes=5)
@require_auth
def buscar_pacientes():
    # Setup admin access
    admin_data = session.get('admin_data')
    is_admin = admin_data or 'admin_usuario' in session

    """Search patients by name"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    try:
        # Search patients by name (case insensitive)
        pacientes = db.session.query(
            Paciente.id,
            Paciente.nome,
            Paciente.cpf,
            Paciente.idade,
            Paciente.endereco,
            Paciente.cidade_uf,
            Paciente.email,
            Paciente.telefone,
            func.count(Prontuario.id).label('total_registros')
        ).outerjoin(Prontuario).filter(
            Paciente.nome.ilike(f'%{query}%')
        ).group_by(
            Paciente.id, Paciente.nome, Paciente.cpf, Paciente.idade, 
            Paciente.endereco, Paciente.cidade_uf, Paciente.email, Paciente.telefone
        ).limit(10).all()
        
        result = []
        for paciente in pacientes:
            result.append({
                'id': paciente.id,
                'nome': paciente.nome,
                'cpf': paciente.cpf,
                'idade': paciente.idade,
                'endereco': paciente.endereco,
                'cidade_uf': paciente.cidade_uf,
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
    if 'usuario' not in session and 'admin_usuario' not in session:
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
    if 'usuario' not in session and 'admin_usuario' not in session:
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
    if 'usuario' not in session and 'admin_usuario' not in session:
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

@api_bp.route('/adicionar_exame_personalizado', methods=['POST'])
def adicionar_exame_personalizado():
    """Add custom exam"""
    try:
        if 'usuario' not in session and 'admin_usuario' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        nome_exame = sanitizar_entrada(request.form.get('nome_exame', ''))
        tipo_exame = sanitizar_entrada(request.form.get('tipo_exame', ''))  # 'laboratorial' ou 'imagem'
        categoria = sanitizar_entrada(request.form.get('categoria', ''))
        
        if not nome_exame or not tipo_exame:
            return jsonify({'success': False, 'message': 'Nome do exame e tipo são obrigatórios'}), 400
        
        if tipo_exame not in ['laboratorial', 'imagem']:
            return jsonify({'success': False, 'message': 'Tipo de exame inválido'}), 400
        
        # Check if exam already exists for this doctor
        medico_id = session['usuario']['id']
        exame_existente = db.session.execute(
            text("SELECT id FROM exames_personalizados WHERE nome = :nome AND tipo = :tipo AND id_medico = :medico_id"),
            {'nome': nome_exame, 'tipo': tipo_exame, 'medico_id': medico_id}
        ).fetchone()
        
        if exame_existente:
            return jsonify({'success': False, 'message': 'Exame já existe'}), 400
        
        # Insert new custom exam
        db.session.execute(
            text("""
                INSERT INTO exames_personalizados (nome, tipo, categoria, id_medico, ativo, created_at)
                VALUES (:nome, :tipo, :categoria, :medico_id, true, :created_at)
            """),
            {
                'nome': nome_exame,
                'tipo': tipo_exame,
                'categoria': categoria,
                'medico_id': medico_id,
                'created_at': datetime.utcnow()
            }
        )
        db.session.commit()
        
        logging.info(f'Custom exam added: {nome_exame} by doctor {medico_id}')
        return jsonify({'success': True, 'message': 'Exame adicionado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error adding custom exam: {e}')
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@api_bp.route('/listar_exames_personalizados/<tipo>')
def listar_exames_personalizados(tipo):
    """List custom exams by type"""
    try:
        if 'usuario' not in session and 'admin_usuario' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        if tipo not in ['laboratorial', 'imagem']:
            return jsonify({'success': False, 'message': 'Tipo de exame inválido'}), 400
        
        medico_id = session['usuario']['id']
        
        exames = db.session.execute(
            text("""
                SELECT id, nome, categoria 
                FROM exames_personalizados 
                WHERE tipo = :tipo AND id_medico = :medico_id AND ativo = true
                ORDER BY nome ASC
            """),
            {'tipo': tipo, 'medico_id': medico_id}
        ).fetchall()
        
        exames_list = []
        for exame in exames:
            exames_list.append({
                'id': exame.id,
                'nome': exame.nome,
                'categoria': exame.categoria
            })
        
        return jsonify({'success': True, 'exames': exames_list})
        
    except Exception as e:
        logging.error(f'Error listing custom exams: {e}')
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@api_bp.route('/remover_exame_personalizado/<int:exame_id>', methods=['DELETE'])
def remover_exame_personalizado(exame_id):
    """Remove custom exam (soft delete)"""
    try:
        if 'usuario' not in session and 'admin_usuario' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        medico_id = session['usuario']['id']
        
        # Verify if exam belongs to this doctor
        exame_exists = db.session.execute(
            text("SELECT id FROM exames_personalizados WHERE id = :exame_id AND id_medico = :medico_id"),
            {'exame_id': exame_id, 'medico_id': medico_id}
        ).fetchone()
        
        if not exame_exists:
            return jsonify({'success': False, 'message': 'Exame não encontrado'}), 404
        
        # Soft delete (set ativo = false)
        result = db.session.execute(
            text("UPDATE exames_personalizados SET ativo = false WHERE id = :exame_id AND id_medico = :medico_id"),
            {'exame_id': exame_id, 'medico_id': medico_id}
        )
        db.session.commit()
        
        logging.info(f'Custom exam removed: {exame_id} by doctor {medico_id}')
        return jsonify({'success': True, 'message': 'Exame removido com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error removing custom exam: {e}')
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500