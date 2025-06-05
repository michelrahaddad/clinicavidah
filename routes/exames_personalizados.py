from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from models import ExamePersonalizado, Medico
from main import db
from sqlalchemy import text
from utils.forms import sanitizar_entrada
from datetime import datetime
import logging

exames_personalizados_bp = Blueprint('exames_personalizados', __name__)

@exames_personalizados_bp.route('/api/adicionar_exame_personalizado', methods=['POST'])
def adicionar_exame_personalizado():
    """Add custom exam"""
    try:
        if 'usuario' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        nome_exame = sanitizar_entrada(request.form.get('nome_exame', ''))
        tipo_exame = sanitizar_entrada(request.form.get('tipo_exame', ''))  # 'laboratorial' ou 'imagem'
        categoria = sanitizar_entrada(request.form.get('categoria', ''))
        
        if not nome_exame or not tipo_exame:
            return jsonify({'success': False, 'message': 'Nome do exame e tipo são obrigatórios'}), 400
        
        if tipo_exame not in ['laboratorial', 'imagem']:
            return jsonify({'success': False, 'message': 'Tipo de exame inválido'}), 400
        
        # Get medico ID safely
        usuario_data = session['usuario']
        if isinstance(usuario_data, dict):
            medico_id = usuario_data.get('id')
        else:
            # Fallback - find medico by name
            medico = Medico.query.filter_by(nome=str(usuario_data)).first()
            medico_id = medico.id if medico else 1
        exame_existente = db.session.execute(
            text("SELECT id FROM exames_personalizados WHERE nome = :nome AND tipo = :tipo AND id_medico = :medico_id AND ativo = true"),
            {'nome': nome_exame, 'tipo': tipo_exame, 'medico_id': medico_id}
        ).first()
        
        if exame_existente:
            return jsonify({'success': False, 'message': 'Este exame já existe'}), 400
        
        # Insert new custom exam
        db.session.execute(
            text("""
            INSERT INTO exames_personalizados (nome, tipo, categoria, id_medico, ativo, created_at)
            VALUES (:nome, :tipo, :categoria, :medico_id, :ativo, :created_at)
            """),
            {
                'nome': nome_exame,
                'tipo': tipo_exame,
                'categoria': categoria,
                'medico_id': medico_id,
                'ativo': True,
                'created_at': datetime.now()
            }
        )
        db.session.commit()
        
        logging.info(f'Custom exam added: {nome_exame} ({tipo_exame}) by doctor {medico_id}')
        return jsonify({'success': True, 'message': 'Exame adicionado com sucesso'})
        
    except Exception as e:
        logging.error(f'Error adding custom exam: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@exames_personalizados_bp.route('/api/listar_exames_personalizados/<tipo>')
def listar_exames_personalizados(tipo):
    """List custom exams by type"""
    try:
        if 'usuario' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        if tipo not in ['laboratorial', 'imagem']:
            return jsonify({'success': False, 'message': 'Tipo de exame inválido'}), 400
        
        medico_id = session['usuario']['id']
        
        # Get custom exams for this doctor and type
        exames = db.session.execute(
            text("""
            SELECT id, nome, categoria 
            FROM exames_personalizados 
            WHERE tipo = :tipo AND id_medico = :medico_id AND ativo = true
            ORDER BY nome
            """),
            {'tipo': tipo, 'medico_id': medico_id}
        ).fetchall()
        
        exames_list = [{'id': exame.id, 'nome': exame.nome, 'categoria': exame.categoria} for exame in exames]
        
        return jsonify({'success': True, 'exames': exames_list})
        
    except Exception as e:
        logging.error(f'Error listing custom exams: {e}')
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@exames_personalizados_bp.route('/api/remover_exame_personalizado/<int:exame_id>', methods=['DELETE'])
def remover_exame_personalizado(exame_id):
    """Remove custom exam (soft delete)"""
    try:
        if 'usuario' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        medico_id = session['usuario']['id']
        
        # Soft delete - set ativo = false
        result = db.session.execute(
            text("""
            UPDATE exames_personalizados 
            SET ativo = false 
            WHERE id = :exame_id AND id_medico = :medico_id
            """),
            {'exame_id': exame_id, 'medico_id': medico_id}
        )
        
        if result.rowcount == 0:
            return jsonify({'success': False, 'message': 'Exame não encontrado'}), 404
        
        db.session.commit()
        logging.info(f'Custom exam removed: {exame_id} by doctor {medico_id}')
        
        return jsonify({'success': True, 'message': 'Exame removido com sucesso'})
        
    except Exception as e:
        logging.error(f'Error removing custom exam: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500