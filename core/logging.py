"""
Sistema de logging centralizado para o Sistema Médico VIDAH
"""
import logging
import logging.handlers
import os
from datetime import datetime


class VidahLogger:
    """Logger centralizado do sistema médico"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o sistema de logging com a aplicação Flask"""
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
        log_format = app.config.get('LOG_FORMAT', 
                                   '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Configurar logging básico
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                self._get_file_handler() if not app.config.get('TESTING') else logging.NullHandler()
            ]
        )
        
        # Logger principal do sistema
        self.logger = logging.getLogger('vidah')
        self.logger.setLevel(log_level)
        
        # Loggers específicos por módulo
        self.auth_logger = logging.getLogger('vidah.auth')
        self.prescription_logger = logging.getLogger('vidah.prescription')
        self.patient_logger = logging.getLogger('vidah.patient')
        self.exam_logger = logging.getLogger('vidah.exam')
        self.security_logger = logging.getLogger('vidah.security')
        
        app.logger = self.logger
    
    def _get_file_handler(self):
        """Cria handler para arquivo de log com rotação"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/vidah.log',
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        return file_handler
    
    def log_user_action(self, user_id, action, details=None):
        """Log de ações do usuário para auditoria"""
        self.logger.info(f"USER_ACTION - ID: {user_id}, Action: {action}, Details: {details}")
    
    def log_security_event(self, event_type, details):
        """Log de eventos de segurança"""
        self.security_logger.warning(f"SECURITY_EVENT - Type: {event_type}, Details: {details}")
    
    def log_prescription_event(self, doctor_id, patient_id, action):
        """Log específico para prescrições"""
        self.prescription_logger.info(f"PRESCRIPTION - Doctor: {doctor_id}, Patient: {patient_id}, Action: {action}")
    
    def log_exam_event(self, doctor_id, patient_id, exam_type, action):
        """Log específico para exames"""
        self.exam_logger.info(f"EXAM - Doctor: {doctor_id}, Patient: {patient_id}, Type: {exam_type}, Action: {action}")
    
    def log_database_operation(self, operation, table, record_id=None):
        """Log de operações no banco de dados"""
        self.logger.debug(f"DB_OPERATION - Operation: {operation}, Table: {table}, ID: {record_id}")


# Instância global do logger
vidah_logger = VidahLogger()


def get_logger(name=None):
    """Função helper para obter logger"""
    if name:
        return logging.getLogger(f'vidah.{name}')
    return logging.getLogger('vidah')


# Decorador para logging automático
def log_action(action_name):
    """Decorador para logging automático de ações"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger()
            logger.info(f"Starting {action_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {action_name}")
                return result
            except Exception as e:
                logger.error(f"Error in {action_name}: {str(e)}")
                raise
        return wrapper
    return decorator