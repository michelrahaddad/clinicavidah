from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import Medico
from app import db
from werkzeug.security import generate_password_hash
import logging

medicos_bp = Blueprint('medicos', __name__)

@medicos_bp.route('/cadastrar_medico', methods=['GET', 'POST'])
def cadastrar_medico():
    if 'usuario' not in session and 'admin_usuario' not in session:
        return redirect(url_for('auth.login'))

    """Register new doctor"""
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            crm = request.form.get('crm', '').strip()
            senha = request.form.get('senha', '')
            assinatura = request.form.get('assinatura', '')
            
            if not nome or not crm or not senha or not assinatura:
                flash('Todos os campos são obrigatórios, incluindo a assinatura digital.', 'error')
                return render_template('cadastro_medico.html')
            
            # Check if CRM already exists - force fresh query
            from sqlalchemy import text
            db.session.commit()  # Ensure any pending changes are committed
            result = db.session.execute(text("SELECT id FROM medicos WHERE crm = :crm"), {'crm': crm}).fetchone()
            if result:
                flash('CRM já cadastrado no sistema!', 'error')
                return render_template('cadastro_medico.html')
            
            # Hash password and insert doctor
            senha_hash = generate_password_hash(senha)
            
            # Create new doctor with proper SQLAlchemy syntax
            from sqlalchemy import text
            db.session.execute(text(
                "INSERT INTO medicos (nome, crm, senha, assinatura) VALUES (:nome, :crm, :senha, :assinatura)"
            ), {
                'nome': nome,
                'crm': crm, 
                'senha': senha_hash,
                'assinatura': assinatura
            })
            
            db.session.commit()
            
            flash('Médico cadastrado com sucesso! Faça login para continuar.', 'success')
            logging.info(f'New doctor registered: {nome} (CRM: {crm})')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            logging.error(f'Doctor registration error: {e}')
            flash('Erro interno ao cadastrar médico. Tente novamente.', 'error')
    
    return render_template('cadastro_medico.html')
