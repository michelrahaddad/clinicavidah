import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def seed_database():
    """Populate database with sample data"""
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    
    # Insert sample patients
    pacientes_sample = [
        'Maria Silva dos Santos',
        'João Carlos Oliveira',
        'Ana Paula Costa',
        'Carlos Eduardo Santos',
        'Fernanda Lima'
    ]
    
    for nome_paciente in pacientes_sample:
        cursor.execute("SELECT * FROM pacientes WHERE nome = ?", (nome_paciente,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO pacientes (nome) VALUES (?)", (nome_paciente,))
            print(f"Paciente adicionado: {nome_paciente}")
    
    # Get test doctor ID
    cursor.execute("SELECT id, nome FROM medicos WHERE crm = ?", ('crm123',))
    medico = cursor.fetchone()
    
    if medico:
        medico_id, medico_nome = medico
        
        # Get patient IDs
        cursor.execute("SELECT id, nome FROM pacientes LIMIT 3")
        pacientes = cursor.fetchall()
        
        # Create sample appointments
        today = datetime.now()
        for i, (paciente_id, paciente_nome) in enumerate(pacientes):
            appointment_date = (today + timedelta(days=i+1)).strftime('%Y-%m-%d')
            
            cursor.execute("SELECT * FROM agenda WHERE data = ? AND id_paciente = ?", 
                         (appointment_date, paciente_id))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO agenda (data, paciente, motivo, id_paciente, id_medico) 
                VALUES (?, ?, ?, ?, ?)
                """, (appointment_date, paciente_nome, 'Consulta de rotina', paciente_id, medico_id))
                print(f"Agendamento criado: {paciente_nome} em {appointment_date}")
        
        # Create sample prescription
        if pacientes:
            paciente_id, paciente_nome = pacientes[0]
            data_receita = today.strftime('%Y-%m-%d')
            
            cursor.execute("SELECT * FROM receitas WHERE id_paciente = ? AND data = ?", 
                         (paciente_id, data_receita))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO receitas (nome_paciente, medicamentos, posologias, duracoes, vias, medico, data, id_paciente, id_medico)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    paciente_nome,
                    'Paracetamol 500mg,Dipirona 500mg',
                    '1 comprimido,1 comprimido',
                    '7 dias,5 dias',
                    'Oral,Oral',
                    medico_nome,
                    data_receita,
                    paciente_id,
                    medico_id
                ))
                
                # Add to prontuario
                receita_id = cursor.lastrowid
                cursor.execute("""
                INSERT INTO prontuario (tipo, id_registro, id_paciente, id_medico, data)
                VALUES (?, ?, ?, ?, ?)
                """, ('receita', receita_id, paciente_id, medico_id, data_receita))
                print(f"Receita de exemplo criada para {paciente_nome}")
    
    conn.commit()
    conn.close()
    print("Dados de exemplo inseridos com sucesso!")

if __name__ == '__main__':
    seed_database()
