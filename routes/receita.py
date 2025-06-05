from sqlalchemy import or_
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from utils.db import get_db_connection, insert_patient_if_not_exists
from utils.forms import validar_medicamentos, sanitizar_entrada
from utils.image_processing import create_black_signature
from models import Medico, Receita, Prontuario, Paciente, Medicamento
from utils.forms import sanitizar_entrada
from app import db
from datetime import datetime
import logging
import weasyprint

def formatar_data_brasileira(data):
    """Converte data para o formato brasileiro DD/MM/AAAA"""
    if isinstance(data, str):
        try:
            # Tenta converter string para datetime
            if '-' in data:
                data_obj = datetime.strptime(data, '%Y-%m-%d')
            else:
                return data  # Já está no formato brasileiro
        except:
            return data
    elif isinstance(data, datetime):
        data_obj = data
    else:
        try:
            data_obj = datetime.strptime(str(data), '%Y-%m-%d')
        except:
            return str(data)
    
    return data_obj.strftime('%d/%m/%Y')

def sanitizar_entrada(valor):
    """Sanitiza entrada de usuário"""
    if not valor:
        return ""
    
    # Remove caracteres perigosos
    import re
    valor = re.sub(r'[<>"\']', '', str(valor))
    return valor.strip()


def salvar_medicamentos_historico(principios_ativos, concentracoes, vias, frequencias, quantidades, medico_id):
    """Salva medicamentos no histórico para autocomplete inteligente"""
    from datetime import datetime
    
    for i in range(len(principios_ativos)):
        principio = principios_ativos[i].strip().lower()
        concentracao = concentracoes[i] if i < len(concentracoes) else ''
        via = vias[i] if i < len(vias) else ''
        frequencia = frequencias[i] if i < len(frequencias) else ''
        quantidade = quantidades[i] if i < len(quantidades) else ''
        
        if not principio:
            continue
            
        # Verificar se já existe este medicamento para este médico
        try:
            from sqlalchemy import text
            # Usar SQL direto para melhor performance
            existing = db.session.execute(
                text("SELECT id, vezes_prescrito FROM medicamentos_historico WHERE principio_ativo = :principio AND id_medico = :medico_id AND concentracao = :concentracao AND via = :via"),
                {'principio': principio, 'medico_id': medico_id, 'concentracao': concentracao, 'via': via}
            ).fetchone()
            
            if existing:
                # Atualizar contagem e data
                db.session.execute(
                    text("UPDATE medicamentos_historico SET vezes_prescrito = :vezes, ultima_prescricao = :data WHERE id = :id"),
                    {'vezes': existing[1] + 1, 'data': datetime.now(), 'id': existing[0]}
                )
            else:
                # Inserir novo registro
                db.session.execute(
                    text("INSERT INTO medicamentos_historico (principio_ativo, concentracao, via, frequencia, quantidade, vezes_prescrito, ultima_prescricao, created_at, id_medico) VALUES (:principio, :concentracao, :via, :frequencia, :quantidade, :vezes, :ultima, :created, :medico_id)"),
                    {
                        'principio': principio, 
                        'concentracao': concentracao, 
                        'via': via, 
                        'frequencia': frequencia, 
                        'quantidade': quantidade, 
                        'vezes': 1, 
                        'ultima': datetime.now(), 
                        'created': datetime.now(), 
                        'medico_id': medico_id
                    }
                )
        except Exception as e:
            logging.error(f"Erro ao salvar medicamento no histórico: {e}")
            continue


receita_bp = Blueprint('receita', __name__)

@receita_bp.route('/receita', methods=['GET'])
def receita():
    """Display prescription form"""
    if 'usuario' not in session and 'admin_usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    # Get last registered patient for auto-fill
    ultimo_paciente = session.get('ultimo_paciente', {})
    nome_paciente = ultimo_paciente.get('nome', '')
    
    return render_template('receita.html', nome_paciente=nome_paciente)

@receita_bp.route('/salvar_receita', methods=['POST'])
def salvar_receita():
    """Save prescription and generate PDF"""
    if 'usuario' not in session and 'admin_usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get form data with new field structure
        data = datetime.now().strftime('%Y-%m-%d')
        nome_paciente = sanitizar_entrada(request.form.get('nome_paciente', ''))
        cpf = sanitizar_entrada(request.form.get('cpf', ''))
        idade = sanitizar_entrada(request.form.get('idade', ''))
        endereco = sanitizar_entrada(request.form.get('endereco', ''))
        cidade = sanitizar_entrada(request.form.get('cidade', ''))
        
        # Get new medication fields
        principios_ativos = [sanitizar_entrada(m) for m in request.form.getlist('principio_ativo[]') if m.strip()]
        concentracoes = [sanitizar_entrada(c) for c in request.form.getlist('concentracao[]') if c.strip()]
        vias = [sanitizar_entrada(v) for v in request.form.getlist('via[]') if v.strip()]
        frequencias = [sanitizar_entrada(f) for f in request.form.getlist('frequencia[]') if f.strip()]
        quantidades = [sanitizar_entrada(q) for q in request.form.getlist('quantidade[]') if q.strip()]
        
        # Validation
        if not nome_paciente:
            flash('Nome do paciente é obrigatório.', 'error')
            return render_template('receita.html')
        
        # Validate medications with new structure
        if not principios_ativos or len(principios_ativos) == 0:
            flash('É necessário pelo menos um medicamento.', 'error')
            return render_template('receita.html')
        
        # Check if all medication fields are filled
        min_length = len(principios_ativos)
        if not (len(concentracoes) >= min_length and len(vias) >= min_length and 
                len(frequencias) >= min_length and len(quantidades) >= min_length):
            flash('Todos os campos de medicamento devem ser preenchidos.', 'error')
            return render_template('receita.html')
        
        # Combine medication data for storage
        medicamentos_completos = []
        for i in range(min_length):
            if (i < len(principios_ativos) and i < len(concentracoes) and 
                i < len(vias) and i < len(frequencias) and i < len(quantidades)):
                medicamento = f"{principios_ativos[i]} {concentracoes[i]} - {vias[i]} - {frequencias[i]} - {quantidades[i]}"
                medicamentos_completos.append(medicamento)
        
        if not medicamentos_completos:
            flash('É necessário pelo menos um medicamento completo.', 'error')
            return render_template('receita.html')
        
        # Insert patient if not exists
        paciente_id = insert_patient_if_not_exists(nome_paciente)
        
        # Get complete patient data for PDF
        paciente = Paciente.query.get(paciente_id)
        
        # Get medico ID safely
        usuario_data = session['usuario']
        if isinstance(usuario_data, dict):
            medico_id = usuario_data.get('id')
        else:
            # Fallback - find medico by name
            medico = Medico.query.filter_by(nome=str(usuario_data)).first()
            medico_id = medico.id if medico else 1
        
        medico = Medico.query.get(medico_id)
        
        receita_obj = Receita(
            nome_paciente=nome_paciente,
            medicamentos=','.join(medicamentos_completos),
            posologias=','.join(frequencias),  # Store frequencies as posologies
            duracoes=','.join(['Conforme prescrição'] * len(medicamentos_completos)),  # Default duration
            vias=','.join(vias),
            medico_nome=medico.nome if medico else 'Médico Sistema',
            data=data,
            id_paciente=paciente_id,
            id_medico=medico_id
        )
        
        db.session.add(receita_obj)
        db.session.flush()
        
        # Add to prontuario
        prontuario = Prontuario(
            tipo='receita',
            id_registro=receita_obj.id,
            id_paciente=paciente_id,
            id_medico=medico_id,
            data=data
        )
        
        db.session.add(prontuario)
        
        # Save medications to intelligent history for future autocomplete
        salvar_medicamentos_historico(principios_ativos, concentracoes, vias, frequencias, quantidades, medico_id)
        
        db.session.commit()
        
        # Generate PDF
        try:
            logging.info(f'Starting PDF generation for prescription: {nome_paciente}')
            
            # Generate PDF directly using WeasyPrint
            pdf_html = render_template('receita_pdf.html',
                                     nome_paciente=nome_paciente,
                                     cpf_paciente=cpf if cpf else '000.000.000-00',
                                     idade_paciente=f"{idade} anos" if idade else 'Não informado',
                                     endereco_paciente=endereco if endereco else 'Não informado',
                                     cidade_uf_paciente=cidade if cidade else 'XX',
                                     medicamentos=medicamentos_completos,
                                     posologias=frequencias,
                                     duracoes=['Conforme prescrição'] * len(medicamentos_completos),
                                     vias=vias,
                                     medico=medico.nome if medico else "Médico não encontrado",
                                     crm=medico.crm if medico else "CRM não disponível",
                                     assinatura=create_black_signature(medico.assinatura) if medico and medico.assinatura else None,
                                     data=formatar_data_brasileira(data),
                                     zip=zip)
            
            logging.info('HTML template rendered successfully')
            
            # Generate PDF directly and return as response to avoid session size limit
            html_doc = weasyprint.HTML(string=pdf_html, base_url=request.url_root)
            pdf_file = html_doc.write_pdf()
            logging.info('PDF file generated successfully')
            
            response = make_response(pdf_file)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=receita_{nome_paciente.replace(" ", "_")}_{data}.pdf'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            flash('Receita salva e PDF gerado com sucesso!', 'success')
            logging.info(f'Prescription created for patient: {nome_paciente}')
            
            return response
            
        except Exception as pdf_error:
            logging.error(f'PDF generation error: {pdf_error}')
            # If PDF generation fails, redirect with success message for data saving
            flash('Receita salva com sucesso! Erro na geração do PDF - verifique os dados.', 'warning')
            return redirect(url_for('receita.receita'))
        
    except Exception as e:
        logging.error(f'Prescription error: {e}')
        flash('Erro ao salvar receita. Tente novamente.', 'error')
        return render_template('receita.html')

@receita_bp.route('/receita/refazer/<int:id>', methods=['GET'])
def refazer_receita(id):
    """Refill prescription from prontuario"""
    if 'usuario' not in session and 'admin_usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        receita_obj = Receita.query.get_or_404(id)
        
        # Check if this is a PDF generation request
        if request.args.get('print') == '1':
            return gerar_pdf_reimprimir_receita(receita_obj)
        
        medicamentos = receita_obj.medicamentos.split(',')
        posologias = receita_obj.posologias.split(',')
        duracoes = receita_obj.duracoes.split(',')
        vias = receita_obj.vias.split(',')
        
        return render_template('receita.html',
                             receita={
                                 'nome_paciente': receita_obj.nome_paciente,
                                 'medicamentos': [{'nome': m, 'posologia': p, 'duracao': d, 'via': v} 
                                                for m, p, d, v in zip(medicamentos, posologias, duracoes, vias)]
                             },
                             refazer=True)
    except Exception as e:
        logging.error(f'Refill prescription error: {e}')
        flash('Erro ao carregar receita.', 'error')
        return render_template('receita.html')

def gerar_pdf_reimprimir_receita(receita_obj):
    """Generate PDF for existing prescription with current date"""
    try:
        medico = Medico.query.get(session['usuario']['id'])
        data_atual = datetime.now().strftime('%d/%m/%Y')
        
        # Get complete patient data
        paciente = Paciente.query.get(receita_obj.id_paciente)
        
        pdf_html = render_template('receita_pdf.html',
                                 nome_paciente=receita_obj.nome_paciente,
                                 cpf_paciente=paciente.cpf if paciente else None,
                                 idade_paciente=f"{paciente.idade} anos" if paciente and paciente.idade else None,
                                 endereco_paciente=paciente.endereco if paciente else None,
                                 cidade_uf_paciente=paciente.cidade_uf if paciente else None,
                                 medicamentos=receita_obj.medicamentos.split(','),
                                 posologias=receita_obj.posologias.split(','),
                                 duracoes=receita_obj.duracoes.split(','),
                                 vias=receita_obj.vias.split(','),
                                 medico=medico.nome if medico else "Médico não encontrado",
                                 crm=medico.crm if medico else "CRM não disponível",
                                 data=data_atual,
                                 assinatura=medico.assinatura if medico else None,
                                 zip=zip)
        
        pdf_file = weasyprint.HTML(string=pdf_html, base_url=request.url_root).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=receita_{receita_obj.nome_paciente}_{datetime.now().strftime("%Y%m%d")}.pdf'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        logging.error(f'Error generating prescription PDF: {e}')
        flash('Erro ao gerar PDF da receita.', 'error')
        return render_template('receita.html')


@receita_bp.route('/gerar_pdf_receita/<int:receita_id>')
def gerar_pdf_receita(receita_id):
    """Generate and serve prescription PDF via GET request"""
    if 'usuario' not in session and 'admin_usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        receita_obj = Receita.query.get_or_404(receita_id)
        medico = Medico.query.get(receita_obj.id_medico)
        
        # Prepare data for PDF
        medicamentos = receita_obj.medicamentos.split(',')
        posologias = receita_obj.posologias.split(',')
        duracoes = receita_obj.duracoes.split(',')
        vias = receita_obj.vias.split(',')
        
        # Generate PDF
        pdf_html = render_template('receita_pdf.html',
                                 paciente=receita_obj.nome_paciente,
                                 medicamentos=medicamentos,
                                 posologias=posologias,
                                 duracoes=duracoes,
                                 vias=vias,
                                 medico=medico.nome if medico else "Médico não encontrado",
                                 crm=medico.crm if medico else "CRM não disponível",
                                 data=formatar_data_brasileira(receita_obj.data),
                                 assinatura=medico.assinatura if medico else None,
                                 zip=zip)
        
        pdf_file = weasyprint.HTML(string=pdf_html, base_url=request.url_root).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=receita_{receita_obj.nome_paciente.replace(" ", "_")}_{receita_obj.data}.pdf'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        logging.error(f'Error generating prescription PDF: {e}')
        flash('Erro ao gerar PDF da receita.', 'error')
        return render_template('receita.html')

@receita_bp.route('/receita/reimprimir/<int:receita_id>')
def reimprimir_receita(receita_id):
    """Generate PDF for existing prescription with current date"""
    if 'usuario' not in session and 'admin_usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get current doctor ID from session
        medico_id = session.get('medico_id')
        if not medico_id:
            flash('Sessão expirada. Faça login novamente.', 'error')
            return render_template('receita.html')
        
        # Get prescription and verify ownership
        receita_obj = db.session.query(Receita).filter_by(id=receita_id, id_medico=medico_id).first()
        if not receita_obj:
            flash('Receita não encontrada.', 'error')
            return render_template('receita.html')
        
        medico = db.session.query(Medico).get(medico_id)
        data_atual = datetime.now().strftime('%d/%m/%Y')
        
        # Get complete patient data
        paciente = db.session.query(Paciente).get(receita_obj.id_paciente)
        
        pdf_html = render_template('receita_pdf.html',
                                 paciente=receita_obj.nome_paciente,
                                 medicamentos=receita_obj.medicamentos.split(','),
                                 posologias=receita_obj.posologias.split(','),
                                 duracoes=receita_obj.duracoes.split(','),
                                 vias=receita_obj.vias.split(','),
                                 medico=medico.nome if medico else "Médico não encontrado",
                                 crm=medico.crm if medico else "CRM não disponível",
                                 data=data_atual,
                                 assinatura=medico.assinatura if medico else None,
                                 zip=zip)
        
        pdf_file = weasyprint.HTML(string=pdf_html, base_url=request.url_root).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=receita_reimpressao_{receita_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
        
        return response
    except Exception as e:
        logging.error(f'Reprint prescription error: {e}')
        flash('Erro ao reimprimir receita.', 'error')
        return render_template('receita.html')
@receita_bp.route('/refazer_receita/<int:id>')
def refazer_receita_novo(id):
    """Refaz uma receita existente usando novo nome de função"""
    if 'usuario' not in session and 'admin_usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        receita = Receita.query.get_or_404(id)
        
        # Verificar se o médico logado é o autor da receita
        if receita.medico_nome != session['usuario']:
            flash('Você não tem permissão para refazer esta receita.', 'error')
            return render_template('receita.html')
        
        # Redirecionar para a página de receita com dados preenchidos
        return redirect(url_for('receita.receita', 
                               paciente_id=receita.id_paciente,
                               medicamentos=receita.medicamentos,
                               posologias=receita.posologias,
                               duracoes=receita.duracoes,
                               vias=receita.vias))
                               
    except Exception as e:
        logging.error(f'Erro ao refazer receita {id}: {e}')
        flash('Erro ao carregar receita para refazer.', 'error')
        return render_template('receita.html')


@receita_bp.route('/api/medicamentos')
def get_medicamentos():
    """API para buscar medicamentos - funciona para médicos e administradores"""
    if 'usuario' not in session and 'admin_usuario' not in session and 'admin_usuario' not in session:
        return jsonify([])
    
    try:
        term = request.args.get('q', '').strip()
        if len(term) < 2:
            return jsonify([])
        
        # Buscar medicamentos cadastrados
        medicamentos = Medicamento.query.filter(
            Medicamento.nome.ilike(f'%{term}%')
        ).limit(10).all()
        
        result = []
        for m in medicamentos:
            result.append({
                'id': m.id,
                'nome': m.nome
            })
        
        return jsonify(result)
    except Exception as e:
        print(f"Erro na API de medicamentos: {e}")
        return jsonify([])

@receita_bp.route('/api/pacientes')
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
        print(f"Erro na API de pacientes: {e}")
        return jsonify([])
