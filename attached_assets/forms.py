from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, ValidationError
from datetime import datetime
import re

class LoginForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    crm = StringField('CRM', validators=[DataRequired(), Length(min=3, max=20)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Entrar')

class MedicoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    crm = StringField('CRM', validators=[DataRequired(), Length(min=3, max=20)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Cadastrar')
    
    def validate_crm(self, field):
        """Validate CRM format"""
        crm_pattern = r'^[A-Za-z0-9]+$'
        if not re.match(crm_pattern, field.data):
            raise ValidationError('CRM deve conter apenas letras e números.')

class AgendaForm(FlaskForm):
    data = DateField('Data', validators=[DataRequired()])
    paciente = StringField('Paciente', validators=[DataRequired(), Length(min=2, max=100)])
    motivo = TextAreaField('Motivo', validators=[Length(max=500)])
    submit = SubmitField('Agendar')
    
    def validate_data(self, field):
        """Validate appointment date"""
        if field.data < datetime.now().date():
            raise ValidationError('Data do agendamento não pode ser no passado.')

def validar_data(data_str):
    """Validate date string format"""
    try:
        datetime.strptime(data_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def sanitizar_entrada(texto):
    """Sanitize text input"""
    if not texto:
        return ""
    return texto.strip()

def validar_medicamentos(medicamentos, posologias, duracoes, vias):
    """Validate prescription data"""
    if not all([medicamentos, posologias, duracoes, vias]):
        return False, "Todos os campos de medicamentos são obrigatórios."
    
    if len(medicamentos) != len(posologias) or len(medicamentos) != len(duracoes) or len(medicamentos) != len(vias):
        return False, "Número de medicamentos, posologias, durações e vias deve ser igual."
    
    for i, med in enumerate(medicamentos):
        if not med.strip() or not posologias[i].strip() or not duracoes[i].strip() or not vias[i].strip():
            return False, f"Medicamento {i+1} tem campos em branco."
    
    return True, "Validação bem-sucedida."
