from flask import Blueprint, render_template, redirect, url_for, flash, request, session, make_response
from models import FormularioAltoCusto, Medico, Paciente, Cid10
from app import db
from sqlalchemy import text
from utils.forms import sanitizar_entrada
from datetime import datetime
import logging
import weasyprint

formulario_alto_custo_bp = Blueprint('formulario_alto_custo', __name__)

@formulario_alto_custo_bp.route('/formulario_alto_custo', methods=['GET'])
def formulario_alto_custo():
    """Display high-cost SUS form"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    # Get last registered patient for auto-fill
    ultimo_paciente = session.get('ultimo_paciente', {})
    nome_paciente = ultimo_paciente.get('nome', '')
    
    return render_template('formulario_alto_custo.html', nome_paciente=nome_paciente)

@formulario_alto_custo_bp.route('/salvar_formulario_alto_custo', methods=['POST'])
def salvar_formulario_alto_custo():
    """Save high-cost SUS form and generate PDF"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get form data
        data = datetime.now().strftime('%Y-%m-%d')
        cnes = sanitizar_entrada(request.form.get('cnes', ''))
        estabelecimento = sanitizar_entrada(request.form.get('estabelecimento', ''))
        nome_paciente = sanitizar_entrada(request.form.get('nome_paciente', ''))
        nome_mae = sanitizar_entrada(request.form.get('nome_mae', ''))
        peso = sanitizar_entrada(request.form.get('peso', ''))
        altura = sanitizar_entrada(request.form.get('altura', ''))
        medicamento = sanitizar_entrada(request.form.get('medicamento', ''))
        quantidade = sanitizar_entrada(request.form.get('quantidade', ''))
        cid_codigo = sanitizar_entrada(request.form.get('cid_codigo', 'I10.0'))
        cid_descricao = sanitizar_entrada(request.form.get('cid_descricao', 'Hipertensão arterial'))
        anamnese = sanitizar_entrada(request.form.get('anamnese', ''))
        tratamento_previo = sanitizar_entrada(request.form.get('tratamento_previo', ''))
        incapaz = request.form.get('incapaz') == 'on'
        responsavel_nome = sanitizar_entrada(request.form.get('responsavel_nome', ''))
        medico_cns = sanitizar_entrada(request.form.get('medico_cns', ''))
        
        if not all([medicamento, quantidade, anamnese]):
            flash('Medicamento, quantidade e anamnese são obrigatórios.', 'error')
            return redirect(url_for('formulario_alto_custo.formulario_alto_custo'))
        
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
            return redirect(url_for('formulario_alto_custo.formulario_alto_custo'))
        
        # Get or create patient
        from utils.db import insert_patient_if_not_exists
        paciente_id = insert_patient_if_not_exists(nome_paciente)
        
        # Create high-cost form using SQL insert
        db.session.execute(
            text("""
            INSERT INTO formularios_alto_custo 
            (cnes, estabelecimento, nome_paciente, nome_mae, peso, altura, medicamento, quantidade, 
             cid_codigo, cid_descricao, anamnese, tratamento_previo, incapaz, responsavel_nome, 
             medico_nome, medico_cns, data, id_paciente, id_medico, created_at)
            VALUES (:cnes, :estabelecimento, :nome_paciente, :nome_mae, :peso, :altura, :medicamento, :quantidade,
                    :cid_codigo, :cid_descricao, :anamnese, :tratamento_previo, :incapaz, :responsavel_nome,
                    :medico_nome, :medico_cns, :data, :id_paciente, :id_medico, :created_at)
            """),
            {
                'cnes': cnes,
                'estabelecimento': estabelecimento,
                'nome_paciente': nome_paciente,
                'nome_mae': nome_mae,
                'peso': peso,
                'altura': altura,
                'medicamento': medicamento,
                'quantidade': quantidade,
                'cid_codigo': cid_codigo,
                'cid_descricao': cid_descricao,
                'anamnese': anamnese,
                'tratamento_previo': tratamento_previo,
                'incapaz': incapaz,
                'responsavel_nome': responsavel_nome,
                'medico_nome': medico.nome,
                'medico_cns': medico_cns,
                'data': data,
                'id_paciente': paciente_id,
                'id_medico': medico.id,
                'created_at': datetime.now()
            }
        )
        
        # Get the ID of the inserted record
        result = db.session.execute(text("SELECT lastval()"))
        formulario_id = result.scalar()
        db.session.commit()
        
        # Generate PDF
        pdf_html = render_template('formulario_alto_custo_pdf.html',
                                 cnes=cnes,
                                 estabelecimento=estabelecimento,
                                 nome_paciente=nome_paciente,
                                 nome_mae=nome_mae,
                                 peso=peso,
                                 altura=altura,
                                 medicamento=medicamento,
                                 quantidade=quantidade,
                                 cid_codigo=cid_codigo,
                                 cid_descricao=cid_descricao,
                                 anamnese=anamnese,
                                 tratamento_previo=tratamento_previo,
                                 incapaz=incapaz,
                                 responsavel_nome=responsavel_nome,
                                 medico=medico.nome if medico else "Médico não encontrado",
                                 crm=medico.crm if medico else "CRM não disponível",
                                 medico_cns=medico_cns,
                                 assinatura=medico.assinatura if medico else None,
                                 data=datetime.now().strftime('%d/%m/%Y'))
        
        pdf_file = weasyprint.HTML(string=pdf_html).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=formulario_alto_custo_{nome_paciente}_{data}.pdf'
        
        flash('Formulário de alto custo salvo e PDF gerado com sucesso!', 'success')
        logging.info(f'High-cost form created for patient: {nome_paciente}')
        
        return response
        
    except Exception as e:
        logging.error(f'High-cost form error: {e}')
        flash('Erro ao salvar formulário. Tente novamente.', 'error')
        return redirect(url_for('formulario_alto_custo.formulario_alto_custo'))