from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import Paciente
from app import db
from utils.db import insert_patient_if_not_exists
import logging

pacientes_bp = Blueprint('pacientes', __name__)

@pacientes_bp.route('/novo_paciente', methods=['GET', 'POST'])
def novo_paciente():
    """Register new patient"""
    if 'usuario' not in session:
        flash('Faça login para acessar esta página.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            nome_paciente = request.form.get('nome_paciente', '').strip()
            email_paciente = request.form.get('email_paciente', '').strip()
            telefone_paciente = request.form.get('telefone_paciente', '').strip()
            
            if not nome_paciente:
                flash('Nome do paciente é obrigatório.', 'error')
                return render_template('novo_paciente.html')
            
            # Check if patient already exists
            paciente_existente = Paciente.query.filter_by(nome=nome_paciente).first()
            if paciente_existente:
                flash(f'Paciente "{nome_paciente}" já está cadastrado no sistema.', 'warning')
                return render_template('novo_paciente.html', nome_paciente=nome_paciente)
            
            # Create new patient with all fields
            novo_paciente = Paciente(
                nome=nome_paciente,
                email=email_paciente if email_paciente else None,
                telefone=telefone_paciente if telefone_paciente else None
            )
            
            db.session.add(novo_paciente)
            db.session.commit()
            
            flash(f'Paciente "{nome_paciente}" cadastrado com sucesso!', 'success')
            logging.info(f'New patient registered: {nome_paciente} (Email: {email_paciente}, Tel: {telefone_paciente})')
            
            # Redirect to prontuario with patient name
            return redirect(url_for('prontuario.prontuario', paciente=nome_paciente))
            
        except Exception as e:
            logging.error(f'Patient registration error: {e}')
            flash('Erro ao cadastrar paciente. Tente novamente.', 'error')
    
    return render_template('novo_paciente.html')