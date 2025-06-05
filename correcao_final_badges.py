#!/usr/bin/env python3
"""
Correção final definitiva dos badges médicos
Força a detecção de todos os tipos de documentos
"""

def corrigir_busca_prontuario_completa():
    """Corrige completamente a busca no prontuário"""
    
    with open('routes/prontuario.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir toda a função prontuario com uma versão que funciona
    nova_funcao = '''@prontuario_bp.route('/prontuario')
def prontuario():
    """Display patient records"""
    if 'medico_id' not in session and 'admin_usuario' not in session:
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
        
        # Always search all document types for complete badges
        tipos_busca = ['receita', 'exame_lab', 'exame_img', 'relatorio', 'atestado', 'alto_custo']
        
        if filtro_tipo:
            tipos_busca = [filtro_tipo]
            
        logging.info(f"Tipos de busca ativados: {tipos_busca}")
        
        resultados = []
        
        # Search Prescriptions
        if 'receita' in tipos_busca:
            try:
                query = db.session.query(Receita, Medico.nome.label('medico_nome')).join(Medico)
                
                if busca_paciente:
                    query = query.filter(Receita.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                if filtro_data_inicio and filtro_data_fim:
                    query = query.filter(Receita.data.between(filtro_data_inicio, filtro_data_fim))
                
                receitas = query.order_by(Receita.data.desc()).all()
                logging.info(f"Found {len(receitas)} receitas for search")
                
                for receita, medico_nome in receitas:
                    resultados.append({
                        'tipo': 'receita',
                        'data': receita.data,
                        'id_registro': receita.id,
                        'nome_paciente': receita.nome_paciente,
                        'medico_nome': medico_nome,
                        'detalhes_registro': f"Receita médica"
                    })
            except Exception as e:
                logging.error(f"Error searching receitas: {e}")
        
        # Search Lab Exams  
        if 'exame_lab' in tipos_busca:
            try:
                query = db.session.query(ExameLab)
                
                if busca_paciente:
                    query = query.filter(ExameLab.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                exames_lab = query.order_by(ExameLab.data.desc()).all()
                logging.info(f"Found {len(exames_lab)} exames lab for search")
                
                for exame in exames_lab:
                    resultados.append({
                        'tipo': 'exame_lab',
                        'data': exame.data,
                        'id_registro': exame.id,
                        'nome_paciente': exame.nome_paciente,
                        'medico_nome': getattr(exame, 'medico_nome', 'N/A'),
                        'detalhes_registro': f"Exame laboratorial"
                    })
            except Exception as e:
                logging.error(f"Error searching exames lab: {e}")
        
        # Search Image Exams
        if 'exame_img' in tipos_busca:
            try:
                query = db.session.query(ExameImg)
                
                if busca_paciente:
                    query = query.filter(ExameImg.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                exames_img = query.order_by(ExameImg.data.desc()).all()
                logging.info(f"Found {len(exames_img)} exames img for search")
                
                for exame in exames_img:
                    resultados.append({
                        'tipo': 'exame_img',
                        'data': exame.data,
                        'id_registro': exame.id,
                        'nome_paciente': exame.nome_paciente,
                        'medico_nome': getattr(exame, 'medico_nome', 'N/A'),
                        'detalhes_registro': f"Exame de imagem"
                    })
            except Exception as e:
                logging.error(f"Error searching exames img: {e}")
        
        # Search Medical Reports
        if 'relatorio' in tipos_busca:
            try:
                query = db.session.query(RelatorioMedico)
                
                if busca_paciente:
                    query = query.filter(RelatorioMedico.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                relatorios = query.order_by(RelatorioMedico.data.desc()).all()
                logging.info(f"Found {len(relatorios)} relatorios for search")
                
                for relatorio in relatorios:
                    resultados.append({
                        'tipo': 'relatorio',
                        'data': relatorio.data,
                        'id_registro': relatorio.id,
                        'nome_paciente': relatorio.nome_paciente,
                        'medico_nome': getattr(relatorio, 'medico_nome', 'N/A'),
                        'detalhes_registro': f"Relatório médico"
                    })
            except Exception as e:
                logging.error(f"Error searching relatorios: {e}")
        
        # Search Medical Certificates
        if 'atestado' in tipos_busca:
            try:
                query = db.session.query(AtestadoMedico)
                
                if busca_paciente:
                    query = query.filter(AtestadoMedico.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                atestados = query.order_by(AtestadoMedico.data.desc()).all()
                logging.info(f"Found {len(atestados)} atestados for search")
                
                for atestado in atestados:
                    resultados.append({
                        'tipo': 'atestado',
                        'data': atestado.data,
                        'id_registro': atestado.id,
                        'nome_paciente': atestado.nome_paciente,
                        'medico_nome': getattr(atestado, 'medico_nome', 'N/A'),
                        'detalhes_registro': f"Atestado médico"
                    })
            except Exception as e:
                logging.error(f"Error searching atestados: {e}")
        
        # Search High Cost Forms
        if 'alto_custo' in tipos_busca:
            try:
                query = db.session.query(FormularioAltoCusto)
                
                if busca_paciente:
                    query = query.filter(FormularioAltoCusto.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                formularios = query.order_by(FormularioAltoCusto.data.desc()).all()
                logging.info(f"Found {len(formularios)} alto custo for search")
                
                for formulario in formularios:
                    resultados.append({
                        'tipo': 'alto_custo',
                        'data': formulario.data,
                        'id_registro': formulario.id,
                        'nome_paciente': formulario.nome_paciente,
                        'medico_nome': getattr(formulario, 'medico_nome', 'N/A'),
                        'detalhes_registro': f"Formulário alto custo"
                    })
            except Exception as e:
                logging.error(f"Error searching alto custo: {e}")
        
        # Group results by patient and date with medical document counters
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
                    },
                    'total_documentos': 0
                }
            
            tipo = resultado['tipo']
            grupos[key]['contadores'][tipo] += 1
            grupos[key]['documentos'][tipo].append(resultado)
            grupos[key]['total_documentos'] += 1
        
        # Log dos contadores para debug
        for key, grupo in grupos.items():
            if 'michel' in grupo['nome_paciente'].lower():
                logging.info(f"Debug Michel - {key}: receitas={grupo['contadores']['receita']}, "
                           f"lab={grupo['contadores']['exame_lab']}, img={grupo['contadores']['exame_img']}, "
                           f"relatorios={grupo['contadores']['relatorio']}, atestados={grupo['contadores']['atestado']}, "
                           f"alto_custo={grupo['contadores']['alto_custo']}")
        
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
        return render_template('prontuario_modern.html', resultados=[])'''
    
    # Encontrar e substituir a função prontuario
    import re
    pattern = r'@prontuario_bp\.route\(\'/prontuario\'\)\ndef prontuario\(\):.*?return render_template\(\'prontuario_modern\.html\', resultados=\[\]\)'
    content = re.sub(pattern, nova_funcao, content, flags=re.DOTALL)
    
    with open('routes/prontuario.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Função prontuário completamente corrigida")

def executar_correcao_final():
    """Executa a correção final"""
    print("🔧 Executando correção final definitiva...")
    
    try:
        corrigir_busca_prontuario_completa()
        
        print("✅ Correção final concluída!")
        print("Agora teste acessando /prontuario com seu login")
        
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        return False
    
    return True

if __name__ == '__main__':
    executar_correcao_final()