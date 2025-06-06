"""
Blueprint de Prescrições Médicas - Sistema Médico VIDAH
Gestão completa de receitas médicas com validação e PDF
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
from models import Receita, Paciente, Medico
from app import db
from blueprints.auth import require_auth, require_doctor
from validators.medical import get_validator
from validators.base import sanitize_input, ValidationError
from services.pdf_service import generate_prescription_pdf
from core.logging import get_logger, log_action

logger = get_logger('prescriptions')
prescriptions_bp = Blueprint('prescriptions', __name__, url_prefix='/receitas')


@prescriptions_bp.route('/')
@require_doctor
@log_action('list_prescriptions')
def index():
    """Lista todas as receitas do médico"""
    user = session.get('usuario')
    user_type = session.get('usuario_tipo', 'medico')
    
    try:
        query = db.session.query(Receita).order_by(Receita.data_criacao.desc())
        
        if user_type != 'admin':
            query = query.filter_by(medico=user)
        
        receitas = query.limit(50).all()
        
        logger.info(f"Listed {len(receitas)} prescriptions for {user}")
        
        return render_template('receitas/index.html', 
                             receitas=receitas, 
                             user=user,
                             user_type=user_type)
                             
    except Exception as e:
        logger.error(f"Error listing prescriptions: {str(e)}")
        flash('Erro ao carregar receitas', 'error')
        return redirect(url_for('dashboard.index'))


@prescriptions_bp.route('/nova', methods=['GET', 'POST'])
@require_doctor
@log_action('create_prescription')
def nova():
    """Cria nova receita médica"""
    user = session.get('usuario')
    
    if request.method == 'POST':
        try:
            # Validar dados da receita
            validator = get_validator('prescription')
            form_data = request.form.to_dict()
            
            # Processar listas de medicamentos
            medicamentos = []
            posologias = []
            vias = []
            duracoes = []
            
            for key, value in form_data.items():
                if key.startswith('medicamento_') and value.strip():
                    idx = key.split('_')[1]
                    medicamentos.append(sanitize_input(value))
                    posologias.append(sanitize_input(form_data.get(f'posologia_{idx}', '')))
                    vias.append(sanitize_input(form_data.get(f'via_{idx}', 'oral')))
                    duracoes.append(sanitize_input(form_data.get(f'duracao_{idx}', '')))
            
            prescription_data = {
                'nome_paciente': sanitize_input(form_data.get('nome_paciente', '')),
                'medicamentos': medicamentos,
                'posologias': posologias,
                'vias': vias,
                'duracoes': duracoes,
                'observacoes': sanitize_input(form_data.get('observacoes', ''))
            }
            
            validated_data = validator.validate(prescription_data)
            
            # Criar receita
            receita = Receita(
                nome_paciente=validated_data['nome_paciente'],
                medicamentos=','.join(validated_data['medicamentos']),
                posologias=','.join(validated_data['posologias']),
                vias=','.join(validated_data['vias']),
                duracoes=','.join(validated_data['duracoes']),
                observacoes=validated_data.get('observacoes', ''),
                medico=user,
                data_criacao=datetime.now()
            )
            
            db.session.add(receita)
            db.session.commit()
            
            logger.info(f"Prescription created: ID {receita.id} for patient {validated_data['nome_paciente']}")
            flash('Receita criada com sucesso!', 'success')
            
            return redirect(url_for('prescriptions.visualizar', receita_id=receita.id))
            
        except ValidationError as e:
            logger.warning(f"Prescription validation error: {e.message}")
            flash(f'Erro de validação: {e.message}', 'error')
        except Exception as e:
            logger.error(f"Error creating prescription: {str(e)}")
            flash('Erro ao criar receita', 'error')
            db.session.rollback()
    
    return render_template('receitas/nova.html', user=user)


@prescriptions_bp.route('/<int:receita_id>')
@require_doctor
@log_action('view_prescription')
def visualizar(receita_id):
    """Visualiza receita específica"""
    user = session.get('usuario')
    user_type = session.get('usuario_tipo', 'medico')
    
    try:
        query = db.session.query(Receita).filter_by(id=receita_id)
        
        if user_type != 'admin':
            query = query.filter_by(medico=user)
        
        receita = query.first()
        
        if not receita:
            flash('Receita não encontrada', 'error')
            return redirect(url_for('prescriptions.index'))
        
        # Processar dados para exibição
        medicamentos = receita.medicamentos.split(',') if receita.medicamentos else []
        posologias = receita.posologias.split(',') if receita.posologias else []
        vias = receita.vias.split(',') if receita.vias else []
        duracoes = receita.duracoes.split(',') if receita.duracoes else []
        
        # Buscar dados do paciente
        paciente = db.session.query(Paciente).filter_by(nome=receita.nome_paciente).first()
        
        logger.info(f"Viewed prescription {receita_id}")
        
        return render_template('receitas/visualizar.html',
                             receita=receita,
                             paciente=paciente,
                             medicamentos=list(zip(medicamentos, posologias, vias, duracoes)),
                             user=user,
                             user_type=user_type)
                             
    except Exception as e:
        logger.error(f"Error viewing prescription {receita_id}: {str(e)}")
        flash('Erro ao carregar receita', 'error')
        return redirect(url_for('prescriptions.index'))


@prescriptions_bp.route('/<int:receita_id>/pdf')
@require_doctor
@log_action('generate_prescription_pdf')
def pdf(receita_id):
    """Gera PDF da receita"""
    user = session.get('usuario')
    user_type = session.get('usuario_tipo', 'medico')
    
    try:
        query = db.session.query(Receita).filter_by(id=receita_id)
        
        if user_type != 'admin':
            query = query.filter_by(medico=user)
        
        receita = query.first()
        
        if not receita:
            flash('Receita não encontrada', 'error')
            return redirect(url_for('prescriptions.index'))
        
        # Preparar dados para PDF
        prescription_data = {
            'nome_paciente': receita.nome_paciente,
            'medicamentos': receita.medicamentos.split(',') if receita.medicamentos else [],
            'posologias': receita.posologias.split(',') if receita.posologias else [],
            'vias': receita.vias.split(',') if receita.vias else [],
            'duracoes': receita.duracoes.split(',') if receita.duracoes else [],
            'observacoes': receita.observacoes or '',
            'medico_nome': receita.medico,
            'data': receita.data_criacao.strftime('%d/%m/%Y') if receita.data_criacao else datetime.now().strftime('%d/%m/%Y')
        }
        
        # Gerar PDF
        pdf_bytes = generate_prescription_pdf(prescription_data)
        
        # Criar resposta
        from flask import make_response
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=receita_{receita_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        logger.info(f"Generated PDF for prescription {receita_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating PDF for prescription {receita_id}: {str(e)}")
        flash('Erro ao gerar PDF', 'error')
        return redirect(url_for('prescriptions.visualizar', receita_id=receita_id))


@prescriptions_bp.route('/<int:receita_id>/editar', methods=['GET', 'POST'])
@require_doctor
@log_action('edit_prescription')
def editar(receita_id):
    """Edita receita existente"""
    user = session.get('usuario')
    user_type = session.get('usuario_tipo', 'medico')
    
    try:
        query = db.session.query(Receita).filter_by(id=receita_id)
        
        if user_type != 'admin':
            query = query.filter_by(medico=user)
        
        receita = query.first()
        
        if not receita:
            flash('Receita não encontrada', 'error')
            return redirect(url_for('prescriptions.index'))
        
        if request.method == 'POST':
            try:
                # Validar dados
                validator = get_validator('prescription')
                form_data = request.form.to_dict()
                
                # Processar listas
                medicamentos = []
                posologias = []
                vias = []
                duracoes = []
                
                for key, value in form_data.items():
                    if key.startswith('medicamento_') and value.strip():
                        idx = key.split('_')[1]
                        medicamentos.append(sanitize_input(value))
                        posologias.append(sanitize_input(form_data.get(f'posologia_{idx}', '')))
                        vias.append(sanitize_input(form_data.get(f'via_{idx}', 'oral')))
                        duracoes.append(sanitize_input(form_data.get(f'duracao_{idx}', '')))
                
                prescription_data = {
                    'nome_paciente': sanitize_input(form_data.get('nome_paciente', '')),
                    'medicamentos': medicamentos,
                    'posologias': posologias,
                    'vias': vias,
                    'duracoes': duracoes,
                    'observacoes': sanitize_input(form_data.get('observacoes', ''))
                }
                
                validated_data = validator.validate(prescription_data)
                
                # Atualizar receita
                receita.nome_paciente = validated_data['nome_paciente']
                receita.medicamentos = ','.join(validated_data['medicamentos'])
                receita.posologias = ','.join(validated_data['posologias'])
                receita.vias = ','.join(validated_data['vias'])
                receita.duracoes = ','.join(validated_data['duracoes'])
                receita.observacoes = validated_data.get('observacoes', '')
                
                db.session.commit()
                
                logger.info(f"Prescription {receita_id} updated")
                flash('Receita atualizada com sucesso!', 'success')
                
                return redirect(url_for('prescriptions.visualizar', receita_id=receita_id))
                
            except ValidationError as e:
                logger.warning(f"Prescription edit validation error: {e.message}")
                flash(f'Erro de validação: {e.message}', 'error')
            except Exception as e:
                logger.error(f"Error updating prescription {receita_id}: {str(e)}")
                flash('Erro ao atualizar receita', 'error')
                db.session.rollback()
        
        # Preparar dados para formulário
        medicamentos = receita.medicamentos.split(',') if receita.medicamentos else []
        posologias = receita.posologias.split(',') if receita.posologias else []
        vias = receita.vias.split(',') if receita.vias else []
        duracoes = receita.duracoes.split(',') if receita.duracoes else []
        
        return render_template('receitas/editar.html',
                             receita=receita,
                             medicamentos=list(zip(medicamentos, posologias, vias, duracoes)),
                             user=user)
                             
    except Exception as e:
        logger.error(f"Error editing prescription {receita_id}: {str(e)}")
        flash('Erro ao carregar receita para edição', 'error')
        return redirect(url_for('prescriptions.index'))


@prescriptions_bp.route('/api/pacientes')
@require_doctor
def api_pacientes():
    """API para autocomplete de pacientes"""
    try:
        query = request.args.get('q', '').strip()
        if not query or len(query) < 2:
            return jsonify([])
        
        query = sanitize_input(query)
        
        # Buscar pacientes
        pacientes = db.session.query(Paciente.nome).filter(
            Paciente.nome.ilike(f'%{query}%')
        ).limit(10).all()
        
        # Buscar também em receitas para nomes não cadastrados como pacientes
        receitas_nomes = db.session.query(Receita.nome_paciente).filter(
            Receita.nome_paciente.ilike(f'%{query}%')
        ).distinct().limit(10).all()
        
        # Combinar resultados
        nomes = set()
        for p in pacientes:
            nomes.add(p.nome)
        for r in receitas_nomes:
            nomes.add(r.nome_paciente)
        
        # Ordenar e limitar
        result = sorted(list(nomes))[:10]
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in patients API: {str(e)}")
        return jsonify([]), 500


@prescriptions_bp.route('/api/medicamentos')
@require_doctor
def api_medicamentos():
    """API para autocomplete de medicamentos"""
    try:
        query = request.args.get('q', '').strip()
        if not query or len(query) < 2:
            return jsonify([])
        
        query = sanitize_input(query)
        
        # Lista básica de medicamentos comuns
        medicamentos_comuns = [
            'Dipirona 500mg', 'Paracetamol 500mg', 'Ibuprofeno 400mg',
            'Amoxicilina 500mg', 'Azitromicina 500mg', 'Omeprazol 20mg',
            'Losartana 50mg', 'Atenolol 25mg', 'Sinvastatina 20mg',
            'Metformina 850mg', 'Captopril 25mg', 'Hidroclorotiazida 25mg',
            'Diclofenaco 50mg', 'Cefalexina 500mg', 'Prednisona 20mg'
        ]
        
        # Filtrar medicamentos que contêm a query
        result = [med for med in medicamentos_comuns if query.lower() in med.lower()]
        
        return jsonify(result[:10])
        
    except Exception as e:
        logger.error(f"Error in medications API: {str(e)}")
        return jsonify([]), 500


@prescriptions_bp.route('/<int:receita_id>/delete', methods=['POST'])
@require_doctor
@log_action('delete_prescription')
def delete(receita_id):
    """Exclui receita"""
    user = session.get('usuario')
    user_type = session.get('usuario_tipo', 'medico')
    
    try:
        query = db.session.query(Receita).filter_by(id=receita_id)
        
        if user_type != 'admin':
            query = query.filter_by(medico=user)
        
        receita = query.first()
        
        if not receita:
            flash('Receita não encontrada', 'error')
            return redirect(url_for('prescriptions.index'))
        
        db.session.delete(receita)
        db.session.commit()
        
        logger.info(f"Prescription {receita_id} deleted by {user}")
        flash('Receita excluída com sucesso!', 'success')
        
    except Exception as e:
        logger.error(f"Error deleting prescription {receita_id}: {str(e)}")
        flash('Erro ao excluir receita', 'error')
        db.session.rollback()
    
    return redirect(url_for('prescriptions.index'))