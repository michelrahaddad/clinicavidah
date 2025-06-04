#!/usr/bin/env python3
"""
Script para inserir 200 medicamentos reais no banco de dados
"""
import csv
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuração do banco
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("Erro: DATABASE_URL não encontrada")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def limpar_medicamentos():
    """Remove todos os medicamentos existentes"""
    session = Session()
    try:
        session.execute(text("DELETE FROM medicamentos"))
        session.commit()
        print("Medicamentos existentes removidos")
    except Exception as e:
        session.rollback()
        print(f"Erro ao limpar medicamentos: {e}")
    finally:
        session.close()

def inserir_medicamentos_csv():
    """Insere medicamentos do arquivo CSV"""
    session = Session()
    csv_file = 'attached_assets/medicamentos_200_reais 2_1749065635366.csv'
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            count = 0
            
            for row in csv_reader:
                nome = row['Nome'].strip()
                principio_ativo = row['Princípio Ativo'].strip()
                tipo = row['Tipo'].strip()
                via = row['Via de Administração'].strip()
                concentracao = row['Concentração'].strip()
                posologia = row['Posologia'].strip()
                
                # Inserir no banco (usando apenas as colunas existentes)
                query = text("""
                    INSERT INTO medicamentos (nome, principio_ativo, concentracao, tipo, forma_farmaceutica)
                    VALUES (:nome, :principio_ativo, :concentracao, :tipo, :forma_farmaceutica)
                """)
                
                # Determinar forma farmacêutica baseada no nome
                forma_farmaceutica = 'Comprimido'
                if 'injetável' in nome.lower() or 'ampola' in posologia.lower():
                    forma_farmaceutica = 'Injetável'
                elif 'cápsula' in posologia.lower():
                    forma_farmaceutica = 'Cápsula'
                elif 'inalat' in via.lower():
                    forma_farmaceutica = 'Inalação'
                elif 'tópica' in via.lower():
                    forma_farmaceutica = 'Tópico'
                
                session.execute(query, {
                    'nome': nome,
                    'principio_ativo': principio_ativo,
                    'concentracao': concentracao,
                    'tipo': tipo,
                    'forma_farmaceutica': forma_farmaceutica
                })
                
                count += 1
                
            session.commit()
            print(f"✅ {count} medicamentos inseridos com sucesso!")
            
    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao inserir medicamentos: {e}")
        raise
    finally:
        session.close()

def verificar_insercao():
    """Verifica se os medicamentos foram inseridos"""
    session = Session()
    try:
        result = session.execute(text("SELECT COUNT(*) as total FROM medicamentos")).fetchone()
        print(f"Total de medicamentos no banco: {result.total}")
        
        # Mostra alguns exemplos
        exemplos = session.execute(text("SELECT nome, principio_ativo, concentracao FROM medicamentos LIMIT 5")).fetchall()
        print("\nExemplos inseridos:")
        for med in exemplos:
            print(f"- {med.nome} ({med.principio_ativo}) - {med.concentracao}")
            
    except Exception as e:
        print(f"Erro ao verificar inserção: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    print("🔄 Iniciando inserção de medicamentos reais...")
    limpar_medicamentos()
    inserir_medicamentos_csv()
    verificar_insercao()
    print("✅ Processo concluído!")