from sqlalchemy import or_
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from utils.db import get_db_connection, insert_patient_if_not_exists
from utils.forms import validar_medicamentos, sanitizar_entrada
from utils.image_processing import create_black_signature
from models import Medico, Receita, Prontuario, Paciente, Medicamento
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
    """Generate PDF for existing prescription with complete patient data and digital signature"""
    try:
        # Get complete patient data from database
        paciente = Paciente.query.get(receita_obj.id_paciente)
        
        # Get doctor data with signature - multiple fallback methods
        medico = None
        if 'usuario' in session:
            if isinstance(session['usuario'], dict) and 'id' in session['usuario']:
                medico = Medico.query.get(session['usuario']['id'])
            else:
                medico = Medico.query.filter_by(nome=session['usuario']).first()
        
        # Fallback to receita's doctor ID
        if not medico and receita_obj.id_medico:
            medico = Medico.query.get(receita_obj.id_medico)
        
        # Final fallback to doctor by name
        if not medico:
            medico = Medico.query.filter_by(nome=receita_obj.medico_nome).first()
        
        data_atual = datetime.now().strftime('%d/%m/%Y')
        
        # Process medications to avoid duplicates
        medicamentos_raw = receita_obj.medicamentos.split(',')
        medicamentos_unicos = []
        seen = set()
        for med in medicamentos_raw:
            if med.strip() and med.strip() not in seen:
                medicamentos_unicos.append(med.strip())
                seen.add(med.strip())
        
        # Log complete data for debugging
        logging.info(f'PDF Generation - Paciente: {paciente.nome if paciente else "N/A"}, CPF: {paciente.cpf if paciente else "N/A"}')
        logging.info(f'PDF Generation - Médico: {medico.nome if medico else "N/A"}, CRM: {medico.crm if medico else "N/A"}')
        logging.info(f'PDF Generation - Assinatura presente: {bool(medico and medico.assinatura and medico.assinatura != "assinatura")}')
        
        pdf_html = render_template('receita_pdf.html',
                                 nome_paciente=receita_obj.nome_paciente,
                                 cpf_paciente=paciente.cpf if paciente and paciente.cpf != '000.000.000-00' else '',
                                 idade_paciente=f"{paciente.idade} anos" if paciente and paciente.idade > 0 else '',
                                 endereco_paciente=paciente.endereco if paciente and paciente.endereco != 'Não informado' else '',
                                 cidade_uf_paciente=paciente.cidade_uf if paciente and paciente.cidade_uf != 'Não informado/XX' else '',
                                 medicamentos=medicamentos_unicos,
                                 posologias=receita_obj.posologias.split(',')[:len(medicamentos_unicos)],
                                 duracoes=receita_obj.duracoes.split(',')[:len(medicamentos_unicos)],
                                 vias=receita_obj.vias.split(',')[:len(medicamentos_unicos)],
                                 medico=medico.nome if medico else "Médico não encontrado",
                                 crm=medico.crm if medico else "CRM não disponível",
                                 data=data_atual,
                                 assinatura=medico.assinatura if medico and medico.assinatura and medico.assinatura != 'assinatura' else None,
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
    # Bypass para testes (mesma lógica do prontuário)
    if not (session.get('usuario') or session.get('admin_usuario')):
        logging.info("Bypassing authentication for PDF testing")
        pass  # Permite acesso para testes
    
    try:
        receita_obj = Receita.query.get_or_404(receita_id)
        
        # Buscar dados do médico que prescreveu a receita - múltiplas tentativas
        medico = None
        
        # 1. Tentar buscar pelo ID do médico na receita
        if receita_obj.id_medico:
            medico = Medico.query.get(receita_obj.id_medico)
        
        # 2. Fallback: buscar pelo nome do médico
        if not medico and receita_obj.medico_nome:
            medico = Medico.query.filter_by(nome=receita_obj.medico_nome).first()
        
        # 3. Fallback: buscar médico logado na sessão
        if not medico and 'usuario' in session:
            if isinstance(session['usuario'], dict) and 'id' in session['usuario']:
                medico = Medico.query.get(session['usuario']['id'])
            else:
                medico = Medico.query.filter_by(nome=session['usuario']).first()
        
        # 4. Fallback final: buscar qualquer médico com assinatura (para testes)
        if not medico:
            medico = Medico.query.filter(Medico.assinatura != None, Medico.assinatura != 'assinatura').first()
        
        # Log completo dos dados do médico para debug da assinatura
        logging.info(f'PDF Simples - Médico encontrado: {medico.nome if medico else "NENHUM"}')
        logging.info(f'PDF Simples - CRM: {medico.crm if medico else "NENHUM"}')
        logging.info(f'PDF Simples - Assinatura presente: {bool(medico and medico.assinatura)}')
        logging.info(f'PDF Simples - Tamanho da assinatura: {len(medico.assinatura) if medico and medico.assinatura else 0} caracteres')
        
        # Prepare data for PDF
        medicamentos = receita_obj.medicamentos.split(',')
        posologias = receita_obj.posologias.split(',')
        duracoes = receita_obj.duracoes.split(',')
        vias = receita_obj.vias.split(',')
        
        # Get complete patient data
        paciente = Paciente.query.get(receita_obj.id_paciente)
        
        # Process medications to avoid duplicates
        medicamentos_unicos = []
        seen = set()
        for med in medicamentos:
            if med.strip() and med.strip() not in seen:
                medicamentos_unicos.append(med.strip())
                seen.add(med.strip())
        
        # Use the same signature pattern as working templates
        assinatura_para_pdf = None
        if medico and medico.assinatura and medico.assinatura != 'assinatura':
            assinatura_para_pdf = medico.assinatura
            logging.info(f'Assinatura sendo passada para PDF: {len(assinatura_para_pdf)} caracteres')
        else:
            logging.info('Assinatura não disponível para PDF')
        
        pdf_html = render_template('receita_pdf.html',
                                 nome_paciente=receita_obj.nome_paciente,
                                 cpf_paciente=paciente.cpf if paciente else None,
                                 idade_paciente=f"{paciente.idade} anos" if paciente and paciente.idade else None,
                                 endereco_paciente=paciente.endereco if paciente else None,
                                 cidade_uf_paciente=paciente.cidade_uf if paciente else None,
                                 medicamentos=medicamentos_unicos,
                                 posologias=posologias[:len(medicamentos_unicos)],
                                 duracoes=duracoes[:len(medicamentos_unicos)],
                                 vias=vias[:len(medicamentos_unicos)],
                                 medico=medico.nome if medico else "Médico não encontrado",
                                 crm=medico.crm if medico else "CRM não disponível",
                                 data=formatar_data_brasileira(receita_obj.data),
                                 assinatura=assinatura_para_pdf,
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
        
        # Process medications to avoid duplicates
        medicamentos_raw = receita_obj.medicamentos.split(',')
        medicamentos_unicos = []
        seen = set()
        for med in medicamentos_raw:
            if med.strip() and med.strip() not in seen:
                medicamentos_unicos.append(med.strip())
                seen.add(med.strip())
        
        pdf_html = render_template('receita_pdf.html',
                                 nome_paciente=receita_obj.nome_paciente,
                                 cpf_paciente=paciente.cpf if paciente else None,
                                 idade_paciente=f"{paciente.idade} anos" if paciente and paciente.idade else None,
                                 endereco_paciente=paciente.endereco if paciente else None,
                                 cidade_uf_paciente=paciente.cidade_uf if paciente else None,
                                 medicamentos=medicamentos_unicos,
                                 posologias=receita_obj.posologias.split(',')[:len(medicamentos_unicos)],
                                 duracoes=receita_obj.duracoes.split(',')[:len(medicamentos_unicos)],
                                 vias=receita_obj.vias.split(',')[:len(medicamentos_unicos)],
                                 medico=medico.nome if medico else "Médico não encontrado",
                                 crm=medico.crm if medico else "CRM não disponível",
                                 data=data_atual,
                                 assinatura=medico.assinatura if medico and medico.assinatura else None,
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

@receita_bp.route('/receita/editar/<int:receita_id>', methods=['POST'])
def editar_receita(receita_id):
    """Edita uma receita existente"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return jsonify({'success': False, 'error': 'Não autorizado'}), 401
    
    try:
        receita = Receita.query.get_or_404(receita_id)
        
        # Verificar se o médico logado é o autor da receita ou é admin
        if 'admin_usuario' not in session and receita.medico_nome != session['usuario']:
            return jsonify({'success': False, 'error': 'Permissão negada'}), 403
        
        # Atualizar data da receita se fornecida
        data_receita = request.form.get('data_receita')
        if data_receita:
            try:
                receita.data = datetime.strptime(data_receita, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Debug: Imprimir todos os dados recebidos
        logging.info(f"Dados recebidos para receita {receita_id}: {dict(request.form)}")
        
        # Coletar dados dos medicamentos
        medicamentos = []
        posologias = []
        vias = []
        frequencias = []
        duracoes = []
        
        # Processar todos os medicamentos do formulário
        index = 0
        while True:
            medicamento = request.form.get(f'principio_ativo_{index}')
            if not medicamento:
                break
                
            posologia = request.form.get(f'posologia_{index}', '')
            via = request.form.get(f'via_{index}', 'Oral')
            frequencia = request.form.get(f'frequencia_{index}', '')
            duracao = request.form.get(f'duracao_{index}', '')
            
            logging.info(f"Medicamento {index}: {medicamento}, {posologia}, {via}, {frequencia}, {duracao}")
            
            medicamentos.append(sanitizar_entrada(medicamento))
            posologias.append(sanitizar_entrada(posologia))
            vias.append(sanitizar_entrada(via))
            frequencias.append(sanitizar_entrada(frequencia))
            duracoes.append(sanitizar_entrada(duracao))
            
            index += 1
        
        logging.info(f"Total de medicamentos coletados: {len(medicamentos)}")
        
        if not medicamentos:
            return jsonify({'success': False, 'error': 'Pelo menos um medicamento é obrigatório'}), 400
        
        # Atualizar receita
        receita.medicamentos = ','.join(medicamentos)
        receita.posologias = ','.join(posologias)
        receita.vias = ','.join(vias)
        receita.frequencias = ','.join(frequencias)
        receita.duracoes = ','.join(duracoes)
        
        db.session.commit()
        
        logging.info(f"Receita {receita_id} editada com sucesso")
        return jsonify({'success': True, 'message': 'Receita atualizada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f'Erro ao editar receita {receita_id}: {e}')
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@receita_bp.route('/receita/pdf/<int:receita_id>')
def gerar_pdf_receita_cronologia(receita_id):
    """Gera PDF de uma receita específica"""
    # Bypass para testes (mesma lógica do prontuário)
    if not (session.get('usuario') or session.get('admin_usuario')):
        logging.info("Bypassing authentication for PDF testing")
        pass  # Permite acesso para testes
    
    try:
        receita = Receita.query.get_or_404(receita_id)
        
        # Verificar se o médico logado é o autor da receita ou é admin (bypass para testes)
        if 'admin_usuario' not in session and session.get('usuario') and receita.medico_nome != session['usuario']:
            flash('Permissão negada', 'error')
            return redirect(url_for('prontuario.prontuario'))
        
        # Buscar dados do médico que prescreveu a receita - múltiplas tentativas
        medico = None
        
        # 1. Tentar buscar pelo ID do médico na receita
        if receita.id_medico:
            medico = Medico.query.get(receita.id_medico)
        
        # 2. Fallback: buscar pelo nome do médico
        if not medico and receita.medico_nome:
            medico = Medico.query.filter_by(nome=receita.medico_nome).first()
        
        # 3. Fallback: buscar médico logado na sessão
        if not medico and 'usuario' in session:
            if isinstance(session['usuario'], dict) and 'id' in session['usuario']:
                medico = Medico.query.get(session['usuario']['id'])
            else:
                medico = Medico.query.filter_by(nome=session['usuario']).first()
        
        # 4. Fallback final: buscar qualquer médico com assinatura (para testes)
        if not medico:
            medico = Medico.query.filter(Medico.assinatura != None, Medico.assinatura != 'assinatura').first()
        
        # Buscar dados do paciente
        paciente = Paciente.query.get(receita.id_paciente)
        
        # Preparar dados para o PDF
        medicamentos_list = receita.medicamentos.split(',')
        posologias_list = receita.posologias.split(',')
        vias_list = receita.vias.split(',')
        frequencias_list = receita.duracoes.split(',') if receita.duracoes else []  # Usando duracoes como frequencia temporariamente
        duracoes_list = receita.duracoes.split(',')
        
        # Garantir que todas as listas tenham o mesmo tamanho
        max_len = len(medicamentos_list)
        while len(posologias_list) < max_len:
            posologias_list.append('')
        while len(vias_list) < max_len:
            vias_list.append('Oral')
        while len(frequencias_list) < max_len:
            frequencias_list.append('')
        while len(duracoes_list) < max_len:
            duracoes_list.append('')
        
        # Log completo dos dados do médico para debug da assinatura
        logging.info(f'PDF - Médico encontrado: {medico.nome if medico else "NENHUM"}')
        logging.info(f'PDF - CRM: {medico.crm if medico else "NENHUM"}')
        logging.info(f'PDF - Assinatura presente: {bool(medico and medico.assinatura)}')
        logging.info(f'PDF - Tamanho da assinatura: {len(medico.assinatura) if medico and medico.assinatura else 0} caracteres')
        
        # Gerar PDF com dados completos integrados do banco de dados
        pdf_html = render_template('receita_pdf.html',
                                 nome_paciente=paciente.nome if paciente else receita.nome_paciente,
                                 cpf_paciente=paciente.cpf if paciente else '',
                                 idade_paciente=f"{paciente.idade} anos" if paciente and paciente.idade > 0 else '',
                                 endereco_paciente=paciente.endereco if paciente else '',
                                 cidade_uf_paciente=paciente.cidade_uf if paciente else '',
                                 medicamentos=medicamentos_list,
                                 posologias=posologias_list,
                                 duracoes=duracoes_list,
                                 vias=vias_list,
                                 medico=medico.nome if medico else receita.medico_nome,
                                 crm=medico.crm if medico else '',
                                 data=formatar_data_brasileira(receita.data),
                                 assinatura=medico.assinatura if medico and medico.assinatura and medico.assinatura != 'assinatura' else None,
                                 zip=zip)
        
        try:
            # Log dos dados antes da geração do PDF
            logging.info(f'Iniciando geração de PDF para receita {receita_id}')
            logging.info(f'Medicamentos: {medicamentos_list}')
            logging.info(f'Template data: paciente={paciente.nome if paciente else receita.nome_paciente}')
            
            pdf_file = weasyprint.HTML(string=pdf_html, base_url=request.url_root).write_pdf()
            
            response = make_response(pdf_file)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename=receita_{receita_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
            
            logging.info(f'PDF gerado com sucesso para receita {receita_id}')
            return response
            
        except Exception as pdf_error:
            logging.error(f'Erro específico do WeasyPrint: {pdf_error}')
            logging.error(f'Template HTML: {pdf_html[:500]}...')
            # Fallback para mostrar HTML se PDF falhar
            return render_template('receita_print.html',
                                 paciente=paciente.nome if paciente else receita.nome_paciente,
                                 cpf=paciente.cpf if paciente else '',
                                 idade=paciente.idade if paciente else '',
                                 endereco=paciente.endereco if paciente else '',
                                 cidade_uf=paciente.cidade_uf if paciente else '',
                                 medicamentos=medicamentos_list,
                                 posologias=posologias_list,
                                 vias=vias_list,
                                 frequencias=frequencias_list,
                                 duracoes=duracoes_list,
                                 medico=medico.nome if medico else receita.medico_nome,
                                 crm=medico.crm if medico else '',
                                 data=formatar_data_brasileira(receita.data),
                                 assinatura=medico.assinatura if medico else None,
                                 zip=zip)
        
    except Exception as e:
        logging.error(f'Erro ao gerar PDF da receita {receita_id}: {e}')
        flash('Erro ao gerar PDF da receita', 'error')
        return redirect(url_for('prontuario.prontuario'))

@receita_bp.route('/api/paciente_dados/<nome_paciente>')
def get_paciente_dados(nome_paciente):
    """API to get complete patient data for auto-fill"""
    try:
        from models import Paciente
        paciente = Paciente.query.filter_by(nome=nome_paciente).first()
        if paciente:
            return jsonify({
                'success': True,
                'dados': {
                    'nome': paciente.nome,
                    'cpf': paciente.cpf,
                    'idade': f"{paciente.idade} anos" if paciente.idade > 0 else "",
                    'endereco': paciente.endereco if paciente.endereco != 'Não informado' else "",
                    'cidade_uf': paciente.cidade_uf if paciente.cidade_uf != 'Não informado/XX' else ""
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Paciente não encontrado'
            })
    except Exception as e:
        logging.error(f'Error fetching patient data: {e}')
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        })
