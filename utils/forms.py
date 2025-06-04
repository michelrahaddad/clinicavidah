import re
from datetime import datetime

def validar_cpf(cpf):
    """Validate CPF format - accepts any numeric sequence"""
    if not cpf:
        return False
    
    # Remove non-numeric characters
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Accept any numeric sequence between 8-11 digits
    return len(cpf) >= 8 and len(cpf) <= 11

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

def validar_email(email):
    """Validate email format"""
    if not email:
        return True  # Email is optional
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_telefone(telefone):
    """Validate phone number format"""
    if not telefone:
        return True  # Phone is optional
    
    # Remove non-numeric characters
    telefone = re.sub(r'[^0-9]', '', telefone)
    
    # Brazilian phone format: 10 or 11 digits
    return len(telefone) in [10, 11]

def validar_crm(crm):
    """Validate CRM format"""
    if not crm:
        return False
    
    # CRM should have at least 4 digits and letters for state
    pattern = r'^\d{4,6}\/[A-Z]{2}$'
    return re.match(pattern, crm.upper()) is not None

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
