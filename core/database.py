"""
Core database configuration - Sistema Médico VIDAH
Centraliza configuração do banco para evitar importações circulares
"""
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Instância global do banco
db = SQLAlchemy(model_class=Base)

def init_database(app):
    """Inicializa o banco de dados com a aplicação"""
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        'pool_pre_ping': True,
        "pool_recycle": 300,
    }
    
    db.init_app(app)
    return db