from sqlalchemy import or_
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import Paciente
from app import db
from utils.db import insert_patient_if_not_exists
import logging

def sanitizar_entrada(valor):
    """Sanitiza entrada de usuário"""
    if not valor:
        return ""
    
    # Remove caracteres perigosos
    import re
    valor = re.sub(r'[<>"\']', '', str(valor))
    return valor.strip()


pacientes_bp = Blueprint('pacientes', __name__)

@pacientes_bp.route('/novo_paciente', methods=['GET', 'POST'])
def novo_paciente():
    """Register new patient"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        flash('Faça login para acessar esta página.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            nome_paciente = request.form.get('nome_paciente', '').strip()
            cpf_paciente = request.form.get('cpf_paciente', '').strip()
            idade_paciente = request.form.get('idade_paciente', '').strip()
            endereco_paciente = request.form.get('endereco_paciente', '').strip()
            cidade_uf_paciente = request.form.get('cidade_uf_paciente', '').strip()
            email_paciente = request.form.get('email_paciente', '').strip()
            telefone_paciente = request.form.get('telefone_paciente', '').strip()
            
            # Validate required fields
            if not nome_paciente:
                flash('Nome do paciente é obrigatório.', 'error')
                return render_template('novo_paciente.html')
            
            if not cpf_paciente:
                flash('CPF do paciente é obrigatório.', 'error')
                return render_template('novo_paciente.html', nome_paciente=nome_paciente)
            
            if not idade_paciente:
                flash('Idade do paciente é obrigatória.', 'error')
                return render_template('novo_paciente.html', nome_paciente=nome_paciente, cpf_paciente=cpf_paciente)
            
            if not endereco_paciente:
                flash('Endereço do paciente é obrigatório.', 'error')
                return render_template('novo_paciente.html', nome_paciente=nome_paciente, cpf_paciente=cpf_paciente, idade_paciente=idade_paciente)
            
            if not cidade_uf_paciente:
                flash('Cidade/UF do paciente é obrigatória.', 'error')
                return render_template('novo_paciente.html', nome_paciente=nome_paciente, cpf_paciente=cpf_paciente, idade_paciente=idade_paciente, endereco_paciente=endereco_paciente)
            
            # Check if patient already exists by name or CPF
            paciente_existente = Paciente.query.filter(
                (Paciente.nome == nome_paciente) | (Paciente.cpf == cpf_paciente)
            ).first()
            
            if paciente_existente:
                if paciente_existente.nome == nome_paciente:
                    flash(f'Paciente "{nome_paciente}" já está cadastrado no sistema.', 'warning')
                else:
                    flash(f'CPF "{cpf_paciente}" já está cadastrado no sistema.', 'warning')
                return render_template('novo_paciente.html', 
                                     nome_paciente=nome_paciente,
                                     cpf_paciente=cpf_paciente,
                                     idade_paciente=idade_paciente,
                                     endereco_paciente=endereco_paciente,
                                     cidade_uf_paciente=cidade_uf_paciente,
                                     email_paciente=email_paciente,
                                     telefone_paciente=telefone_paciente)
            
            # Convert age to integer
            try:
                idade_int = int(idade_paciente)
                if idade_int < 0 or idade_int > 120:
                    flash('Idade deve estar entre 0 e 120 anos.', 'error')
                    return render_template('novo_paciente.html', 
                                         nome_paciente=nome_paciente,
                                         cpf_paciente=cpf_paciente,
                                         idade_paciente=idade_paciente,
                                         endereco_paciente=endereco_paciente,
                                         cidade_uf_paciente=cidade_uf_paciente,
                                         email_paciente=email_paciente,
                                         telefone_paciente=telefone_paciente)
            except ValueError:
                flash('Idade deve ser um número válido.', 'error')
                return render_template('novo_paciente.html', 
                                     nome_paciente=nome_paciente,
                                     cpf_paciente=cpf_paciente,
                                     idade_paciente=idade_paciente,
                                     endereco_paciente=endereco_paciente,
                                     cidade_uf_paciente=cidade_uf_paciente,
                                     email_paciente=email_paciente,
                                     telefone_paciente=telefone_paciente)
            
            # Create new patient with all fields
            novo_paciente = Paciente(
                nome=nome_paciente,
                cpf=cpf_paciente,
                idade=idade_int,
                endereco=endereco_paciente,
                cidade_uf=cidade_uf_paciente,
                email=email_paciente if email_paciente else None,
                telefone=telefone_paciente if telefone_paciente else None
            )
            
            db.session.add(novo_paciente)
            db.session.commit()
            
            flash(f'Paciente "{nome_paciente}" cadastrado com sucesso!', 'success')
            logging.info(f'New patient registered: {nome_paciente} (Email: {email_paciente}, Tel: {telefone_paciente})')
            
            # Store last patient info in session for auto-fill
            session['ultimo_paciente'] = {
                'id': novo_paciente.id,
                'nome': nome_paciente
            }
            
            # Stay on the same page after successful registration
            return render_template('novo_paciente.html')
            
        except Exception as e:
            logging.error(f'Patient registration error: {e}')
            flash('Erro ao cadastrar paciente. Tente novamente.', 'error')
    
    return render_template('novo_paciente.html')