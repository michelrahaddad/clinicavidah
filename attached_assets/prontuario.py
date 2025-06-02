from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.db import get_db_connection
from utils.forms import sanitizar_entrada
import logging

prontuario_bp = Blueprint('prontuario', __name__)

@prontuario_bp.route('/prontuario', methods=['GET'])
def prontuario():
    """Display patient records"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Get search parameters
        busca_paciente = sanitizar_entrada(request.args.get('busca_paciente', ''))
        filtro_tipo = request.args.get('tipo', '')
        filtro_data_inicio = request.args.get('data_inicio', '')
        filtro_data_fim = request.args.get('data_fim', '')
        
        conn = get_db_connection()
        
        # Build query
        query = """
        SELECT p.*, m.nome as medico_nome
        FROM prontuario p
        JOIN medicos m ON p.id_medico = m.id
        WHERE 1=1
        """
        params = []
        
        if filtro_tipo:
            query += " AND p.tipo = ?"
            params.append(filtro_tipo)
        
        if filtro_data_inicio and filtro_data_fim:
            query += " AND date(p.data) BETWEEN ? AND ?"
            params.append(filtro_data_inicio)
            params.append(filtro_data_fim)
        
        query += " ORDER BY p.data DESC, p.created_at DESC LIMIT 50"
        
        registros = conn.execute(query, params).fetchall()
        
        # Get detailed information for each record
        resultados = []
        for reg in registros:
            dados = None
            detalhes_registro = ""
            
            try:
                if reg['tipo'] == 'receita':
                    dados = conn.execute("SELECT * FROM receitas WHERE id = ?", (reg['id_registro'],)).fetchone()
                    if dados:
                        medicamentos = dados['medicamentos'].split(',')
                        detalhes_registro = f"Medicamentos: {', '.join(medicamentos[:3])}{'...' if len(medicamentos) > 3 else ''}"
                elif reg['tipo'] == 'exame_lab':
                    dados = conn.execute("SELECT * FROM exames_lab WHERE id = ?", (reg['id_registro'],)).fetchone()
                    if dados:
                        exames = dados['exames'].split(',')
                        detalhes_registro = f"Exames: {', '.join(exames[:3])}{'...' if len(exames) > 3 else ''}"
                elif reg['tipo'] == 'exame_img':
                    dados = conn.execute("SELECT * FROM exames_img WHERE id = ?", (reg['id_registro'],)).fetchone()
                    if dados:
                        exames = dados['exames'].split(',')
                        detalhes_registro = f"Exames: {', '.join(exames[:3])}{'...' if len(exames) > 3 else ''}"
                
                if dados:
                    # Filter by patient name if specified
                    if busca_paciente and busca_paciente.lower() not in dados['nome_paciente'].lower():
                        continue
                    
                    resultados.append({
                        'tipo': reg['tipo'],
                        'data': reg['data'],
                        'id_registro': reg['id_registro'],
                        'nome_paciente': dados['nome_paciente'],
                        'medico_nome': reg['medico_nome'],
                        'detalhes_registro': detalhes_registro
                    })
                    
            except Exception as e:
                logging.warning(f"Error processing record {reg['id']}: {e}")
                continue
        
        conn.close()
        
        return render_template('prontuario.html', 
                             resultados=resultados,
                             busca_paciente=busca_paciente,
                             filtro_tipo=filtro_tipo,
                             filtro_data_inicio=filtro_data_inicio,
                             filtro_data_fim=filtro_data_fim)
                             
    except Exception as e:
        logging.error(f'Prontuario error: {e}')
        flash('Erro ao carregar prontuário.', 'error')
        return render_template('prontuario.html', resultados=[])
