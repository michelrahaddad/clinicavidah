"""
Sistema de logging centralizado - Sistema Médico VIDAH
"""
import logging
import logging.handlers
import os
from datetime import datetime

# Configurar formatadores
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)

# Configurar handlers
def setup_logger(name, log_file, level=logging.INFO):
    """Configura logger específico"""
    
    # Criar diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)
    
    # Handler para arquivo
    file_handler = logging.handlers.RotatingFileHandler(
        f'logs/{log_file}', 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Loggers específicos do sistema
auth_logger = setup_logger('auth', 'auth.log')
dashboard_logger = setup_logger('dashboard', 'dashboard.log')
medical_logger = setup_logger('medical', 'medical.log')
database_logger = setup_logger('database', 'database.log')
security_logger = setup_logger('security', 'security.log')
audit_logger = setup_logger('audit', 'audit.log')

def log_user_action(user, action, details=None):
    """Log de ações do usuário para auditoria"""
    message = f"User: {user.get('nome', 'Unknown')} ({user.get('tipo', 'Unknown')}) - Action: {action}"
    if details:
        message += f" - Details: {details}"
    audit_logger.info(message)

def log_database_operation(operation, table, user, details=None):
    """Log de operações no banco de dados"""
    message = f"DB Operation: {operation} on {table} by {user.get('nome', 'Unknown')}"
    if details:
        message += f" - {details}"
    database_logger.info(message)

def log_security_event(event_type, user, details):
    """Log de eventos de segurança"""
    message = f"Security Event: {event_type} - User: {user.get('nome', 'Unknown')} - {details}"
    security_logger.warning(message)
