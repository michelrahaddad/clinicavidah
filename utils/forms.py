import re
from datetime import datetime

def sanitizar_entrada(texto):
    """Sanitize input text"""
    if not texto:
        return ""
    return str(texto).strip()

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
