from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Medico(db.Model):
    __tablename__ = 'medicos'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    crm = Column(String(20), unique=True, nullable=False)
    senha = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    receitas = relationship('Receita', back_populates='medico', lazy=True)
    exames_lab = relationship('ExameLab', back_populates='medico', lazy=True)
    exames_img = relationship('ExameImg', back_populates='medico', lazy=True)
    agendamentos = relationship('Agendamento', back_populates='medico', lazy=True)
    prontuarios = relationship('Prontuario', back_populates='medico', lazy=True)

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    receitas = relationship('Receita', back_populates='paciente', lazy=True)
    exames_lab = relationship('ExameLab', back_populates='paciente', lazy=True)
    exames_img = relationship('ExameImg', back_populates='paciente', lazy=True)
    agendamentos = relationship('Agendamento', back_populates='paciente_obj', lazy=True)
    prontuarios = relationship('Prontuario', back_populates='paciente', lazy=True)

class Receita(db.Model):
    __tablename__ = 'receitas'
    
    id = Column(Integer, primary_key=True)
    nome_paciente = Column(String(200), nullable=False)
    medicamentos = Column(Text, nullable=False)
    posologias = Column(Text, nullable=False)
    duracoes = Column(Text, nullable=False)
    vias = Column(Text, nullable=False)
    medico_nome = Column(String(200), nullable=False)
    data = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    id_paciente = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    id_medico = Column(Integer, ForeignKey('medicos.id'), nullable=False)
    
    # Relationships
    paciente = relationship('Paciente', back_populates='receitas')
    medico = relationship('Medico', back_populates='receitas')

class ExameLab(db.Model):
    __tablename__ = 'exames_lab'
    
    id = Column(Integer, primary_key=True)
    nome_paciente = Column(String(200), nullable=False)
    exames = Column(Text, nullable=False)
    medico_nome = Column(String(200), nullable=False)
    data = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    id_paciente = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    id_medico = Column(Integer, ForeignKey('medicos.id'), nullable=False)
    
    # Relationships
    paciente = relationship('Paciente', back_populates='exames_lab')
    medico = relationship('Medico', back_populates='exames_lab')

class ExameImg(db.Model):
    __tablename__ = 'exames_img'
    
    id = Column(Integer, primary_key=True)
    nome_paciente = Column(String(200), nullable=False)
    exames = Column(Text, nullable=False)
    medico_nome = Column(String(200), nullable=False)
    data = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    id_paciente = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    id_medico = Column(Integer, ForeignKey('medicos.id'), nullable=False)
    
    # Relationships
    paciente = relationship('Paciente', back_populates='exames_img')
    medico = relationship('Medico', back_populates='exames_img')

class Agendamento(db.Model):
    __tablename__ = 'agenda'
    
    id = Column(Integer, primary_key=True)
    data = Column(String(10), nullable=False)
    paciente = Column(String(200), nullable=False)
    motivo = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    id_paciente = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    id_medico = Column(Integer, ForeignKey('medicos.id'), nullable=False)
    
    # Relationships
    paciente_obj = relationship('Paciente', back_populates='agendamentos')
    medico = relationship('Medico', back_populates='agendamentos')

class Prontuario(db.Model):
    __tablename__ = 'prontuario'
    
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)  # 'receita', 'exame_lab', 'exame_img'
    id_registro = Column(Integer, nullable=False)
    data = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    id_paciente = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    id_medico = Column(Integer, ForeignKey('medicos.id'), nullable=False)
    
    # Relationships
    paciente = relationship('Paciente', back_populates='prontuarios')
    medico = relationship('Medico', back_populates='prontuarios')
