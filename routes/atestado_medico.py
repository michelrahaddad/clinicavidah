from flask import Blueprint, render_template, redirect, url_for, flash, request, session, make_response
from models import AtestadoMedico, Medico, Paciente, Cid10
from main import db
from sqlalchemy import text
from utils.forms import sanitizar_entrada
from datetime import datetime, timedelta
import logging
import weasyprint

atestado_medico_bp = Blueprint('atestado_medico', __name__)

@atestado_medico_bp.route('/atestado_medico', methods=['GET'])
def atestado_medico():
    """Display medical certificate form"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    # Get last registered patient for auto-fill
    ultimo_paciente = session.get('ultimo_paciente', {})
    nome_paciente = ultimo_paciente.get('nome', '')
    
    # Current date for auto-fill
    data_atual = datetime.now().strftime('%d/%m/%Y')
    
    return render_template('atestado_medico.html', 
                         nome_paciente=nome_paciente,
                         data_atual=data_atual)

@atestado_medico_bp.route('/salvar_atestado_medico', methods=['POST'])
def salvar_atestado_medico():
    """Save medical certificate and generate PDF"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get form data
        data = datetime.now().strftime('%Y-%m-%d')
        nome_paciente = sanitizar_entrada(request.form.get('nome_paciente', ''))
        cid_codigo = sanitizar_entrada(request.form.get('cid_codigo', ''))
        cid_descricao = sanitizar_entrada(request.form.get('cid_descricao', ''))
        dias_afastamento = int(request.form.get('dias_afastamento', 1))
        data_inicio = sanitizar_entrada(request.form.get('data_inicio', ''))
        
        if not all([nome_paciente, dias_afastamento, data_inicio]):
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return redirect(url_for('atestado_medico.atestado_medico'))
        
        # Calculate end date
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        fim = inicio + timedelta(days=dias_afastamento - 1)
        data_fim = fim.strftime('%Y-%m-%d')
        
        # Get medico ID safely
        usuario_data = session['usuario']
        if isinstance(usuario_data, dict):
            medico_id = usuario_data.get('id')
        else:
            # Fallback - find medico by name
            medico = Medico.query.filter_by(nome=str(usuario_data)).first()
            medico_id = medico.id if medico else 1
        
        medico = Medico.query.get(medico_id)
        if not medico:
            flash('Médico não encontrado.', 'error')
            return redirect(url_for('atestado_medico.atestado_medico'))
        
        # Get or create patient
        from utils.db import insert_patient_if_not_exists
        paciente_id = insert_patient_if_not_exists(nome_paciente)
        
        # Create medical certificate using SQL insert
        db.session.execute(
            text("""
            INSERT INTO atestados_medicos 
            (nome_paciente, cid_codigo, cid_descricao, dias_afastamento, data_inicio, data_fim, medico_nome, data, id_paciente, id_medico, created_at)
            VALUES (:nome_paciente, :cid_codigo, :cid_descricao, :dias_afastamento, :data_inicio, :data_fim, :medico_nome, :data, :id_paciente, :id_medico, :created_at)
            """),
            {
                'nome_paciente': nome_paciente,
                'cid_codigo': cid_codigo,
                'cid_descricao': cid_descricao,
                'dias_afastamento': dias_afastamento,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'medico_nome': medico.nome,
                'data': data,
                'id_paciente': paciente_id,
                'id_medico': medico.id,
                'created_at': datetime.now()
            }
        )
        
        # Get the ID of the inserted record
        result = db.session.execute(text("SELECT lastval()"))
        atestado_id = result.scalar()
        db.session.commit()
        
        # Generate PDF
        pdf_html = render_template('atestado_medico_pdf.html',
                                 nome_paciente=nome_paciente,
                                 cid_codigo=cid_codigo,
                                 cid_descricao=cid_descricao,
                                 dias_afastamento=dias_afastamento,
                                 data_inicio=inicio.strftime('%d/%m/%Y'),
                                 data_fim=fim.strftime('%d/%m/%Y'),
                                 medico=medico.nome if medico else "Médico não encontrado",
                                 crm=medico.crm if medico else "CRM não disponível",
                                 assinatura=medico.assinatura if medico else None,
                                 data=datetime.now().strftime('%d/%m/%Y'))
        
        pdf_file = weasyprint.HTML(string=pdf_html, base_url=request.url_root).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=atestado_medico_{nome_paciente}_{data}.pdf'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        flash('Atestado médico salvo e PDF gerado com sucesso!', 'success')
        logging.info(f'Medical certificate created for patient: {nome_paciente}')
        
        return response
        
    except Exception as e:
        logging.error(f'Medical certificate error: {e}')
        flash('Erro ao salvar atestado. Tente novamente.', 'error')
        return redirect(url_for('atestado_medico.atestado_medico'))