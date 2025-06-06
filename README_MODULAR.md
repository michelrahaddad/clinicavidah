# Sistema Médico VIDAH - Estrutura Modular

## Arquitetura Organizada por Módulos

### 📁 Estrutura de Diretórios

```
sistema-medico-vidah/
├── config.py                 # Configurações centralizadas
├── app_modular.py            # Aplicação principal modernizada
├── main.py                   # Ponto de entrada
├── models.py                 # Modelos de dados existentes
│
├── core/                     # Componentes centrais
│   ├── __init__.py
│   └── logging.py           # Sistema de logging centralizado
│
├── validators/              # Sistema de validação
│   ├── __init__.py
│   ├── base.py             # Validadores base e utilitários
│   └── medical.py          # Validadores específicos médicos
│
├── blueprints/             # Módulos de rotas organizados
│   ├── __init__.py
│   └── auth.py            # Autenticação e autorização
│
├── services/              # Serviços de negócio
│   ├── __init__.py
│   └── pdf_service.py    # Geração de PDFs médicos
│
├── routes/               # Blueprints existentes (compatibilidade)
├── templates/           # Templates HTML
├── static/             # Arquivos estáticos
└── utils/              # Utilitários diversos
```

## 🔧 Componentes Principais

### 1. Sistema de Configuração (`config.py`)

- Configurações centralizadas por ambiente (desenvolvimento, produção, teste)
- Configurações de logging, segurança e sistema médico
- Separação clara entre diferentes ambientes

### 2. Logging Centralizado (`core/logging.py`)

```python
# Uso básico
from core.logging import get_logger, log_action

logger = get_logger('modulo_name')
logger.info("Mensagem de log")

# Decorador para logging automático
@log_action('criar_receita')
def criar_receita():
    pass
```

**Características:**
- Logs estruturados por módulo
- Rotação automática de arquivos
- Logs de auditoria para ações médicas
- Diferentes níveis por ambiente

### 3. Sistema de Validação (`validators/`)

```python
# Validadores base
from validators.base import StringValidator, CPFValidator
from validators.medical import get_validator

# Validação simples
cpf_validator = CPFValidator()
cpf_valido = cpf_validator.validate("123.456.789-00")

# Validação completa de prescrição
validator = get_validator('prescription')
dados_validados = validator.validate(dados_receita)
```

**Validadores Disponíveis:**
- `StringValidator`: Strings com tamanho e padrão
- `EmailValidator`: Emails válidos
- `CPFValidator`: CPF com dígitos verificadores
- `CRMValidator`: CRM no formato correto
- `PrescriptionValidator`: Validação completa de receitas
- `PatientValidator`: Dados de pacientes
- `ExamValidator`: Solicitações de exames

### 4. Blueprints Modulares (`blueprints/`)

```python
# Decoradores de autenticação
from blueprints.auth import require_auth, require_admin, require_doctor

@require_doctor
def criar_receita():
    pass

@require_admin
def gerenciar_usuarios():
    pass
```

**Funcionalidades:**
- Autenticação segura com sessões
- Autorização baseada em roles
- Registro de novos médicos (apenas admins)
- Gestão de perfis

### 5. Serviços de Negócio (`services/`)

```python
# Geração de PDFs médicos
from services.pdf_service import generate_prescription_pdf

pdf_bytes = generate_prescription_pdf({
    'nome_paciente': 'João Silva',
    'medicamentos': ['Dipirona 500mg'],
    'medico_nome': 'Dr. Michel'
})
```

**Serviços Disponíveis:**
- `PDFService`: Geração de PDFs com assinatura digital
- Limpeza automática de arquivos temporários
- Processamento de assinaturas para visibilidade
- Templates específicos por tipo de documento

## 🛡️ Recursos de Segurança

### Headers de Segurança
- `X-Frame-Options`: Prevenção de clickjacking
- `X-Content-Type-Options`: Prevenção de MIME sniffing
- `X-XSS-Protection`: Proteção contra XSS
- `Content-Security-Policy`: Política de conteúdo
- `Strict-Transport-Security`: HTTPS obrigatório

### Validação e Sanitização
- Sanitização automática de entradas
- Validação rigorosa de dados médicos
- Prevenção de injeção SQL e XSS

### Auditoria
- Log de todas as ações de usuários
- Rastreamento de operações médicas
- Monitoramento de eventos de segurança

## 📊 Logging e Monitoramento

### Níveis de Log
- `DEBUG`: Informações detalhadas para desenvolvimento
- `INFO`: Operações normais do sistema
- `WARNING`: Situações que requerem atenção
- `ERROR`: Erros que afetam funcionalidades

### Logs Específicos
```python
# Log de ações médicas
vidah_logger.log_prescription_event(doctor_id, patient_id, 'created')

# Log de eventos de segurança
vidah_logger.log_security_event('failed_login', {'user': 'test'})

# Log de operações no banco
vidah_logger.log_database_operation('INSERT', 'receitas', receita_id)
```

## 🚀 Como Usar

### 1. Modo de Compatibilidade
O sistema atual continua funcionando normalmente através do `app.py` existente.

### 2. Modo Modular
Para usar a nova estrutura:

```python
# Use app_modular.py como ponto de entrada
from app_modular import create_app

app = create_app('development')  # ou 'production'
```

### 3. Desenvolvimento de Novos Módulos

```python
# Criar novo blueprint
from flask import Blueprint
from blueprints.auth import require_doctor
from validators.medical import get_validator

new_module = Blueprint('new_module', __name__)

@new_module.route('/exemplo')
@require_doctor
def exemplo():
    validator = get_validator('prescription')
    # Lógica do módulo
    pass
```

## 🔄 Migração Gradual

A estrutura foi projetada para migração gradual:

1. **Fase 1**: Sistema atual continua funcionando
2. **Fase 2**: Novos módulos usam a estrutura modular
3. **Fase 3**: Migração gradual dos módulos existentes
4. **Fase 4**: Substituição completa para app_modular.py

## 📈 Benefícios

### Manutenibilidade
- Código organizado por responsabilidade
- Separação clara de concerns
- Fácil localização de bugs

### Escalabilidade
- Adicionar novos módulos sem afetar existentes
- Configuração flexível por ambiente
- Estrutura preparada para crescimento

### Segurança
- Validação consistente em todo o sistema
- Logging de auditoria automático
- Headers de segurança padronizados

### Qualidade
- Validação rigorosa de dados
- Tratamento consistente de erros
- Logs estruturados para debugging

## 🛠️ Exemplos de Uso

### Criando Nova Funcionalidade

```python
# 1. Criar validador específico
class NovoValidator(CompositeValidator):
    def __init__(self):
        validators = {
            'campo': StringValidator(min_length=2)
        }
        super().__init__(validators)

# 2. Criar blueprint
@novo_bp.route('/criar', methods=['POST'])
@require_doctor
@log_action('criar_documento')
def criar_documento():
    validator = NovoValidator()
    dados = validator.validate(request.form.to_dict())
    # Processar dados validados
    
# 3. Gerar PDF se necessário
pdf_bytes = pdf_service.generate_custom_pdf(dados)
```

Esta estrutura modular fornece uma base sólida, segura e escalável para o desenvolvimento contínuo do Sistema Médico VIDAH.