from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from models import Prontuario, Receita, ExameLab, ExameImg, Medico, RelatorioMedico, AtestadoMedico, FormularioAltoCusto
from app import db
from utils.forms import sanitizar_entrada
import logging

prontuario_bp = Blueprint('prontuario', __name__)

@prontuario_bp.route('/prontuario', methods=['GET'])
def prontuario():
    """Display patient records"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get current doctor ID from session
        medico_id = session.get('medico_id')
        if not medico_id:
            flash('Sessão expirada. Faça login novamente.', 'error')
            return redirect(url_for('auth.login'))
            
        # Get search parameters
        busca_paciente = sanitizar_entrada(request.args.get('busca_paciente', ''))
        filtro_tipo = request.args.get('tipo', '')
        filtro_data_inicio = request.args.get('data_inicio', '')
        filtro_data_fim = request.args.get('data_fim', '')
        
        logging.info(f"Prontuario search - busca_paciente: '{busca_paciente}', filtro_tipo: '{filtro_tipo}', data_inicio: '{filtro_data_inicio}', data_fim: '{filtro_data_fim}', medico_id: {medico_id}")
        
        resultados = []
        
        # Search in different record types based on filters
        tipos_busca = [filtro_tipo] if filtro_tipo else ['receita', 'exame_lab', 'exame_img']
        
        for tipo in tipos_busca:
            if tipo == 'receita':
                # Search in prescriptions - only for current doctor
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
                # Search in lab exams - only for current doctor
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
                # Search in imaging exams - only for current doctor
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
        if not tipo or tipo == 'relatorio':
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
        if not tipo or tipo == 'atestado':
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
        if not tipo or tipo == 'alto_custo':
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

@prontuario_bp.route('/api/autocomplete_pacientes')
def autocomplete_pacientes():
    """API endpoint for patient name autocomplete"""
    if 'usuario' not in session:
        return {'suggestions': []}
    
    term = request.args.get('term', '').strip()
    if len(term) < 2:
        return {'suggestions': []}
    
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
        
        from flask import jsonify
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        logging.error(f"Autocomplete error: {str(e)}")
        from flask import jsonify
        return jsonify({'suggestions': []})

@prontuario_bp.route('/prontuario/detalhes', methods=['GET'])
def prontuario_detalhes():
    """Display detailed view of patient records for a specific date"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get current doctor ID from session
        medico_id = session.get('medico_id')
        if not medico_id:
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
                detalhes = f"CID: {relatorio.cid_codigo} - {relatorio.cid_descricao[:50]}{'...' if len(relatorio.cid_descricao) > 50 else ''}"
                
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
                detalhes = f"Medicamento: {formulario.medicamento[:50]}{'...' if len(formulario.medicamento) > 50 else ''}"
                
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
