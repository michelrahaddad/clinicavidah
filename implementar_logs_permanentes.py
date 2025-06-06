"""
Implementação de logs permanentes em todos os pontos críticos do sistema
Para monitoramento contínuo e diagnóstico de problemas
"""

def implementar_logs_completos():
    """Implementa sistema de logs completo e permanente"""
    
    # 1. Configurar sistema de logging centralizado
    criar_sistema_logging()
    
    # 2. Adicionar logs nas rotas principais
    adicionar_logs_rotas()
    
    # 3. Adicionar logs no sistema de autenticação
    adicionar_logs_auth()
    
    # 4. Adicionar logs no acesso ao banco
    adicionar_logs_database()
    
    # 5. Adicionar logs nas operações médicas
    adicionar_logs_medical()
    
    # 6. Criar middleware de auditoria
    criar_middleware_auditoria()

def criar_sistema_logging():
    """Cria sistema de logging centralizado"""
    
    logging_config = '''"""
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
'''

    with open('core/logging_config.py', 'w', encoding='utf-8') as f:
        f.write(logging_config)

def adicionar_logs_rotas():
    """Adiciona logs em todas as rotas principais"""
    
    # Logs no app principal
    with open('app_modular_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Adicionar import do sistema de logging
    if 'from core.logging_config import' not in content:
        import_line = 'from core.logging_config import auth_logger, dashboard_logger, audit_logger, log_user_action\n'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'from datetime import timedelta' in line:
                lines.insert(i + 1, import_line)
                break
        content = '\n'.join(lines)
    
    # Adicionar logs nas rotas principais
    route_patterns = [
        ('@app.route(\'/\')', 'log_user_action(session.get("usuario", {}), "ACCESS_HOME")'),
        ('@app.route(\'/dashboard\')', 'log_user_action(session.get("usuario", {}), "ACCESS_DASHBOARD")'),
        ('def health_check():', 'audit_logger.info("Health check accessed")')
    ]
    
    for pattern, log_line in route_patterns:
        if pattern in content:
            content = content.replace(
                pattern,
                f'{pattern}\n    {log_line}'
            )
    
    with open('app_modular_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)

def adicionar_logs_auth():
    """Adiciona logs permanentes no sistema de autenticação"""
    
    with open('auth_simple.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Adicionar imports
    if 'from core.logging_config import' not in content:
        import_line = 'from core.logging_config import auth_logger, security_logger, log_user_action, log_security_event\n'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'import logging' in line:
                lines.insert(i + 1, import_line)
                break
        content = '\n'.join(lines)
    
    # Adicionar logs específicos
    auth_patterns = [
        ('nome = request.form.get(\'nome\', \'\').strip()', 'auth_logger.info(f"Login attempt: {nome}")'),
        ('medico = db.session.query(Medico)', 'auth_logger.debug(f"Searching for doctor: {nome}, CRM: {crm}")'),
        ('if medico and check_password_hash', 'auth_logger.info(f"Doctor found: {medico.nome if medico else None}")'),
        ('session[\'usuario\'] = {', 'auth_logger.info(f"Successful login: {nome}"); log_user_action({"nome": nome, "crm": crm}, "LOGIN")'),
        ('flash(\'Credenciais inválidas\'', 'auth_logger.warning(f"Failed login attempt: {nome}"); log_security_event("FAILED_LOGIN", {"nome": nome}, f"Invalid credentials for {nome}")')
    ]
    
    for pattern, log_line in auth_patterns:
        if pattern in content:
            content = content.replace(
                pattern,
                f'{log_line}\n            {pattern}'
            )
    
    with open('auth_simple.py', 'w', encoding='utf-8') as f:
        f.write(content)

def adicionar_logs_database():
    """Adiciona logs nas operações de banco de dados"""
    
    database_middleware = '''"""
Middleware de logging para operações de banco de dados
"""
from core.logging_config import database_logger, log_database_operation
from flask import session
from sqlalchemy import event
from core.database import db

def setup_database_logging():
    """Configura logging automático para operações de banco"""
    
    @event.listens_for(db.session, 'before_insert')
    def log_before_insert(mapper, connection, target):
        user = session.get('usuario', {})
        table_name = target.__tablename__
        log_database_operation('INSERT', table_name, user, f"New record in {table_name}")
    
    @event.listens_for(db.session, 'before_update')  
    def log_before_update(mapper, connection, target):
        user = session.get('usuario', {})
        table_name = target.__tablename__
        log_database_operation('UPDATE', table_name, user, f"Updated record in {table_name}")
    
    @event.listens_for(db.session, 'before_delete')
    def log_before_delete(mapper, connection, target):
        user = session.get('usuario', {})
        table_name = target.__tablename__
        log_database_operation('DELETE', table_name, user, f"Deleted record from {table_name}")
'''
    
    # Criar diretório core se não existir
    import os
    os.makedirs('core', exist_ok=True)
    
    with open('core/database_logging.py', 'w', encoding='utf-8') as f:
        f.write(database_middleware)

def adicionar_logs_medical():
    """Adiciona logs nas operações médicas"""
    
    with open('routes/medical.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Adicionar imports
    if 'from core.logging_config import' not in content:
        import_line = 'from core.logging_config import medical_logger, log_user_action, log_database_operation\n'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'import json' in line:
                lines.insert(i + 1, import_line)
                break
        content = '\n'.join(lines)
    
    # Adicionar logs nas operações médicas
    medical_patterns = [
        ('@medical_bp.route(\'/receitas\')', 'log_user_action(session["usuario"], "VIEW_RECEITAS")'),
        ('@medical_bp.route(\'/receitas/nova\')', 'log_user_action(session["usuario"], "CREATE_RECEITA")'),
        ('db.session.add(receita)', 'medical_logger.info(f"New receita created for patient: {receita.nome_paciente}"); log_database_operation("INSERT", "receitas", session["usuario"], f"Receita for {receita.nome_paciente}")'),
        ('@medical_bp.route(\'/exames-lab\')', 'log_user_action(session["usuario"], "VIEW_EXAMES_LAB")'),
        ('@medical_bp.route(\'/pacientes\')', 'log_user_action(session["usuario"], "VIEW_PACIENTES")')
    ]
    
    for pattern, log_line in medical_patterns:
        if pattern in content:
            content = content.replace(
                pattern,
                f'{pattern}\n    {log_line}'
            )
    
    with open('routes/medical.py', 'w', encoding='utf-8') as f:
        f.write(content)

def criar_middleware_auditoria():
    """Cria middleware de auditoria para todas as requisições"""
    
    middleware_content = '''"""
Middleware de auditoria - Sistema Médico VIDAH
"""
from flask import request, session, g
from core.logging_config import audit_logger, security_logger
from datetime import datetime
import time

def setup_audit_middleware(app):
    """Configura middleware de auditoria"""
    
    @app.before_request
    def log_request():
        """Log de todas as requisições"""
        g.start_time = time.time()
        user = session.get('usuario', {})
        user_info = f"{user.get('nome', 'Anonymous')} ({user.get('tipo', 'guest')})"
        
        audit_logger.info(
            f"Request: {request.method} {request.path} - "
            f"User: {user_info} - "
            f"IP: {request.remote_addr} - "
            f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
        )
        
        # Log tentativas de acesso sem autenticação em rotas protegidas
        protected_routes = ['/dashboard', '/medical', '/receitas', '/exames']
        if any(request.path.startswith(route) for route in protected_routes):
            if 'usuario' not in session:
                security_logger.warning(
                    f"Unauthorized access attempt to {request.path} from {request.remote_addr}"
                )
    
    @app.after_request
    def log_response(response):
        """Log de respostas"""
        duration = time.time() - g.start_time
        user = session.get('usuario', {})
        user_info = f"{user.get('nome', 'Anonymous')}"
        
        audit_logger.info(
            f"Response: {response.status_code} - "
            f"Duration: {duration:.3f}s - "
            f"User: {user_info} - "
            f"Path: {request.path}"
        )
        
        # Log erros críticos
        if response.status_code >= 500:
            security_logger.error(
                f"Server error {response.status_code} on {request.path} "
                f"for user {user_info}"
            )
        
        return response
'''
    
    with open('core/audit_middleware.py', 'w', encoding='utf-8') as f:
        f.write(middleware_content)

def executar_implementacao():
    """Executa toda a implementação de logs permanentes"""
    print("=== IMPLEMENTANDO LOGS PERMANENTES ===")
    
    import os
    os.makedirs('core', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    implementar_logs_completos()
    
    print("\n=== LOGS PERMANENTES IMPLEMENTADOS ===")
    print("✓ Sistema de logging centralizado")
    print("✓ Logs nas rotas principais")
    print("✓ Logs no sistema de autenticação")
    print("✓ Logs nas operações de banco")
    print("✓ Logs nas operações médicas")
    print("✓ Middleware de auditoria")
    print("✓ Logs salvos em arquivos rotativos")
    print("\nSistema com monitoramento completo!")

if __name__ == '__main__':
    executar_implementacao()