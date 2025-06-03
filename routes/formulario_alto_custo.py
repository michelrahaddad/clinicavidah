from flask import Blueprint, render_template, redirect, url_for, flash, request, session, make_response
from models import FormularioAltoCusto, Medico, Paciente, Cid10
from app import db
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
        
        if not all([nome_paciente, nome_mae, peso, altura, medicamento, quantidade, anamnese]):
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return redirect(url_for('formulario_alto_custo.formulario_alto_custo'))
        
        # Get doctor info
        medico = Medico.query.filter_by(nome=session['usuario']).first()
        if not medico:
            flash('Médico não encontrado.', 'error')
            return redirect(url_for('formulario_alto_custo.formulario_alto_custo'))
        
        # Get or create patient
        from utils.db import insert_patient_if_not_exists
        paciente_id = insert_patient_if_not_exists(nome_paciente)
        
        # Create high-cost form
        formulario = FormularioAltoCusto()
        formulario.cnes = cnes
        formulario.estabelecimento = estabelecimento
        formulario.nome_paciente = nome_paciente
        formulario.nome_mae = nome_mae
        formulario.peso = peso
        formulario.altura = altura
        formulario.medicamento = medicamento
        formulario.quantidade = quantidade
        formulario.cid_codigo = cid_codigo
        formulario.cid_descricao = cid_descricao
        formulario.anamnese = anamnese
        formulario.tratamento_previo = tratamento_previo
        formulario.incapaz = incapaz
        formulario.responsavel_nome = responsavel_nome
        formulario.medico_nome = medico.nome
        formulario.medico_cns = medico_cns
        formulario.data = data
        formulario.id_paciente = paciente_id
        formulario.id_medico = medico.id
        
        db.session.add(formulario)
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
                                 medico=medico.nome,
                                 crm=medico.crm,
                                 medico_cns=medico_cns,
                                 assinatura=medico.assinatura,
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