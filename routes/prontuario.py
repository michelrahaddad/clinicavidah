from sqlalchemy import or_
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from models import Prontuario, Receita, ExameLab, ExameImg, Medico, RelatorioMedico, AtestadoMedico, FormularioAltoCusto, Paciente
from app import db
from utils.forms import sanitizar_entrada
import logging

def sanitizar_entrada(valor):
    """Sanitiza entrada de usuário"""
    if not valor:
        return ""
    
    # Remove caracteres perigosos
    import re
    valor = re.sub(r'[<>"\']', '', str(valor))
    return valor.strip()


prontuario_bp = Blueprint('prontuario', __name__)

@prontuario_bp.route('/prontuario', methods=['GET'])
def prontuario():
    """Display patient records"""
    # Log session data for debugging
    logging.info(f"Prontuario access - usuario: {session.get('usuario')}, admin_usuario: {session.get('admin_usuario')}")
    
    # Simple authentication check
    if 'usuario' not in session and 'admin_usuario' not in session:
        logging.info("No valid session found, redirecting to login")
        return redirect(url_for('auth.login'))
    
    try:
        # Get current doctor ID from session, handle admin users
        medico_id = session.get('medico_id')
        admin_data = session.get('admin_data')
        
        # If admin user, get first available doctor ID or use a default value
        if not medico_id and (admin_data or 'admin_usuario' in session):
            primeiro_medico = db.session.query(Medico).first()
            if primeiro_medico:
                medico_id = primeiro_medico.id
                logging.info(f"Admin user accessing prontuario, using medico_id: {medico_id}")
            else:
                medico_id = 1  # Default fallback
            
        # Get search parameters
        busca_paciente = sanitizar_entrada(request.args.get('busca_paciente', ''))
        filtro_tipo = request.args.get('tipo', '')
        filtro_data_inicio = request.args.get('data_inicio', '')
        filtro_data_fim = request.args.get('data_fim', '')
        
        logging.info(f"Prontuario search - busca_paciente: '{busca_paciente}', filtro_tipo: '{filtro_tipo}', data_inicio: '{filtro_data_inicio}', data_fim: '{filtro_data_fim}', medico_id: {medico_id}")
        
        resultados = []
        
        # Search in different record types based on filters
        tipos_busca = [filtro_tipo] if filtro_tipo else ['receita', 'exame_lab', 'exame_img']
        
        # Check if user is admin
        is_admin = admin_data or 'admin_usuario' in session
        
        for tipo in tipos_busca:
            if tipo == 'receita':
                # Search in prescriptions - admin sees all, doctors see only their own
                if is_admin:
                    query = db.session.query(Receita, Medico.nome.label('medico_nome')).join(Medico)
                else:
                    query = db.session.query(Receita, Medico.nome.label('medico_nome')).join(Medico).filter(Receita.id_medico == medico_id)
                
                if busca_paciente:
                    # Split search terms and create flexible search
                    search_terms = busca_paciente.strip().split()
                    for term in search_terms:
                        if len(term) >= 2:  # Only search terms with 2+ characters
                            query = query.filter(Receita.nome_paciente.ilike(f'%{term}%'))
                
                if filtro_data_inicio and filtro_data_fim:
                    query = query.filter(Receita.data.between(filtro_data_inicio, filtro_data_fim))
                
                receitas = query.order_by(Receita.data.desc(), Receita.created_at.desc()).all()
                
                logging.info(f"Found {len(receitas)} receitas for search term '{busca_paciente}'")
                
                for receita, medico_nome in receitas:
                    try:
                        medicamentos = receita.medicamentos.split('\n')
                        detalhes_registro = f"Medicamentos: {', '.join([m.strip() for m in medicamentos[:3] if m.strip()])}{'...' if len(medicamentos) > 3 else ''}"
                        
                        resultados.append({
                            'tipo': 'receita',
                            'data': receita.data,
                            'id_registro': receita.id,
                            'nome_paciente': receita.nome_paciente,
                            'medico_nome': medico_nome,
                            'detalhes_registro': detalhes_registro
                        })
                    except Exception as e:
                        logging.warning(f"Error processing prescription {receita.id}: {e}")
                        continue
            
            elif tipo == 'exame_lab':
                # Search in lab exams - admin sees all, doctors see only their own
                if is_admin:
                    query = db.session.query(ExameLab, Medico.nome.label('medico_nome')).join(Medico)
                else:
                    query = db.session.query(ExameLab, Medico.nome.label('medico_nome')).join(Medico).filter(ExameLab.id_medico == medico_id)
                
                if busca_paciente:
                    # Split search terms and create flexible search
                    search_terms = busca_paciente.strip().split()
                    for term in search_terms:
                        if len(term) >= 2:  # Only search terms with 2+ characters
                            query = query.filter(ExameLab.nome_paciente.ilike(f'%{term}%'))
                
                if filtro_data_inicio and filtro_data_fim:
                    query = query.filter(ExameLab.data.between(filtro_data_inicio, filtro_data_fim))
                
                exames_lab = query.order_by(ExameLab.data.desc(), ExameLab.created_at.desc()).all()
                
                for exame, medico_nome in exames_lab:
                    try:
                        exames = exame.exames.split('\n')
                        detalhes_registro = f"Exames: {', '.join([e.strip() for e in exames[:3] if e.strip()])}{'...' if len(exames) > 3 else ''}"
                        
                        resultados.append({
                            'tipo': 'exame_lab',
                            'data': exame.data,
                            'id_registro': exame.id,
                            'nome_paciente': exame.nome_paciente,
                            'medico_nome': medico_nome,
                            'detalhes_registro': detalhes_registro
                        })
                    except Exception as e:
                        logging.warning(f"Error processing lab exam {exame.id}: {e}")
                        continue
            
            elif tipo == 'exame_img':
                # Search in imaging exams - admin sees all, doctors see only their own
                if is_admin:
                    query = db.session.query(ExameImg, Medico.nome.label('medico_nome')).join(Medico)
                else:
                    query = db.session.query(ExameImg, Medico.nome.label('medico_nome')).join(Medico).filter(ExameImg.id_medico == medico_id)
                
                if busca_paciente:
                    # Split search terms and create flexible search
                    search_terms = busca_paciente.strip().split()
                    for term in search_terms:
                        if len(term) >= 2:  # Only search terms with 2+ characters
                            query = query.filter(ExameImg.nome_paciente.ilike(f'%{term}%'))
                
                if filtro_data_inicio and filtro_data_fim:
                    query = query.filter(ExameImg.data.between(filtro_data_inicio, filtro_data_fim))
                
                exames_img = query.order_by(ExameImg.data.desc(), ExameImg.created_at.desc()).all()
                
                for exame, medico_nome in exames_img:
                    try:
                        exames = exame.exames.split('\n')
                        detalhes_registro = f"Exames: {', '.join([e.strip() for e in exames[:3] if e.strip()])}{'...' if len(exames) > 3 else ''}"
                        
                        resultados.append({
                            'tipo': 'exame_img',
                            'data': exame.data,
                            'id_registro': exame.id,
                            'nome_paciente': exame.nome_paciente,
                            'medico_nome': medico_nome,
                            'detalhes_registro': detalhes_registro
                        })
                    except Exception as e:
                        logging.warning(f"Error processing imaging exam {exame.id}: {e}")
                        continue
        
        # Search Medical Reports
        if 'relatorio' in tipos_busca:
            query = db.session.query(RelatorioMedico, Medico.nome.label('medico_nome')).join(Medico)
            
            if busca_paciente:
                search_terms = busca_paciente.strip().split()
                for term in search_terms:
                    if len(term) >= 2:
                        query = query.filter(RelatorioMedico.nome_paciente.ilike(f'%{term}%'))
            
            if filtro_data_inicio and filtro_data_fim:
                query = query.filter(RelatorioMedico.data.between(filtro_data_inicio, filtro_data_fim))
            
            relatorios = query.order_by(RelatorioMedico.data.desc(), RelatorioMedico.created_at.desc()).all()
            
            for relatorio, medico_nome in relatorios:
                try:
                    detalhes_registro = f"CID: {relatorio.cid_codigo} - {relatorio.cid_descricao[:50]}{'...' if len(relatorio.cid_descricao) > 50 else ''}"
                    
                    resultados.append({
                        'tipo': 'relatorio',
                        'data': relatorio.data,
                        'id_registro': relatorio.id,
                        'nome_paciente': relatorio.nome_paciente,
                        'medico_nome': medico_nome,
                        'detalhes_registro': detalhes_registro
                    })
                except Exception as e:
                    logging.warning(f"Error processing medical report {relatorio.id}: {e}")
                    continue
        
        # Search Medical Certificates
        if 'atestado' in tipos_busca:
            query = db.session.query(AtestadoMedico, Medico.nome.label('medico_nome')).join(Medico)
            
            if busca_paciente:
                search_terms = busca_paciente.strip().split()
                for term in search_terms:
                    if len(term) >= 2:
                        query = query.filter(AtestadoMedico.nome_paciente.ilike(f'%{term}%'))
            
            if filtro_data_inicio and filtro_data_fim:
                query = query.filter(AtestadoMedico.data.between(filtro_data_inicio, filtro_data_fim))
            
            atestados = query.order_by(AtestadoMedico.data.desc(), AtestadoMedico.created_at.desc()).all()
            
            for atestado, medico_nome in atestados:
                try:
                    detalhes_registro = f"Afastamento: {atestado.dias_afastamento} dias - CID: {atestado.cid_codigo}"
                    
                    resultados.append({
                        'tipo': 'atestado',
                        'data': atestado.data,
                        'id_registro': atestado.id,
                        'nome_paciente': atestado.nome_paciente,
                        'medico_nome': medico_nome,
                        'detalhes_registro': detalhes_registro
                    })
                except Exception as e:
                    logging.warning(f"Error processing medical certificate {atestado.id}: {e}")
                    continue
        
        # Search High Cost Forms
        if 'alto_custo' in tipos_busca:
            query = db.session.query(FormularioAltoCusto, Medico.nome.label('medico_nome')).join(Medico)
            
            if busca_paciente:
                search_terms = busca_paciente.strip().split()
                for term in search_terms:
                    if len(term) >= 2:
                        query = query.filter(FormularioAltoCusto.nome_paciente.ilike(f'%{term}%'))
            
            if filtro_data_inicio and filtro_data_fim:
                query = query.filter(FormularioAltoCusto.data.between(filtro_data_inicio, filtro_data_fim))
            
            formularios = query.order_by(FormularioAltoCusto.data.desc(), FormularioAltoCusto.created_at.desc()).all()
            
            for formulario, medico_nome in formularios:
                try:
                    detalhes_registro = f"Medicamento: {formulario.medicamento[:50]}{'...' if len(formulario.medicamento) > 50 else ''} - CID: {formulario.cid_codigo}"
                    
                    resultados.append({
                        'tipo': 'alto_custo',
                        'data': formulario.data,
                        'id_registro': formulario.id,
                        'nome_paciente': formulario.nome_paciente,
                        'medico_nome': medico_nome,
                        'detalhes_registro': detalhes_registro
                    })
                except Exception as e:
                    logging.warning(f"Error processing high cost form {formulario.id}: {e}")
                    continue
        
        # Group results by patient and date with counters
        grupos = {}
        for resultado in resultados:
            key = f"{resultado['nome_paciente']}|{resultado['data']}"
            if key not in grupos:
                grupos[key] = {
                    'nome_paciente': resultado['nome_paciente'],
                    'data': resultado['data'],
                    'medico_nome': resultado['medico_nome'],
                    'contadores': {
                        'receita': 0,
                        'exame_lab': 0,
                        'exame_img': 0,
                        'relatorio': 0,
                        'atestado': 0,
                        'alto_custo': 0
                    },
                    'documentos': {
                        'receita': [],
                        'exame_lab': [],
                        'exame_img': [],
                        'relatorio': [],
                        'atestado': [],
                        'alto_custo': []
                    }
                }
            
            tipo = resultado['tipo']
            grupos[key]['contadores'][tipo] += 1
            grupos[key]['documentos'][tipo].append(resultado)
        
        # Convert to list and sort by date (newest first)
        resultados_agrupados = list(grupos.values())
        resultados_agrupados.sort(key=lambda x: x['data'], reverse=True)
        
        return render_template('prontuario_modern.html', 
                             resultados=resultados_agrupados,
                             busca_paciente=busca_paciente,
                             filtro_tipo=filtro_tipo,
                             filtro_data_inicio=filtro_data_inicio,
                             filtro_data_fim=filtro_data_fim)
                             
    except Exception as e:
        logging.error(f'Prontuario error: {e}')
        flash('Erro ao carregar prontuário.', 'error')
        return render_template('prontuario_modern.html', resultados=[])

@prontuario_bp.route('/prontuario/api/autocomplete_pacientes')
def autocomplete_pacientes():
    """API endpoint for patient name autocomplete"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return {'suggestions': []}
    
    term = request.args.get('q', '').strip()
    if len(term) < 2:
        return jsonify({'suggestions': []})
    
    try:
        # Get unique patient names from all tables
        receitas_names = db.session.query(Receita.nome_paciente).filter(
            Receita.nome_paciente.ilike(f'%{term}%')
        ).distinct().limit(10).all()
        
        exames_lab_names = db.session.query(ExameLab.nome_paciente).filter(
            ExameLab.nome_paciente.ilike(f'%{term}%')
        ).distinct().limit(10).all()
        
        exames_img_names = db.session.query(ExameImg.nome_paciente).filter(
            ExameImg.nome_paciente.ilike(f'%{term}%')
        ).distinct().limit(10).all()
        
        relatorios_names = db.session.query(RelatorioMedico.nome_paciente).filter(
            RelatorioMedico.nome_paciente.ilike(f'%{term}%')
        ).distinct().limit(10).all()
        
        atestados_names = db.session.query(AtestadoMedico.nome_paciente).filter(
            AtestadoMedico.nome_paciente.ilike(f'%{term}%')
        ).distinct().limit(10).all()
        
        alto_custo_names = db.session.query(FormularioAltoCusto.nome_paciente).filter(
            FormularioAltoCusto.nome_paciente.ilike(f'%{term}%')
        ).distinct().limit(10).all()
        
        # Combine and deduplicate
        all_names = set()
        for result in receitas_names + exames_lab_names + exames_img_names + relatorios_names + atestados_names + alto_custo_names:
            all_names.add(result[0])
        
        # Sort and limit to 8 suggestions
        suggestions = sorted(list(all_names))[:8]
        
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        logging.error(f"Autocomplete error: {str(e)}")
        return jsonify({'suggestions': []})

@prontuario_bp.route('/prontuario/detalhes', methods=['GET'])
def prontuario_detalhes():
    """Display detailed view of patient records for a specific date"""
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
        
        # Only redirect if neither medico_id nor admin session exists
        if not medico_id and not admin_data and 'admin_usuario' not in session:
            flash('Sessão expirada. Faça login novamente.', 'error')
            return redirect(url_for('auth.login'))
            
        # Get parameters
        paciente_nome = request.args.get('paciente', '')
        data_selecionada = request.args.get('data', '')
        tipo_filtro = request.args.get('tipo', '')  # Optional filter by document type
        
        if not paciente_nome or not data_selecionada:
            flash('Parâmetros inválidos.', 'error')
            return redirect(url_for('prontuario.prontuario'))
        
        logging.info(f"Prontuario detalhes - paciente: '{paciente_nome}', data: '{data_selecionada}', tipo: '{tipo_filtro}', medico_id: {medico_id}")
        
        # Get doctor info
        medico = db.session.query(Medico).filter_by(id=medico_id).first()
        medico_nome = medico.nome if medico else "Médico"
        
        # Initialize document collections
        documentos = {
            'receita': [],
            'exame_lab': [],
            'exame_img': [],
            'relatorio': [],
            'atestado': [],
            'alto_custo': []
        }
        
        # Search in Receitas - only for current doctor
        if not tipo_filtro or tipo_filtro == 'receita':
            receitas = db.session.query(Receita).filter(
                Receita.id_medico == medico_id,
                Receita.nome_paciente.ilike(f'%{paciente_nome}%'),
                Receita.data == data_selecionada
            ).all()
            
            for receita in receitas:
                medicamentos = receita.medicamentos.split('\n')
                detalhes = f"Medicamentos: {', '.join([m.strip() for m in medicamentos[:3] if m.strip()])}{'...' if len(medicamentos) > 3 else ''}"
                
                documentos['receita'].append({
                    'id_registro': receita.id,
                    'data': receita.data,
                    'detalhes_registro': detalhes
                })
        
        # Search in ExameLab - only for current doctor
        if not tipo_filtro or tipo_filtro == 'exame_lab':
            exames_lab = db.session.query(ExameLab).filter(
                ExameLab.id_medico == medico_id,
                ExameLab.nome_paciente.ilike(f'%{paciente_nome}%'),
                ExameLab.data == data_selecionada
            ).all()
            
            for exame in exames_lab:
                exames = exame.exames.split('\n')
                detalhes = f"Exames: {', '.join([e.strip() for e in exames[:3] if e.strip()])}{'...' if len(exames) > 3 else ''}"
                
                documentos['exame_lab'].append({
                    'id_registro': exame.id,
                    'data': exame.data,
                    'detalhes_registro': detalhes
                })
        
        # Search in ExameImg - only for current doctor
        if not tipo_filtro or tipo_filtro == 'exame_img':
            exames_img = db.session.query(ExameImg).filter(
                ExameImg.id_medico == medico_id,
                ExameImg.nome_paciente.ilike(f'%{paciente_nome}%'),
                ExameImg.data == data_selecionada
            ).all()
            
            for exame in exames_img:
                exames = exame.exames.split('\n')
                detalhes = f"Exames: {', '.join([e.strip() for e in exames[:3] if e.strip()])}{'...' if len(exames) > 3 else ''}"
                
                documentos['exame_img'].append({
                    'id_registro': exame.id,
                    'data': exame.data,
                    'detalhes_registro': detalhes
                })
        
        # Search in RelatorioMedico - only for current doctor
        if not tipo_filtro or tipo_filtro == 'relatorio':
            relatorios = db.session.query(RelatorioMedico).filter(
                RelatorioMedico.id_medico == medico_id,
                RelatorioMedico.nome_paciente.ilike(f'%{paciente_nome}%'),
                RelatorioMedico.data == data_selecionada
            ).all()
            
            for relatorio in relatorios:
                try:
                    cid_desc = str(relatorio.cid_descricao) if hasattr(relatorio, 'cid_descricao') and relatorio.cid_descricao else ''
                except:
                    cid_desc = ''
                detalhes = f"CID: {relatorio.cid_codigo} - {cid_desc[:50]}{'...' if len(cid_desc) > 50 else ''}"
                
                documentos['relatorio'].append({
                    'id_registro': relatorio.id,
                    'data': relatorio.data,
                    'detalhes_registro': detalhes
                })
        
        # Search in AtestadoMedico - only for current doctor
        if not tipo_filtro or tipo_filtro == 'atestado':
            atestados = db.session.query(AtestadoMedico).filter(
                AtestadoMedico.id_medico == medico_id,
                AtestadoMedico.nome_paciente.ilike(f'%{paciente_nome}%'),
                AtestadoMedico.data == data_selecionada
            ).all()
            
            for atestado in atestados:
                detalhes = f"Afastamento: {atestado.dias_afastamento} dias - CID: {atestado.cid_codigo}"
                
                documentos['atestado'].append({
                    'id_registro': atestado.id,
                    'data': atestado.data,
                    'detalhes_registro': detalhes
                })
        
        # Search in FormularioAltoCusto - only for current doctor
        if not tipo_filtro or tipo_filtro == 'alto_custo':
            formularios = db.session.query(FormularioAltoCusto).filter(
                FormularioAltoCusto.id_medico == medico_id,
                FormularioAltoCusto.nome_paciente.ilike(f'%{paciente_nome}%'),
                FormularioAltoCusto.data == data_selecionada
            ).all()
            
            for formulario in formularios:
                try:
                    medicamento_text = str(formulario.medicamento) if formulario.medicamento else ''
                except:
                    medicamento_text = ''
                detalhes = f"Medicamento: {medicamento_text[:50]}{'...' if len(medicamento_text) > 50 else ''}"
                
                documentos['alto_custo'].append({
                    'id_registro': formulario.id,
                    'data': formulario.data,
                    'detalhes_registro': detalhes
                })
        
        return render_template('prontuario_detalhes.html',
                             paciente_nome=paciente_nome,
                             data_formatada=data_selecionada,
                             medico_nome=medico_nome,
                             documentos=documentos,
                             tipo_filtro=tipo_filtro)
                             
    except Exception as e:
        logging.error(f'Prontuario detalhes error: {e}')
        flash('Erro ao carregar detalhes do prontuário.', 'error')
        return redirect(url_for('prontuario.prontuario'))

@prontuario_bp.route('/prontuario/api/update_date', methods=['POST'])
def update_date():
    """API endpoint to update document date"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return jsonify({'success': False, 'error': 'Sessão expirada'})
    
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
        
        if not medico_id and not admin_data and 'admin_usuario' not in session:
            return jsonify({'success': False, 'error': 'Sessão expirada'})
        
        data = request.get_json()
        tipo = data.get('tipo')
        doc_id = data.get('id')
        nova_data = data.get('nova_data')
        
        if not all([tipo, doc_id, nova_data]):
            return jsonify({'success': False, 'error': 'Parâmetros inválidos'})
        
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(nova_data, '%Y-%m-%d')
        except ValueError:
            return jsonify({'success': False, 'error': 'Formato de data inválido'})
        
        # Update the appropriate table based on document type
        if tipo == 'receita':
            receita = db.session.query(Receita).filter_by(id=doc_id, id_medico=medico_id).first()
            if receita:
                receita.data = nova_data
                db.session.commit()
                return jsonify({'success': True})
        
        elif tipo == 'exame_lab':
            exame = db.session.query(ExameLab).filter_by(id=doc_id, id_medico=medico_id).first()
            if exame:
                exame.data = nova_data
                db.session.commit()
                return jsonify({'success': True})
        
        elif tipo == 'exame_img':
            exame = db.session.query(ExameImg).filter_by(id=doc_id, id_medico=medico_id).first()
            if exame:
                exame.data = nova_data
                db.session.commit()
                return jsonify({'success': True})
        
        elif tipo == 'relatorio':
            relatorio = db.session.query(RelatorioMedico).filter_by(id=doc_id, id_medico=medico_id).first()
            if relatorio:
                relatorio.data = nova_data
                db.session.commit()
                return jsonify({'success': True})
        
        elif tipo == 'atestado':
            atestado = db.session.query(AtestadoMedico).filter_by(id=doc_id, id_medico=medico_id).first()
            if atestado:
                atestado.data = nova_data
                db.session.commit()
                return jsonify({'success': True})
        
        elif tipo == 'alto_custo':
            formulario = db.session.query(FormularioAltoCusto).filter_by(id=doc_id, id_medico=medico_id).first()
            if formulario:
                formulario.data = nova_data
                db.session.commit()
                return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Documento não encontrado'})
        
    except Exception as e:
        logging.error(f'Update date error: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@prontuario_bp.route('/prontuario/api/autocomplete', methods=['POST'])
def autocomplete():
    """API endpoint for patient name autocomplete"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return jsonify({'success': False, 'error': 'Sessão expirada'})
    
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
        
        if not medico_id and not admin_data and 'admin_usuario' not in session:
            return jsonify({'success': False, 'error': 'Sessão expirada'})
        
        data = request.get_json()
        termo = data.get('termo', '').strip()
        
        if len(termo) < 2:
            return jsonify({'sugestoes': []})
        
        sugestoes = []
        pacientes_encontrados = set()
        
        # Se for admin, buscar em todos os médicos; se for médico específico, só nos seus registros
        is_admin = admin_data or 'admin_usuario' in session
        
        # Buscar em receitas
        if is_admin:
            receitas = db.session.query(Receita.nome_paciente, Receita.data).filter(
                Receita.nome_paciente.ilike(f'%{termo}%')
            ).order_by(Receita.data.desc()).limit(20).all()
        else:
            receitas = db.session.query(Receita.nome_paciente, Receita.data).filter(
                Receita.id_medico == medico_id,
                Receita.nome_paciente.ilike(f'%{termo}%')
            ).order_by(Receita.data.desc()).limit(10).all()
        
        for receita in receitas:
            nome = receita.nome_paciente
            if nome not in pacientes_encontrados:
                pacientes_encontrados.add(nome)
                sugestoes.append({
                    'nome': nome,
                    'ultima_data': receita.data,
                    'tipo': 'receita'
                })
        
        # Buscar em exames laboratoriais
        if is_admin:
            exames_lab = db.session.query(ExameLab.nome_paciente, ExameLab.data).filter(
                ExameLab.nome_paciente.ilike(f'%{termo}%')
            ).order_by(ExameLab.data.desc()).limit(20).all()
        else:
            exames_lab = db.session.query(ExameLab.nome_paciente, ExameLab.data).filter(
                ExameLab.id_medico == medico_id,
                ExameLab.nome_paciente.ilike(f'%{termo}%')
            ).order_by(ExameLab.data.desc()).limit(10).all()
        
        for exame in exames_lab:
            nome = exame.nome_paciente
            if nome not in pacientes_encontrados:
                pacientes_encontrados.add(nome)
                sugestoes.append({
                    'nome': nome,
                    'ultima_data': exame.data,
                    'tipo': 'exame_lab'
                })
        
        # Buscar em exames de imagem
        if is_admin:
            exames_img = db.session.query(ExameImg.nome_paciente, ExameImg.data).filter(
                ExameImg.nome_paciente.ilike(f'%{termo}%')
            ).order_by(ExameImg.data.desc()).limit(20).all()
        else:
            exames_img = db.session.query(ExameImg.nome_paciente, ExameImg.data).filter(
                ExameImg.id_medico == medico_id,
                ExameImg.nome_paciente.ilike(f'%{termo}%')
            ).order_by(ExameImg.data.desc()).limit(10).all()
        
        for exame in exames_img:
            nome = exame.nome_paciente
            if nome not in pacientes_encontrados:
                pacientes_encontrados.add(nome)
                sugestoes.append({
                    'nome': nome,
                    'ultima_data': exame.data,
                    'tipo': 'exame_img'
                })
        
        # Ordenar sugestões por data mais recente
        sugestoes.sort(key=lambda x: x['ultima_data'], reverse=True)
        
        # Limitar a 8 sugestões
        sugestoes = sugestoes[:8]
        
        logging.info(f"Autocomplete search for '{termo}' returned {len(sugestoes)} suggestions")
        
        return jsonify({'success': True, 'sugestoes': sugestoes})
        
    except Exception as e:
        logging.error(f'Autocomplete error: {e}')
        return jsonify({'success': False, 'error': str(e)})

@prontuario_bp.route('/api/pacientes')
def get_pacientes():
    """API para buscar pacientes - funciona para médicos e administradores"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return jsonify([])
    
    try:
        term = request.args.get('q', '').strip()
        if len(term) < 2:
            return jsonify([])
        
        # Buscar pacientes cadastrados
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
                'cidade': p.cidade or ''
            })
        
        return jsonify(result)
    except Exception as e:
        print(f"Erro na API de pacientes: {e}")
        return jsonify([])
