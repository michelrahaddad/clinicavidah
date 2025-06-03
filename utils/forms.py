import re
from datetime import datetime

def validar_cpf(cpf):
    """Validate CPF format and check digit"""
    if not cpf:
        return False
    
    # Remove non-numeric characters
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Must have 11 digits
    if len(cpf) != 11:
        return False
    
    # Check for known invalid CPFs
    if cpf == cpf[0] * 11:
        return False
    
    # Calculate check digits
    def calculate_check_digit(cpf_digits, weight):
        total = sum(int(digit) * weight for digit, weight in zip(cpf_digits, range(weight, 1, -1)))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
    
    # Validate first check digit
    first_check = calculate_check_digit(cpf[:9], 10)
    if int(cpf[9]) != first_check:
        return False
    
    # Validate second check digit
    second_check = calculate_check_digit(cpf[:10], 11)
    if int(cpf[10]) != second_check:
        return False
    
    return True

def format_cpf(cpf):
    """Format CPF with dots and dash"""
    if not cpf:
        return ""
    
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
    return cpf

def sanitizar_entrada(texto):
    """Sanitize input text with enhanced security"""
    if not texto:
        return ""
    
    # Convert to string and strip whitespace
    texto = str(texto).strip()
    
    # Remove potentially dangerous characters
    texto = re.sub(r'[<>\"\'%;()&+]', '', texto)
    
    # Remove script tags and other dangerous patterns
    texto = re.sub(r'<script.*?</script>', '', texto, flags=re.IGNORECASE | re.DOTALL)
    texto = re.sub(r'javascript:', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'on\w+\s*=', '', texto, flags=re.IGNORECASE)
    
    return texto

def validar_data(data_str):
    """Validate date format YYYY-MM-DD"""
    try:
        datetime.strptime(data_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validar_medicamentos(medicamentos, posologias, duracoes, vias):
    """Validate medication fields"""
    if not medicamentos or len(medicamentos) == 0:
        return False, "É necessário pelo menos um medicamento."
    
    # Check if all arrays have the same length
    if not (len(medicamentos) == len(posologias) == len(duracoes) == len(vias)):
        return False, "Todos os campos de medicamento devem ser preenchidos."
    
    # Check if any field is empty
    for i in range(len(medicamentos)):
        if not medicamentos[i] or not posologias[i] or not duracoes[i] or not vias[i]:
            return False, f"Todos os campos do medicamento {i+1} devem ser preenchidos."
    
    return True, ""

class LoginForm:
    """Simple form class for backward compatibility"""
    def __init__(self):
        self.nome = None
        self.crm = None
        self.senha = None
    
    def validate_on_submit(self):
        return True

class MedicoForm:
    """Simple form class for backward compatibility"""
    def __init__(self):
        self.nome = None
        self.crm = None
        self.senha = None
    
    def validate_on_submit(self):
        return True
