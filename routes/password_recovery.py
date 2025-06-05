from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash
from models import db, Medico
import secrets
import logging
from datetime import datetime, timedelta

password_recovery_bp = Blueprint('password_recovery', __name__)

# Armazenar tokens temporariamente (em produção, usar Redis ou banco)
recovery_tokens = {}

@password_recovery_bp.route('/esqueci-senha', methods=['GET', 'POST'])
def forgot_password():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    """Handle password recovery request"""
    if request.method == 'POST':
        try:
            crm = request.form.get('crm', '').strip()
            
            if not crm:
                flash('CRM é obrigatório.', 'error')
                return render_template('forgot_password.html')
            
            # Buscar médico pelo CRM
            medico = Medico.query.filter_by(crm=crm).first()
            
            if not medico:
                # Por segurança, não revelar se o CRM existe ou não
                flash('Se o CRM estiver cadastrado, você receberá instruções para redefinir sua senha.', 'info')
                return render_template('forgot_password.html')
            
            # Gerar token de recuperação
            token = secrets.token_urlsafe(32)
            recovery_tokens[token] = {
                'medico_id': medico.id,
                'expires': datetime.now() + timedelta(hours=1)  # Token válido por 1 hora
            }
            
            # Em um sistema real, enviaríamos email aqui
            # Por enquanto, vamos redirecionar diretamente para reset
            logging.info(f'Password recovery requested for CRM: {crm}')
            
            return redirect(url_for('password_recovery.reset_password', token=token))
            
        except Exception as e:
            logging.error(f'Password recovery error: {e}')
            flash('Erro interno. Tente novamente.', 'error')
    
    return render_template('forgot_password.html')

@password_recovery_bp.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    """Reset password with token"""
    # Verificar se token é válido
    if token not in recovery_tokens:
        flash('Token inválido ou expirado.', 'error')
        return redirect(url_for('auth.login'))
    
    token_data = recovery_tokens[token]
    
    # Verificar se token não expirou
    if datetime.now() > token_data['expires']:
        del recovery_tokens[token]
        flash('Token expirado. Solicite uma nova redefinição.', 'error')
        return redirect(url_for('password_recovery.forgot_password'))
    
    if request.method == 'POST':
        try:
            new_password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validações
            if not new_password or not confirm_password:
                flash('Todos os campos são obrigatórios.', 'error')
                return render_template('reset_password.html', token=token)
            
            if len(new_password) < 6:
                flash('A senha deve ter pelo menos 6 caracteres.', 'error')
                return render_template('reset_password.html', token=token)
            
            if new_password != confirm_password:
                flash('As senhas não coincidem.', 'error')
                return render_template('reset_password.html', token=token)
            
            # Buscar médico
            medico = Medico.query.get(token_data['medico_id'])
            if not medico:
                flash('Usuário não encontrado.', 'error')
                return redirect(url_for('auth.login'))
            
            # Atualizar senha
            medico.senha = generate_password_hash(new_password)
            db.session.commit()
            
            # Remover token usado
            del recovery_tokens[token]
            
            logging.info(f'Password reset successful for user: {medico.nome}')
            flash('Senha redefinida com sucesso! Faça login com sua nova senha.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            logging.error(f'Password reset error: {e}')
            flash('Erro ao redefinir senha. Tente novamente.', 'error')
    
    return render_template('reset_password.html', token=token)