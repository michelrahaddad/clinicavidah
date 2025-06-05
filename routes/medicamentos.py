from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, make_response
from models import db, Receita, Medico, Paciente
import logging
from datetime import datetime
import os
import html
import weasyprint
from io import BytesIO

medicamentos_bp = Blueprint('medicamentos', __name__)

def sanitizar_entrada(texto):
    """Sanitize user input"""
    if not texto:
        return ""
    return html.escape(str(texto).strip())

def generate_pdf_response(html_content, filename):
    """Generate PDF response from HTML content"""
    try:
        # Create PDF from HTML
        pdf_buffer = BytesIO()
        html_doc = weasyprint.HTML(string=html_content)
        html_doc.write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        
        # Create response
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
        
        return response
    except Exception as e:
        logging.error(f'Error generating PDF: {e}')
        flash('Erro ao gerar PDF.', 'error')
        return redirect(url_for('prontuario.prontuario'))

@medicamentos_bp.route('/prontuario/medicamentos/<int:receita_id>')
def prontuario_medicamentos(receita_id):
    """Display specific medication prescription with pre-filled data for editing"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get current doctor ID from session, handle admin users
        medico_id = session.get('medico_id')
        admin_data = session.get('admin_data')
        
        # If admin user, get first available doctor ID
        if not medico_id and (admin_data or 'admin_usuario' in session):
            primeiro_medico = db.session.query(Medico).first()
            if primeiro_medico:
                medico_id = primeiro_medico.id
            else:
                medico_id = 1
        
        # Get the specific prescription
        receita = db.session.query(Receita).filter_by(id=receita_id).first()
        if not receita:
            flash('Receita não encontrada.', 'error')
            return redirect(url_for('prontuario.prontuario'))
        
        # Get doctor information
        medico = db.session.query(Medico).filter_by(id=receita.id_medico).first()
        
        # Parse medications from the prescription
        medicamentos_list = []
        if receita.medicamentos:
            medicamentos_raw = receita.medicamentos.split('\n')
            for i, med in enumerate(medicamentos_raw):
                if med.strip():
                    # Try to parse the medication format: "principio concentracao - via - frequencia - quantidade"
                    parts = med.strip().split(' - ')
                    if len(parts) >= 4:
                        # Extract nome and concentracao from first part
                        nome_conc = parts[0].strip()
                        nome_parts = nome_conc.split(' ')
                        if len(nome_parts) >= 2:
                            principio_ativo = ' '.join(nome_parts[:-1])
                            concentracao = nome_parts[-1]
                        else:
                            principio_ativo = nome_conc
                            concentracao = '500mg'
                        
                        medicamentos_list.append({
                            'index': i,
                            'principio_ativo': principio_ativo,
                            'concentracao': concentracao,
                            'via': parts[1].strip() if len(parts) > 1 else 'Oral',
                            'frequencia': parts[2].strip() if len(parts) > 2 else '2x',
                            'quantidade': parts[3].strip() if len(parts) > 3 else '30 comprimidos'
                        })
                    else:
                        # Fallback for malformed entries
                        medicamentos_list.append({
                            'index': i,
                            'principio_ativo': med.strip(),
                            'concentracao': '500mg',
                            'via': 'Oral',
                            'frequencia': '2x',
                            'quantidade': '30 comprimidos'
                        })
        
        # If no medications found, add a default one
        if not medicamentos_list:
            medicamentos_list.append({
                'index': 0,
                'principio_ativo': 'Dipirona',
                'concentracao': '500mg',
                'via': 'Oral',
                'frequencia': '2x',
                'quantidade': '30 comprimidos'
            })
        
        # Get patient information
        paciente_data = {
            'nome': receita.nome_paciente or '',
            'cpf': getattr(receita, 'cpf', '') or '',
            'idade': getattr(receita, 'idade', '') or '',
            'endereco': getattr(receita, 'endereco', '') or '',
            'cidade': getattr(receita, 'cidade_uf', '') or ''
        }
        
        return render_template('prontuario_medicamentos.html',
                             receita=receita,
                             medico=medico,
                             medicamentos=medicamentos_list,
                             paciente=paciente_data,
                             data_formatada=receita.data.strftime('%d/%m/%Y') if receita.data else datetime.now().strftime('%d/%m/%Y'))
        
    except Exception as e:
        logging.error(f'Error displaying medication page: {e}')
        flash('Erro ao carregar página de medicamentos.', 'error')
        return redirect(url_for('prontuario.prontuario'))

@medicamentos_bp.route('/prontuario/medicamentos/<int:receita_id>/salvar', methods=['POST'])
def salvar_medicamentos(receita_id):
    """Save edited medication prescription"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get current doctor ID from session
        medico_id = session.get('medico_id')
        admin_data = session.get('admin_data')
        
        if not medico_id and (admin_data or 'admin_usuario' in session):
            primeiro_medico = db.session.query(Medico).first()
            if primeiro_medico:
                medico_id = primeiro_medico.id
            else:
                medico_id = 1
        
        # Get the prescription
        receita = db.session.query(Receita).filter_by(id=receita_id).first()
        if not receita:
            return jsonify({'success': False, 'error': 'Receita não encontrada'})
        
        # Get form data
        nome_paciente = sanitizar_entrada(request.form.get('nome_paciente', ''))
        
        # Get medication data
        principios_ativos = [sanitizar_entrada(p) for p in request.form.getlist('principio_ativo[]') if p.strip()]
        concentracoes = [sanitizar_entrada(c) for c in request.form.getlist('concentracao[]') if c.strip()]
        vias = [sanitizar_entrada(v) for v in request.form.getlist('via[]') if v.strip()]
        frequencias = [sanitizar_entrada(f) for f in request.form.getlist('frequencia[]') if f.strip()]
        quantidades = [sanitizar_entrada(q) for q in request.form.getlist('quantidade[]') if q.strip()]
        
        # Validation
        if not nome_paciente:
            return jsonify({'success': False, 'error': 'Nome do paciente é obrigatório'})
        
        if not principios_ativos:
            return jsonify({'success': False, 'error': 'É necessário pelo menos um medicamento'})
        
        # Build medications string
        medicamentos_completos = []
        min_length = min(len(principios_ativos), len(concentracoes), len(vias), len(frequencias), len(quantidades))
        
        for i in range(min_length):
            if all([principios_ativos[i], concentracoes[i], vias[i], frequencias[i], quantidades[i]]):
                medicamento = f"{principios_ativos[i]} {concentracoes[i]} - {vias[i]} - {frequencias[i]} - {quantidades[i]}"
                medicamentos_completos.append(medicamento)
        
        if not medicamentos_completos:
            return jsonify({'success': False, 'error': 'É necessário pelo menos um medicamento completo'})
        
        # Update prescription
        receita.nome_paciente = nome_paciente
        receita.medicamentos = '\n'.join(medicamentos_completos)
        receita.data = datetime.now()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Medicamentos salvos com sucesso'})
        
    except Exception as e:
        logging.error(f'Error saving medications: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Erro ao salvar medicamentos'})

@medicamentos_bp.route('/prontuario/medicamentos/<int:receita_id>/pdf')
def medicamentos_pdf(receita_id):
    """Generate PDF for medication prescription"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get the prescription
        receita = db.session.query(Receita).filter_by(id=receita_id).first()
        if not receita:
            flash('Receita não encontrada.', 'error')
            return redirect(url_for('prontuario.prontuario'))
        
        # Get doctor information
        medico = db.session.query(Medico).filter_by(id=receita.id_medico).first()
        
        # Parse medications
        medicamentos_list = []
        if receita.medicamentos:
            for med in receita.medicamentos.split('\n'):
                if med.strip():
                    medicamentos_list.append(med.strip())
        
        # Prepare data for PDF
        context = {
            'titulo': f'Receita Médica #{receita.id}',
            'nome_paciente': receita.nome_paciente,
            'data': receita.data.strftime('%d/%m/%Y'),
            'medicamentos': medicamentos_list,
            'medico_nome': medico.nome if medico else 'N/A',
            'medico_crm': medico.crm if medico else 'N/A'
        }
        
        # Generate PDF
        html_content = render_template('medicamentos_pdf.html', **context)
        
        filename = f'medicamentos_receita_{receita.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        return generate_pdf_response(html_content, filename)
        
    except Exception as e:
        logging.error(f'Error generating medication PDF: {e}')
        flash('Erro ao gerar PDF de medicamentos.', 'error')
        return redirect(url_for('prontuario.prontuario'))