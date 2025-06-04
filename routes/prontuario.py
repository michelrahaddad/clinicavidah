from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import Prontuario, Receita, ExameLab, ExameImg, Medico
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
        # Get search parameters
        busca_paciente = sanitizar_entrada(request.args.get('busca_paciente', ''))
        filtro_tipo = request.args.get('tipo', '')
        filtro_data_inicio = request.args.get('data_inicio', '')
        filtro_data_fim = request.args.get('data_fim', '')
        
        logging.info(f"Prontuario search - busca_paciente: '{busca_paciente}', filtro_tipo: '{filtro_tipo}', data_inicio: '{filtro_data_inicio}', data_fim: '{filtro_data_fim}'")
        
        resultados = []
        
        # Search in different record types based on filters
        tipos_busca = [filtro_tipo] if filtro_tipo else ['receita', 'exame_lab', 'exame_img']
        
        for tipo in tipos_busca:
            if tipo == 'receita':
                # Search in prescriptions
                query = db.session.query(Receita, Medico.nome.label('medico_nome')).join(Medico)
                
                if busca_paciente:
                    query = query.filter(Receita.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                if filtro_data_inicio and filtro_data_fim:
                    query = query.filter(Receita.data.between(filtro_data_inicio, filtro_data_fim))
                
                receitas = query.order_by(Receita.data.desc(), Receita.created_at.desc()).all()
                
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
                # Search in lab exams
                query = db.session.query(ExameLab, Medico.nome.label('medico_nome')).join(Medico)
                
                if busca_paciente:
                    query = query.filter(ExameLab.nome_paciente.ilike(f'%{busca_paciente}%'))
                
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
                # Search in imaging exams
                query = db.session.query(ExameImg, Medico.nome.label('medico_nome')).join(Medico)
                
                if busca_paciente:
                    query = query.filter(ExameImg.nome_paciente.ilike(f'%{busca_paciente}%'))
                
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
        
        # Sort all results by date (newest first)
        resultados.sort(key=lambda x: x['data'], reverse=True)
        
        return render_template('prontuario_clean.html', 
                             resultados=resultados,
                             busca_paciente=busca_paciente,
                             filtro_tipo=filtro_tipo,
                             filtro_data_inicio=filtro_data_inicio,
                             filtro_data_fim=filtro_data_fim)
                             
    except Exception as e:
        logging.error(f'Prontuario error: {e}')
        flash('Erro ao carregar prontuário.', 'error')
        return render_template('prontuario_clean.html', resultados=[])
