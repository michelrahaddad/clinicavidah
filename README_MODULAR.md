# Sistema Médico VIDAH - Arquitetura Modular

## Visão Geral

Este documento descreve a nova arquitetura modular do Sistema Médico VIDAH, implementada para garantir alto padrão de qualidade, manutenibilidade e escalabilidade.

## Estrutura da Arquitetura

### Aplicação Principal
- **app_modular.py**: Factory function principal que cria e configura a aplicação
- **main.py**: Ponto de entrada que utiliza o factory pattern
- **config.py**: Configurações centralizadas do sistema

### Blueprints Modulares
```
blueprints/
├── auth.py          # Autenticação e autorização
├── dashboard.py     # Dashboard principal com estatísticas
├── prescriptions.py # Gestão de prescrições médicas
└── patients.py      # Gestão de pacientes
```

### Camadas de Serviços
```
services/
└── pdf_service.py   # Serviços de geração de PDF
```

### Validadores
```
validators/
├── base.py          # Validadores base e sanitização
└── medical.py       # Validadores médicos especializados
```

### Sistema de Logging
```
core/
└── logging.py       # Sistema centralizado de logs
```

### Utilitários
```
utils/
└── __init__.py      # Utilitários gerais
```

## Funcionalidades dos Blueprints

### Auth Blueprint (`/auth`)
- Login médico com validação CRM
- Logout seguro
- Controle de sessões
- Decoradores de autenticação (`@require_auth`, `@require_doctor`)

### Dashboard Blueprint (`/dashboard`)
- Estatísticas em tempo real
- Gráficos de atividades
- APIs para dados dinâmicos (`/api/stats`, `/api/activities`)
- Visão geral do sistema

### Prescriptions Blueprint (`/receitas`)
- Listagem de receitas médicas
- Criação de novas receitas
- Edição e visualização
- Geração de PDF
- APIs de autocomplete para pacientes e medicamentos
- Sistema de validação integrado

### Patients Blueprint (`/pacientes`)
- Gestão completa de pacientes
- Busca avançada com paginação
- Histórico médico completo
- Estatísticas por paciente
- APIs de busca dinâmica

## Características da Arquitetura

### 1. Factory Pattern
A aplicação utiliza o padrão Factory para criação da instância Flask:
```python
app = create_app(config_name)
```

### 2. Separação de Responsabilidades
Cada blueprint tem responsabilidade específica e bem definida.

### 3. Sistema de Validação Robusto
- Sanitização automática de inputs
- Validadores especializados por tipo de dados
- Tratamento de erros padronizado

### 4. Logging Centralizado
- Logs estruturados por módulo
- Rastreamento de ações do usuário
- Sistema de auditoria integrado

### 5. Compatibilidade Retroativa
A arquitetura mantém compatibilidade com blueprints existentes para transição suave.

## Configuração

### Variáveis de Ambiente
- `FLASK_ENV`: Ambiente de execução (development/production)
- `SESSION_SECRET`: Chave secreta para sessões
- `DATABASE_URL`: URL do banco PostgreSQL

### Configurações por Ambiente
- **Development**: Debug ativo, logs detalhados
- **Production**: Otimizações de performance, logs de warning
- **Testing**: Configuração para testes automatizados

## Segurança

### Medidas Implementadas
- Rate limiting por IP
- Headers de segurança padronizados
- Sanitização automática de inputs
- Validação de dados em todas as camadas
- Sistema de auditoria de ações

### Autenticação
- Sessões seguras com timeout
- Verificação de privilégios por rota
- Controle de acesso baseado em roles

## Performance

### Otimizações
- Queries otimizadas com eager loading
- Cache de sessões
- Conexões de banco com pool
- Compressão de respostas

### Monitoramento
- Logs de performance
- Métricas de uso por blueprint
- Rastreamento de erros

## Manutenção

### Estrutura para Desenvolvimento
- Código organizado por funcionalidade
- Testes unitários por módulo
- Documentação inline
- Padrões de código consistentes

### Escalabilidade
- Blueprints independentes
- Serviços desacoplados
- APIs RESTful padronizadas
- Banco de dados normalizado

## Uso da Nova Arquitetura

### Executar o Sistema
```bash
python main.py
```

### Acessar Funcionalidades
- Dashboard: `/dashboard/`
- Receitas: `/receitas/`
- Pacientes: `/pacientes/`
- Login: `/auth/login`

### APIs Disponíveis
- `/dashboard/api/stats` - Estatísticas do dashboard
- `/receitas/api/pacientes` - Autocomplete de pacientes
- `/receitas/api/medicamentos` - Autocomplete de medicamentos
- `/pacientes/api/search` - Busca de pacientes

## Migração

### Processo de Transição
1. Nova arquitetura implementada em paralelo
2. Blueprints antigos mantidos para compatibilidade
3. Migração gradual das funcionalidades
4. Testes extensivos de funcionalidade
5. Deprecação controlada do código legado

### Benefícios da Migração
- **Manutenibilidade**: Código mais organizado e modular
- **Escalabilidade**: Facilita adição de novas funcionalidades
- **Qualidade**: Padrões de código mais rigorosos
- **Performance**: Otimizações específicas por módulo
- **Segurança**: Camadas de proteção padronizadas

## Conclusão

A nova arquitetura modular do Sistema Médico VIDAH representa um avanço significativo em qualidade de código, organização e escalabilidade. A implementação segue as melhores práticas de desenvolvimento Flask e garante um sistema robusto e profissional para gestão médica.