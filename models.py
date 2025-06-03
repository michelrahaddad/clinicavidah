from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class Medico(db.Model):
    __tablename__ = 'medicos'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    crm = Column(String(20), unique=True, nullable=False)
    senha = Column(String(256), nullable=False)
    assinatura = Column(Text, nullable=True)  # Base64 encoded signature
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    receitas = relationship('Receita', back_populates='medico', lazy=True)
    exames_lab = relationship('ExameLab', back_populates='medico', lazy=True)
    exames_img = relationship('ExameImg', back_populates='medico', lazy=True)
    agendamentos = relationship('Agendamento', back_populates='medico', lazy=True)
    prontuarios = relationship('Prontuario', back_populates='medico', lazy=True)
    relatorios = relationship('RelatorioMedico', back_populates='medico', lazy=True)
    atestados = relationship('AtestadoMedico', back_populates='medico', lazy=True)
    formularios_alto_custo = relationship('FormularioAltoCusto', back_populates='medico', lazy=True)

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    cpf = Column(String(14), nullable=True)  # Format: 000.000.000-00
    email = Column(String(255), nullable=True)
    telefone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    receitas = relationship('Receita', back_populates='paciente', lazy=True)
    exames_lab = relationship('ExameLab', back_populates='paciente', lazy=True)
    exames_img = relationship('ExameImg', back_populates='paciente', lazy=True)
    agendamentos = relationship('Agendamento', back_populates='paciente_obj', lazy=True)
    prontuarios = relationship('Prontuario', back_populates='paciente', lazy=True)
    relatorios = relationship('RelatorioMedico', back_populates='paciente', lazy=True)
    atestados = relationship('AtestadoMedico', back_populates='paciente', lazy=True)
    formularios_alto_custo = relationship('FormularioAltoCusto', back_populates='paciente', lazy=True)

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


class Cid10(db.Model):
    __tablename__ = 'cid10'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(10), unique=True, nullable=False)
    descricao = Column(Text, nullable=False)
    categoria = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RelatorioMedico(db.Model):
    __tablename__ = 'relatorios_medicos'
    
    id = Column(Integer, primary_key=True)
    nome_paciente = Column(String(200), nullable=False)
    cid_codigo = Column(String(10), nullable=False)
    cid_descricao = Column(Text, nullable=False)
    relatorio_texto = Column(Text, nullable=False)
    medico_nome = Column(String(200), nullable=False)
    data = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    id_paciente = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    id_medico = Column(Integer, ForeignKey('medicos.id'), nullable=False)
    
    # Relationships
    paciente = relationship('Paciente', back_populates='relatorios')
    medico = relationship('Medico', back_populates='relatorios')


class AtestadoMedico(db.Model):
    __tablename__ = 'atestados_medicos'
    
    id = Column(Integer, primary_key=True)
    nome_paciente = Column(String(200), nullable=False)
    cid_codigo = Column(String(10), nullable=False)
    cid_descricao = Column(Text, nullable=False)
    dias_afastamento = Column(Integer, nullable=False)
    data_inicio = Column(String(10), nullable=False)
    data_fim = Column(String(10), nullable=False)
    medico_nome = Column(String(200), nullable=False)
    data = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    id_paciente = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    id_medico = Column(Integer, ForeignKey('medicos.id'), nullable=False)
    
    # Relationships
    paciente = relationship('Paciente', back_populates='atestados')
    medico = relationship('Medico', back_populates='atestados')


class FormularioAltoCusto(db.Model):
    __tablename__ = 'formularios_alto_custo'
    
    id = Column(Integer, primary_key=True)
    cnes = Column(String(20), nullable=True)
    estabelecimento = Column(String(300), nullable=True)
    nome_paciente = Column(String(200), nullable=False)
    nome_mae = Column(String(200), nullable=False)
    peso = Column(String(10), nullable=False)
    altura = Column(String(10), nullable=False)
    medicamento = Column(Text, nullable=False)
    quantidade = Column(Text, nullable=False)
    cid_codigo = Column(String(10), nullable=False)
    cid_descricao = Column(Text, nullable=False)
    anamnese = Column(Text, nullable=False)
    tratamento_previo = Column(Text, nullable=True)
    incapaz = Column(Boolean, default=False)
    responsavel_nome = Column(String(200), nullable=True)
    medico_nome = Column(String(200), nullable=False)
    medico_cns = Column(String(20), nullable=True)
    data = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    id_paciente = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    id_medico = Column(Integer, ForeignKey('medicos.id'), nullable=False)
    
    # Relationships
    paciente = relationship('Paciente', back_populates='formularios_alto_custo')
    medico = relationship('Medico', back_populates='formularios_alto_custo')
