# Sistema Médico VIDAH - Instalação

Este guia contém instruções para instalar e executar o Sistema Médico VIDAH em diferentes sistemas operacionais.

## Requisitos do Sistema

- Python 3.8 ou superior
- PostgreSQL (opcional - usa SQLite por padrão)
- Git

## Dependências Python

O sistema utiliza as seguintes bibliotecas:

- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-WTF 1.2.1
- WTForms 3.1.1
- Werkzeug 3.0.1
- SQLAlchemy 2.0.23
- psycopg2-binary 2.9.9
- email-validator 2.1.0
- WeasyPrint 61.2
- gunicorn 21.2.0

## Instalação

### Windows

1. **Instalar Python**
   - Baixe Python 3.8+ do site oficial: https://python.org
   - Durante a instalação, marque "Add Python to PATH"

2. **Instalar Git**
   - Baixe do site oficial: https://git-scm.com

3. **Clonar o projeto**
   ```cmd
   git clone <url-do-repositorio>
   cd sistema-medico-vidah
   ```

4. **Criar ambiente virtual**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

5. **Instalar dependências**
   ```cmd
   pip install -r install/requirements-windows.txt
   ```

6. **Executar o sistema**
   ```cmd
   python main.py
   ```

### macOS

1. **Instalar Homebrew** (se não tiver)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Instalar Python e Git**
   ```bash
   brew install python git
   ```

3. **Clonar o projeto**
   ```bash
   git clone <url-do-repositorio>
   cd sistema-medico-vidah
   ```

4. **Criar ambiente virtual**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Instalar dependências**
   ```bash
   pip install -r install/requirements-macos.txt
   ```

6. **Executar o sistema**
   ```bash
   python main.py
   ```

### Linux (Ubuntu/Debian)

1. **Atualizar sistema e instalar dependências**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git
   sudo apt install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0  # Para WeasyPrint
   ```

2. **Clonar o projeto**
   ```bash
   git clone <url-do-repositorio>
   cd sistema-medico-vidah
   ```

3. **Criar ambiente virtual**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Instalar dependências**
   ```bash
   pip install -r install/requirements-linux.txt
   ```

5. **Executar o sistema**
   ```bash
   python main.py
   ```

## Configuração do Banco de Dados

### SQLite (Padrão)
O sistema criará automaticamente um arquivo `vidah_medical.db` na primeira execução.

### PostgreSQL (Opcional)
1. Instale PostgreSQL
2. Crie um banco de dados
3. Configure a variável de ambiente:
   ```bash
   export DATABASE_URL="postgresql://usuario:senha@localhost/nome_do_banco"
   ```

## Configuração de Segurança

Configure a chave secreta da sessão:

**Windows:**
```cmd
set SESSION_SECRET=sua-chave-secreta-muito-forte
```

**macOS/Linux:**
```bash
export SESSION_SECRET=sua-chave-secreta-muito-forte
```

## Acesso ao Sistema

1. Abra o navegador
2. Acesse: http://localhost:5000
3. Use as credenciais padrão:
   - Nome: Michel Raineri HAddad
   - CRM: 123456-SP
   - Senha: 123456

## Funcionalidades

- ✅ Autenticação de médicos
- ✅ Recuperação de senha
- ✅ Prescrição de receitas (200 medicamentos)
- ✅ Solicitação de exames laboratoriais
- ✅ Solicitação de exames de imagem
- ✅ Exames cardiológicos especializados
- ✅ Prontuário eletrônico
- ✅ Agenda de consultas
- ✅ Geração de PDFs otimizados para impressão A4
- ✅ Assinatura digital do médico

## Resolução de Problemas

### Erro de instalação WeasyPrint no Windows
```cmd
pip install --upgrade pip setuptools wheel
pip install WeasyPrint
```

### Erro de permissão no macOS
```bash
pip install --user -r install/requirements-macos.txt
```

### Problema com PostgreSQL
Verifique se o serviço está rodando:
```bash
sudo systemctl status postgresql  # Linux
brew services list | grep postgres  # macOS
```

## Suporte

Para suporte técnico, consulte a documentação ou entre em contato com a equipe de desenvolvimento.

---
**Sistema Médico VIDAH** - Tecnologia avançada para profissionais de saúde