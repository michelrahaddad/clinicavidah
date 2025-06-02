from flask import Blueprint, render_template, redirect, url_for, flash
from utils.forms import MedicoForm
from utils.db import get_db_connection
from werkzeug.security import generate_password_hash
import logging

medicos_bp = Blueprint('medicos', __name__)

@medicos_bp.route('/cadastrar_medico', methods=['GET', 'POST'])
def cadastrar_medico():
    """Register new doctor"""
    form = MedicoForm()
    
    if form.validate_on_submit():
        try:
            nome = form.nome.data.strip() if form.nome.data else ""
            crm = form.crm.data.strip() if form.crm.data else ""
            senha = form.senha.data if form.senha.data else ""
            
            if not nome or not crm or not senha:
                flash('Todos os campos são obrigatórios.', 'error')
                return render_template('cadastro_medico.html', form=form)
            
            conn = get_db_connection()
            
            # Check if CRM already exists
            existente = conn.execute("SELECT * FROM medicos WHERE crm = ?", (crm,)).fetchone()
            if existente:
                flash('CRM já cadastrado no sistema!', 'error')
                conn.close()
                return render_template('cadastro_medico.html', form=form)
            
            # Hash password and insert doctor
            senha_hash = generate_password_hash(senha)
            conn.execute("INSERT INTO medicos (nome, crm, senha) VALUES (?, ?, ?)", 
                        (nome, crm, senha_hash))
            conn.commit()
            conn.close()
            
            flash('Médico cadastrado com sucesso! Faça login para continuar.', 'success')
            logging.info(f'New doctor registered: {nome} (CRM: {crm})')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            logging.error(f'Doctor registration error: {e}')
            flash('Erro interno ao cadastrar médico. Tente novamente.', 'error')
    
    return render_template('cadastro_medico.html', form=form)
