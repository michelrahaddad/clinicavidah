# Sistema Médico VIDAH - Download e Instalação

## Como Baixar o Sistema Completo

### Opção 1: Download via Git (Recomendado)
```bash
git clone <url-do-repositorio>
cd sistema-medico-vidah
```

### Opção 2: Download Manual
Se você está visualizando este sistema no Replit:
1. Clique no botão "Download" no painel lateral
2. Baixe todos os arquivos como ZIP
3. Extraia em uma pasta local

## Estrutura do Sistema

```
sistema-medico-vidah/
├── app.py                    # Configuração principal do Flask
├── main.py                   # Arquivo de entrada
├── models.py                 # Modelos do banco de dados
├── routes/                   # Rotas do sistema
│   ├── auth.py              # Autenticação
│   ├── dashboard.py         # Dashboard principal
│   ├── receita.py           # Prescrição de medicamentos
│   ├── exames_lab.py        # Exames laboratoriais
│   ├── exames_img.py        # Exames de imagem
│   ├── prontuario.py        # Prontuário eletrônico
│   ├── agenda.py            # Agenda de consultas
│   ├── password_recovery.py # Recuperação de senha
│   └── api.py               # APIs auxiliares
├── templates/               # Templates HTML
├── static/                  # Arquivos estáticos (CSS, JS, imagens)
├── utils/                   # Utilitários
├── install/                 # Arquivos de instalação
│   ├── README.md           # Instruções detalhadas
│   ├── requirements-*.txt  # Dependências por OS
│   └── scripts/            # Scripts de inicialização
└── logovidah.png           # Logo do sistema
```

## Instalação Rápida

### Windows
1. Instale Python 3.8+ de python.org
2. Abra o PowerShell ou CMD na pasta do projeto
3. Execute:
```cmd
python -m venv venv
venv\Scripts\activate
pip install Flask Flask-SQLAlchemy Flask-WTF WTForms Werkzeug SQLAlchemy psycopg2-binary email-validator WeasyPrint gunicorn
python main.py
```

### macOS
1. Instale Python via Homebrew: `brew install python`
2. No Terminal, na pasta do projeto:
```bash
python3 -m venv venv
source venv/bin/activate
pip install Flask Flask-SQLAlchemy Flask-WTF WTForms Werkzeug SQLAlchemy psycopg2-binary email-validator WeasyPrint gunicorn
python main.py
```

### Linux (Ubuntu/Debian)
1. Instale dependências do sistema:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
sudo apt install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
```

2. Configure o projeto:
```bash
python3 -m venv venv
source venv/bin/activate
pip install Flask Flask-SQLAlchemy Flask-WTF WTForms Werkzeug SQLAlchemy psycopg2-binary email-validator WeasyPrint gunicorn
python3 main.py
```

## Inicialização Automática

Use os scripts na pasta `install/scripts/`:

**Windows:** Execute `install\scripts\start-windows.bat`
**macOS/Linux:** Execute `./install/scripts/start-macos.sh` ou `./install/scripts/start-linux.sh`

## Acesso ao Sistema

1. Abra seu navegador
2. Vá para: http://localhost:5000
3. Credenciais padrão:
   - Nome: Michel Raineri HAddad
   - CRM: 123456-SP
   - Senha: 123456

## Configurações Opcionais

### Banco PostgreSQL
```bash
export DATABASE_URL="postgresql://usuario:senha@localhost/vidah_db"
```

### Chave de Segurança
```bash
export SESSION_SECRET="sua-chave-super-secreta"
```

## Funcionalidades Disponíveis

✅ **Autenticação Segura**
- Login com nome, CRM e senha
- Recuperação de senha por CRM
- Sessões seguras

✅ **Prescrição Médica**
- 200 medicamentos com autocomplete
- Posologia personalizada
- Geração de PDF A4 otimizado

✅ **Exames Médicos**
- Exames laboratoriais completos
- Exames de imagem especializados
- Seção dedicada de cardiologia (12 exames)

✅ **Gestão**
- Prontuário eletrônico integrado
- Agenda de consultas
- Dashboard com estatísticas

✅ **PDFs Profissionais**
- Design minimalista para impressão
- Logo VIDAH integrado
- Otimizado para tinta preta A4

## Solução de Problemas

### Erro WeasyPrint no Windows
```cmd
pip install --upgrade pip setuptools wheel
pip install WeasyPrint
```

### Porta ocupada
Se a porta 5000 estiver em uso, o sistema tentará outras portas automaticamente.

### Problemas de permissão
No macOS/Linux, você pode precisar usar `sudo` para algumas instalações de dependências do sistema.

## Suporte

- Consulte `install/README.md` para instruções detalhadas
- Verifique os logs do sistema para diagnóstico
- O banco SQLite é criado automaticamente na primeira execução

---
**Sistema Médico VIDAH** - Pronto para produção em qualquer ambiente