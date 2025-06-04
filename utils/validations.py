"""
Validações extras para robustez do sistema
"""

import re
from datetime import datetime

def validar_cpf(cpf):
    """Valida formato de CPF"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    return len(cpf) == 11 and cpf != cpf[0] * 11

def validar_crm(crm):
    """Valida formato de CRM"""
    return len(crm.strip()) >= 4 and crm.strip().replace('-', '').replace('/', '').isalnum()

def validar_data(data_str):
    """Valida formato de data"""
    try:
        datetime.strptime(data_str, '%d/%m/%Y')
        return True
    except:
        return False

def sanitizar_texto(texto):
    """Sanitiza texto removendo caracteres perigosos"""
    if not texto:
        return ""
    
    # Remove scripts e tags perigosas
    texto = re.sub(r'<script.*?</script>', '', texto, flags=re.IGNORECASE | re.DOTALL)
    texto = re.sub(r'javascript:', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'on\w+\s*=', '', texto, flags=re.IGNORECASE)
    
    return texto.strip()
