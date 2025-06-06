"""
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
