from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from models import db, Atestado, Paciente
from datetime import datetime
import logging

def sanitizar_entrada(valor):
    """Sanitiza entrada de usuário"""
    if not valor:
        return ""
    
    # Remove caracteres perigosos
    import re
    valor = re.sub(r'[<>"\']', '', str(valor))
    return valor.strip()

atestado_bp = Blueprint('atestado', __name__)

@atestado_bp.route('/atestado')
def atestado():
    """Página de atestado médico"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    return render_template('atestado.html')

@atestado_bp.route('/atestado', methods=['POST'])
def salvar_atestado():
    """Salva atestado médico"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        nome_paciente = sanitizar_entrada(request.form.get('nome_paciente'))
        dias_afastamento = sanitizar_entrada(request.form.get('dias_afastamento'))
        
        if not nome_paciente or not dias_afastamento:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('atestado.html')
        
        # Salvar atestado
        atestado = Atestado(
            nome_paciente=nome_paciente,
            dias_afastamento=int(dias_afastamento),
            data_criacao=datetime.now(),
            usuario_id=session.get('usuario', session.get('admin_usuario'))
        )
        
        db.session.add(atestado)
        db.session.commit()
        
        flash('Atestado salvo com sucesso!', 'success')
        return render_template('atestado.html')
        
    except Exception as e:
        logging.error(f'Erro ao salvar atestado: {e}')
        flash('Erro ao salvar atestado.', 'error')
        return render_template('atestado.html')

@atestado_bp.route('/api/pacientes')
def get_pacientes():
    """API para autocomplete de pacientes"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return jsonify([])
    
    try:
        term = request.args.get('q', '').strip()
        if len(term) < 2:
            return jsonify([])
        
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
        return jsonify([])
