"""
Blueprint de Pacientes - Sistema Médico VIDAH
Gestão completa de pacientes com validação e histórico médico
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from sqlalchemy import func, desc, or_
from datetime import datetime
from models import Paciente, Receita, ExamesLab, ExamesImg, Atestado
from app import db
from blueprints.auth import require_auth, require_doctor
from validators.medical import get_validator
from validators.base import sanitize_input, ValidationError
from core.logging import get_logger, log_action

logger = get_logger('patients')
patients_bp = Blueprint('patients', __name__, url_prefix='/pacientes')


@patients_bp.route('/')
@require_doctor
@log_action('list_patients')
def index():
    """Lista todos os pacientes"""
    user = session.get('usuario')
    user_type = session.get('usuario_tipo', 'medico')
    
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '').strip()
        
        query = db.session.query(Paciente)
        
        if search:
            search_term = sanitize_input(search)
            query = query.filter(
                or_(
                    Paciente.nome.ilike(f'%{search_term}%'),
                    Paciente.cpf.ilike(f'%{search_term}%'),
                    Paciente.email.ilike(f'%{search_term}%')
                )
            )
        
        query = query.order_by(desc(Paciente.data_criacao))
        
        # Paginação
        per_page = 20
        patients = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        logger.info(f"Listed {len(patients.items)} patients for {user}")
        
        return render_template('pacientes/index.html',
                             patients=patients,
                             search=search,
                             user=user,
                             user_type=user_type)
                             
    except Exception as e:
        logger.error(f"Error listing patients: {str(e)}")
        flash('Erro ao carregar pacientes', 'error')
        return redirect(url_for('dashboard.index'))


@patients_bp.route('/novo', methods=['GET', 'POST'])
@require_doctor
@log_action('create_patient')
def novo():
    """Cria novo paciente"""
    user = session.get('usuario')
    
    if request.method == 'POST':
        try:
            # Validar dados do paciente
            validator = get_validator('patient')
            form_data = {
                'nome': sanitize_input(request.form.get('nome', '')),
                'cpf': sanitize_input(request.form.get('cpf', '')),
                'idade': request.form.get('idade', type=int),
                'email': sanitize_input(request.form.get('email', '')),
                'telefone': sanitize_input(request.form.get('telefone', '')),
                'endereco': sanitize_input(request.form.get('endereco', '')),
                'cidade_uf': sanitize_input(request.form.get('cidade_uf', ''))
            }
            
            validated_data = validator.validate(form_data)
            
            # Verificar se CPF já existe (se fornecido)
            if validated_data.get('cpf'):
                existing = db.session.query(Paciente).filter_by(cpf=validated_data['cpf']).first()
                if existing:
                    flash('CPF já cadastrado no sistema', 'error')
                    return render_template('pacientes/novo.html', user=user, form_data=form_data)
            
            # Criar paciente
            paciente = Paciente(
                nome=validated_data['nome'],
                cpf=validated_data.get('cpf') or '000.000.000-00',
                idade=validated_data.get('idade', 0),
                email=validated_data.get('email') or '',
                telefone=validated_data.get('telefone') or '',
                endereco=validated_data.get('endereco') or 'Não informado',
                cidade_uf=validated_data.get('cidade_uf') or 'Não informado/XX',
                data_criacao=datetime.now()
            )
            
            db.session.add(paciente)
            db.session.commit()
            
            logger.info(f"Patient created: {validated_data['nome']} (ID: {paciente.id})")
            flash('Paciente cadastrado com sucesso!', 'success')
            
            return redirect(url_for('patients.visualizar', paciente_id=paciente.id))
            
        except ValidationError as e:
            logger.warning(f"Patient validation error: {e.message}")
            flash(f'Erro de validação: {e.message}', 'error')
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            flash('Erro ao cadastrar paciente', 'error')
            db.session.rollback()
    
    return render_template('pacientes/novo.html', user=user)


@patients_bp.route('/<int:paciente_id>')
@require_doctor
@log_action('view_patient')
def visualizar(paciente_id):
    """Visualiza paciente específico"""
    user = session.get('usuario')
    user_type = session.get('usuario_tipo', 'medico')
    
    try:
        paciente = db.session.query(Paciente).filter_by(id=paciente_id).first()
        
        if not paciente:
            flash('Paciente não encontrado', 'error')
            return redirect(url_for('patients.index'))
        
        # Buscar histórico médico
        historico = get_patient_history(paciente.nome, user_type, user)
        
        # Estatísticas do paciente
        stats = get_patient_statistics(paciente.nome, user_type, user)
        
        logger.info(f"Viewed patient {paciente_id}")
        
        return render_template('pacientes/visualizar.html',
                             paciente=paciente,
                             historico=historico,
                             stats=stats,
                             user=user,
                             user_type=user_type)
                             
    except Exception as e:
        logger.error(f"Error viewing patient {paciente_id}: {str(e)}")
        flash('Erro ao carregar paciente', 'error')
        return redirect(url_for('patients.index'))


@patients_bp.route('/<int:paciente_id>/editar', methods=['GET', 'POST'])
@require_doctor
@log_action('edit_patient')
def editar(paciente_id):
    """Edita paciente existente"""
    user = session.get('usuario')
    
    try:
        paciente = db.session.query(Paciente).filter_by(id=paciente_id).first()
        
        if not paciente:
            flash('Paciente não encontrado', 'error')
            return redirect(url_for('patients.index'))
        
        if request.method == 'POST':
            try:
                # Validar dados
                validator = get_validator('patient')
                form_data = {
                    'nome': sanitize_input(request.form.get('nome', '')),
                    'cpf': sanitize_input(request.form.get('cpf', '')),
                    'idade': request.form.get('idade', type=int),
                    'email': sanitize_input(request.form.get('email', '')),
                    'telefone': sanitize_input(request.form.get('telefone', '')),
                    'endereco': sanitize_input(request.form.get('endereco', '')),
                    'cidade_uf': sanitize_input(request.form.get('cidade_uf', ''))
                }
                
                validated_data = validator.validate(form_data)
                
                # Verificar CPF duplicado (exceto o próprio paciente)
                if validated_data.get('cpf') and validated_data['cpf'] != paciente.cpf:
                    existing = db.session.query(Paciente).filter(
                        Paciente.cpf == validated_data['cpf'],
                        Paciente.id != paciente_id
                    ).first()
                    if existing:
                        flash('CPF já cadastrado para outro paciente', 'error')
                        return render_template('pacientes/editar.html', 
                                             paciente=paciente, 
                                             user=user, 
                                             form_data=form_data)
                
                # Atualizar paciente
                paciente.nome = validated_data['nome']
                paciente.cpf = validated_data.get('cpf') or paciente.cpf
                paciente.idade = validated_data.get('idade', paciente.idade)
                paciente.email = validated_data.get('email') or paciente.email
                paciente.telefone = validated_data.get('telefone') or paciente.telefone
                paciente.endereco = validated_data.get('endereco') or paciente.endereco
                paciente.cidade_uf = validated_data.get('cidade_uf') or paciente.cidade_uf
                
                db.session.commit()
                
                logger.info(f"Patient {paciente_id} updated")
                flash('Paciente atualizado com sucesso!', 'success')
                
                return redirect(url_for('patients.visualizar', paciente_id=paciente_id))
                
            except ValidationError as e:
                logger.warning(f"Patient edit validation error: {e.message}")
                flash(f'Erro de validação: {e.message}', 'error')
            except Exception as e:
                logger.error(f"Error updating patient {paciente_id}: {str(e)}")
                flash('Erro ao atualizar paciente', 'error')
                db.session.rollback()
        
        return render_template('pacientes/editar.html',
                             paciente=paciente,
                             user=user)
                             
    except Exception as e:
        logger.error(f"Error editing patient {paciente_id}: {str(e)}")
        flash('Erro ao carregar paciente para edição', 'error')
        return redirect(url_for('patients.index'))


@patients_bp.route('/api/search')
@require_doctor
def api_search():
    """API para busca de pacientes"""
    try:
        query = request.args.get('q', '').strip()
        if not query or len(query) < 2:
            return jsonify([])
        
        query = sanitize_input(query)
        
        # Buscar pacientes
        patients = db.session.query(Paciente).filter(
            or_(
                Paciente.nome.ilike(f'%{query}%'),
                Paciente.cpf.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        result = []
        for patient in patients:
            result.append({
                'id': patient.id,
                'nome': patient.nome,
                'cpf': patient.cpf if patient.cpf != '000.000.000-00' else '',
                'idade': f"{patient.idade} anos" if patient.idade > 0 else '',
                'telefone': patient.telefone if patient.telefone else ''
            })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in patient search API: {str(e)}")
        return jsonify([]), 500


@patients_bp.route('/<int:paciente_id>/historico')
@require_doctor
@log_action('view_patient_history')
def historico(paciente_id):
    """Visualiza histórico médico completo do paciente"""
    user = session.get('usuario')
    user_type = session.get('usuario_tipo', 'medico')
    
    try:
        paciente = db.session.query(Paciente).filter_by(id=paciente_id).first()
        
        if not paciente:
            flash('Paciente não encontrado', 'error')
            return redirect(url_for('patients.index'))
        
        # Buscar histórico completo
        historico_completo = get_complete_patient_history(paciente.nome, user_type, user)
        
        logger.info(f"Viewed complete history for patient {paciente_id}")
        
        return render_template('pacientes/historico.html',
                             paciente=paciente,
                             historico=historico_completo,
                             user=user,
                             user_type=user_type)
                             
    except Exception as e:
        logger.error(f"Error viewing patient history {paciente_id}: {str(e)}")
        flash('Erro ao carregar histórico', 'error')
        return redirect(url_for('patients.visualizar', paciente_id=paciente_id))


def get_patient_history(patient_name, user_type, user):
    """Busca histórico médico resumido do paciente"""
    history = []
    
    try:
        # Receitas recentes
        receitas_query = db.session.query(Receita).filter_by(nome_paciente=patient_name)
        if user_type != 'admin':
            receitas_query = receitas_query.filter_by(medico=user)
        
        receitas = receitas_query.order_by(desc(Receita.data_criacao)).limit(5).all()
        
        for receita in receitas:
            history.append({
                'type': 'receita',
                'title': 'Receita Médica',
                'description': f"Medicamentos: {len(receita.medicamentos.split(',')) if receita.medicamentos else 0}",
                'date': receita.data_criacao,
                'medico': receita.medico,
                'id': receita.id
            })
        
        # Exames recentes
        exames_query = db.session.query(ExamesLab).filter_by(nome_paciente=patient_name)
        if user_type != 'admin':
            exames_query = exames_query.filter_by(medico=user)
        
        exames = exames_query.order_by(desc(ExamesLab.data_criacao)).limit(3).all()
        
        for exame in exames:
            history.append({
                'type': 'exame_lab',
                'title': 'Exame Laboratorial',
                'description': f"Exames: {len(exame.exames_solicitados.split(',')) if exame.exames_solicitados else 0}",
                'date': exame.data_criacao,
                'medico': exame.medico,
                'id': exame.id
            })
        
        # Ordenar por data
        history.sort(key=lambda x: x['date'] or datetime.min, reverse=True)
        
    except Exception as e:
        logger.error(f"Error getting patient history: {str(e)}")
    
    return history[:10]


def get_complete_patient_history(patient_name, user_type, user):
    """Busca histórico médico completo do paciente"""
    history = {
        'receitas': [],
        'exames_lab': [],
        'exames_img': [],
        'atestados': []
    }
    
    try:
        # Receitas
        receitas_query = db.session.query(Receita).filter_by(nome_paciente=patient_name)
        if user_type != 'admin':
            receitas_query = receitas_query.filter_by(medico=user)
        
        history['receitas'] = receitas_query.order_by(desc(Receita.data_criacao)).all()
        
        # Exames laboratoriais
        exames_lab_query = db.session.query(ExamesLab).filter_by(nome_paciente=patient_name)
        if user_type != 'admin':
            exames_lab_query = exames_lab_query.filter_by(medico=user)
        
        history['exames_lab'] = exames_lab_query.order_by(desc(ExamesLab.data_criacao)).all()
        
        # Exames de imagem
        exames_img_query = db.session.query(ExamesImg).filter_by(nome_paciente=patient_name)
        if user_type != 'admin':
            exames_img_query = exames_img_query.filter_by(medico=user)
        
        history['exames_img'] = exames_img_query.order_by(desc(ExamesImg.data_criacao)).all()
        
        # Atestados
        atestados_query = db.session.query(Atestado).filter_by(nome_paciente=patient_name)
        if user_type != 'admin':
            atestados_query = atestados_query.filter_by(medico=user)
        
        history['atestados'] = atestados_query.order_by(desc(Atestado.data_criacao)).all()
        
    except Exception as e:
        logger.error(f"Error getting complete patient history: {str(e)}")
    
    return history


def get_patient_statistics(patient_name, user_type, user):
    """Calcula estatísticas do paciente"""
    stats = {}
    
    try:
        # Contadores básicos
        receitas_query = db.session.query(func.count(Receita.id)).filter_by(nome_paciente=patient_name)
        if user_type != 'admin':
            receitas_query = receitas_query.filter_by(medico=user)
        stats['total_receitas'] = receitas_query.scalar() or 0
        
        exames_lab_query = db.session.query(func.count(ExamesLab.id)).filter_by(nome_paciente=patient_name)
        if user_type != 'admin':
            exames_lab_query = exames_lab_query.filter_by(medico=user)
        stats['total_exames_lab'] = exames_lab_query.scalar() or 0
        
        exames_img_query = db.session.query(func.count(ExamesImg.id)).filter_by(nome_paciente=patient_name)
        if user_type != 'admin':
            exames_img_query = exames_img_query.filter_by(medico=user)
        stats['total_exames_img'] = exames_img_query.scalar() or 0
        
        atestados_query = db.session.query(func.count(Atestado.id)).filter_by(nome_paciente=patient_name)
        if user_type != 'admin':
            atestados_query = atestados_query.filter_by(medico=user)
        stats['total_atestados'] = atestados_query.scalar() or 0
        
        # Última consulta
        ultima_receita = db.session.query(Receita.data_criacao).filter_by(nome_paciente=patient_name)
        if user_type != 'admin':
            ultima_receita = ultima_receita.filter_by(medico=user)
        ultima_receita = ultima_receita.order_by(desc(Receita.data_criacao)).first()
        
        stats['ultima_consulta'] = ultima_receita.data_criacao if ultima_receita else None
        
    except Exception as e:
        logger.error(f"Error calculating patient statistics: {str(e)}")
        stats = {
            'total_receitas': 0,
            'total_exames_lab': 0,
            'total_exames_img': 0,
            'total_atestados': 0,
            'ultima_consulta': None
        }
    
    return stats