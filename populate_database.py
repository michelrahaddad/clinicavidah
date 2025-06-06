"""
Script para popular o banco de dados com dados médicos reais
Criará dados para o Dr. Michel Raineri Haddad e pacientes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import db
from models import Medico, Paciente, Receita, ExameLab, ExameImg, AtestadoMedico
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def populate_database():
    """Popula o banco de dados com dados médicos reais"""
    
    # Verificar se já existe o Dr. Michel
    michel = db.session.query(Medico).filter_by(crm='183299-SP').first()
    if not michel:
        # Criar Dr. Michel
        michel = Medico()
        michel.nome = 'Michel Raineri Haddad'
        michel.crm = '183299-SP'
        michel.senha = generate_password_hash('123456')
        michel.assinatura = None
        db.session.add(michel)
        db.session.commit()
        print(f"Dr. Michel criado com ID: {michel.id}")
    else:
        print(f"Dr. Michel já existe com ID: {michel.id}")
    
    # Criar pacientes reais
    pacientes_data = [
        {
            'nome': 'João Silva Santos',
            'cpf': '123.456.789-10',
            'idade': 45,
            'endereco': 'Rua das Flores, 123',
            'cidade_uf': 'São Paulo, SP',
            'email': 'joao.silva@email.com',
            'telefone': '(11) 99999-1234'
        },
        {
            'nome': 'Maria Oliveira Costa',
            'cpf': '987.654.321-00',
            'idade': 32,
            'endereco': 'Av. Paulista, 456',
            'cidade_uf': 'São Paulo, SP',
            'email': 'maria.oliveira@email.com',
            'telefone': '(11) 88888-5678'
        },
        {
            'nome': 'Carlos Eduardo Lima',
            'cpf': '456.789.123-45',
            'idade': 58,
            'endereco': 'Rua Augusta, 789',
            'cidade_uf': 'São Paulo, SP',
            'email': 'carlos.lima@email.com',
            'telefone': '(11) 77777-9012'
        }
    ]
    
    pacientes = []
    for p_data in pacientes_data:
        # Verificar se já existe
        paciente = db.session.query(Paciente).filter_by(cpf=p_data['cpf']).first()
        if not paciente:
            paciente = Paciente()
            paciente.nome = p_data['nome']
            paciente.cpf = p_data['cpf']
            paciente.idade = p_data['idade']
            paciente.endereco = p_data['endereco']
            paciente.cidade_uf = p_data['cidade_uf']
            paciente.email = p_data['email']
            paciente.telefone = p_data['telefone']
            db.session.add(paciente)
            db.session.commit()
            print(f"Paciente {paciente.nome} criado com ID: {paciente.id}")
        else:
            print(f"Paciente {paciente.nome} já existe com ID: {paciente.id}")
        pacientes.append(paciente)
    
    # Criar receitas médicas
    medicamentos_comuns = [
        ['Dipirona 500mg', 'Paracetamol 750mg'],
        ['Amoxicilina 875mg', 'Azitromicina 500mg'],
        ['Omeprazol 20mg', 'Pantoprazol 40mg'],
        ['Losartana 50mg', 'Enalapril 10mg'],
        ['Metformina 850mg', 'Glibenclamida 5mg']
    ]
    
    posologias = [
        ['1 comprimido a cada 6 horas', '1 comprimido a cada 8 horas'],
        ['1 comprimido a cada 8 horas por 7 dias', '1 comprimido ao dia por 5 dias'],
        ['1 cápsula em jejum', '1 comprimido antes das refeições'],
        ['1 comprimido ao dia', '1 comprimido 2 vezes ao dia'],
        ['1 comprimido após café da manhã', '1 comprimido antes do almoço']
    ]
    
    for i, paciente in enumerate(pacientes):
        # Criar 2-3 receitas por paciente
        for j in range(random.randint(2, 3)):
            receita = Receita()
            receita.nome_paciente = paciente.nome
            receita.id_paciente = paciente.id
            receita.id_medico = michel.id
            receita.medico_nome = michel.nome
            
            # Escolher medicamentos aleatórios
            med_idx = random.randint(0, len(medicamentos_comuns) - 1)
            receita.medicamentos = ';'.join(medicamentos_comuns[med_idx])
            receita.posologias = ';'.join(posologias[med_idx])
            receita.duracoes = ';'.join(['7 dias', '10 dias'])
            receita.vias = ';'.join(['Oral', 'Oral'])
            
            # Data da receita (últimos 30 dias)
            days_ago = random.randint(1, 30)
            data_receita = datetime.now() - timedelta(days=days_ago)
            receita.data = data_receita.strftime('%d/%m/%Y')
            receita.data_criacao = data_receita
            
            db.session.add(receita)
            print(f"Receita criada para {paciente.nome}")
    
    # Criar exames laboratoriais
    exames_lab_tipos = [
        'Hemograma completo;Glicemia em jejum;Colesterol total',
        'Ureia;Creatinina;Ácido úrico',
        'TSH;T4 livre;T3',
        'Triglicerídeos;HDL;LDL',
        'Proteína C reativa;VHS;Fibrinogênio'
    ]
    
    for i, paciente in enumerate(pacientes):
        for j in range(random.randint(1, 2)):
            exame = ExameLab()
            exame.nome_paciente = paciente.nome
            exame.id_paciente = paciente.id
            exame.id_medico = michel.id
            exame.medico_nome = michel.nome
            exame.exames = random.choice(exames_lab_tipos)
            
            days_ago = random.randint(1, 30)
            data_exame = datetime.now() - timedelta(days=days_ago)
            exame.data = data_exame.strftime('%d/%m/%Y')
            
            db.session.add(exame)
            print(f"Exame laboratorial criado para {paciente.nome}")
    
    # Criar exames de imagem
    exames_img_tipos = [
        'Raio-X de tórax;Ultrassonografia abdominal',
        'Tomografia computadorizada do abdome',
        'Ressonância magnética do joelho',
        'Ecocardiograma;Eletrocardiograma',
        'Ultrassonografia de tireoide'
    ]
    
    for i, paciente in enumerate(pacientes):
        for j in range(random.randint(0, 2)):
            exame = ExameImg()
            exame.nome_paciente = paciente.nome
            exame.id_paciente = paciente.id
            exame.id_medico = michel.id
            exame.medico_nome = michel.nome
            exame.exames = random.choice(exames_img_tipos)
            
            days_ago = random.randint(1, 30)
            data_exame = datetime.now() - timedelta(days=days_ago)
            exame.data = data_exame.strftime('%d/%m/%Y')
            
            db.session.add(exame)
            print(f"Exame de imagem criado para {paciente.nome}")
    
    db.session.commit()
    print("\nBanco de dados populado com sucesso!")
    
    # Estatísticas finais
    total_receitas = db.session.query(Receita).count()
    total_exames_lab = db.session.query(ExameLab).count()
    total_exames_img = db.session.query(ExameImg).count()
    total_pacientes = db.session.query(Paciente).count()
    
    print(f"\nEstatísticas finais:")
    print(f"- Pacientes: {total_pacientes}")
    print(f"- Receitas: {total_receitas}")
    print(f"- Exames laboratoriais: {total_exames_lab}")
    print(f"- Exames de imagem: {total_exames_img}")

if __name__ == '__main__':
    from app_modular_fixed import app
    with app.app_context():
        populate_database()