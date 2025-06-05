from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import Medico
from app import db
from werkzeug.security import generate_password_hash
import logging

medicos_bp = Blueprint('medicos', __name__)

@medicos_bp.route('/cadastrar_medico', methods=['GET', 'POST'])
def cadastrar_medico():
    """Register new doctor with signature integration"""
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            crm = request.form.get('crm', '').strip()
            senha = request.form.get('senha', '')
            assinatura = request.form.get('assinatura', '')
            
            if not nome or not crm or not senha:
                flash('Nome, CRM e senha são obrigatórios.', 'error')
                return render_template('cadastro_medico.html')
            
            if not assinatura:
                flash('A assinatura digital é obrigatória para validação dos documentos médicos.', 'error')
                return render_template('cadastro_medico.html')
            
            # Check if CRM already exists
            existing_medico = Medico.query.filter_by(crm=crm).first()
            if existing_medico:
                flash('CRM já cadastrado no sistema!', 'error')
                return render_template('cadastro_medico.html')
            
            # Hash password and create new doctor
            senha_hash = generate_password_hash(senha)
            
            novo_medico = Medico(
                nome=nome,
                crm=crm,
                senha=senha_hash,
                assinatura=assinatura
            )
            
            db.session.add(novo_medico)
            db.session.commit()
            
            flash('Médico cadastrado com sucesso! Faça login para continuar.', 'success')
            logging.info(f'New doctor registered: {nome} (CRM: {crm})')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f'Doctor registration error: {e}')
            flash('Erro interno ao cadastrar médico. Tente novamente.', 'error')
    
    return render_template('cadastro_medico.html')
