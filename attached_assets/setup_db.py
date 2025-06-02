import sqlite3
from werkzeug.security import generate_password_hash

def create_database():
    """Create all database tables"""
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create médicos table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        crm TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create pacientes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create receitas table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_paciente TEXT NOT NULL,
        medicamentos TEXT NOT NULL,
        posologias TEXT NOT NULL,
        duracoes TEXT NOT NULL,
        vias TEXT NOT NULL,
        medico TEXT NOT NULL,
        data TEXT NOT NULL,
        id_paciente INTEGER,
        id_medico INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_paciente) REFERENCES pacientes (id),
        FOREIGN KEY (id_medico) REFERENCES medicos (id)
    )
    """)
    
    # Create exames_lab table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exames_lab (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_paciente TEXT NOT NULL,
        exames TEXT NOT NULL,
        medico TEXT NOT NULL,
        data TEXT NOT NULL,
        id_paciente INTEGER,
        id_medico INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_paciente) REFERENCES pacientes (id),
        FOREIGN KEY (id_medico) REFERENCES medicos (id)
    )
    """)
    
    # Create exames_img table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exames_img (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_paciente TEXT NOT NULL,
        exames TEXT NOT NULL,
        medico TEXT NOT NULL,
        data TEXT NOT NULL,
        id_paciente INTEGER,
        id_medico INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_paciente) REFERENCES pacientes (id),
        FOREIGN KEY (id_medico) REFERENCES medicos (id)
    )
    """)
    
    # Create agenda table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        paciente TEXT NOT NULL,
        motivo TEXT,
        id_paciente INTEGER,
        id_medico INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_paciente) REFERENCES pacientes (id),
        FOREIGN KEY (id_medico) REFERENCES medicos (id)
    )
    """)
    
    # Create prontuario table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prontuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        id_registro INTEGER NOT NULL,
        id_paciente INTEGER,
        id_medico INTEGER NOT NULL,
        data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_paciente) REFERENCES pacientes (id),
        FOREIGN KEY (id_medico) REFERENCES medicos (id)
    )
    """)
    
    # Create test doctor
    try:
        test_nome = "Dr. Teste"
        test_crm = "crm123"
        test_senha = "senha123"
        senha_hash = generate_password_hash(test_senha)
        
        cursor.execute("SELECT * FROM medicos WHERE crm = ?", (test_crm,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO medicos (nome, crm, senha) VALUES (?, ?, ?)", 
                         (test_nome, test_crm, senha_hash))
            print(f"Médico de teste criado: {test_nome} (CRM: {test_crm}, Senha: {test_senha})")
        else:
            print("Médico de teste já existe.")
    except sqlite3.IntegrityError as e:
        print(f"Erro ao criar médico de teste: {e}")
    
    conn.commit()
    conn.close()
    print("Database criado com sucesso!")

if __name__ == '__main__':
    create_database()
