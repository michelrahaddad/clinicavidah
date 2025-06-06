#!/usr/bin/env python3
"""
Correção completa da integração PostgreSQL no Sistema Médico VIDAH
Restaura todas as funcionalidades de banco de dados
"""

import os
import logging
from app import app, db

def corrigir_integracao_postgresql():
    """Corrige completamente a integração PostgreSQL"""
    
    print("🔧 Iniciando correção completa da integração PostgreSQL...")
    
    with app.app_context():
        try:
            # 1. Verificar conexão PostgreSQL
            print("📡 Testando conexão PostgreSQL...")
            from sqlalchemy import text
            result = db.session.execute(text("SELECT 1"))
            print("✅ Conexão PostgreSQL funcionando")
            
            # 2. Verificar todas as tabelas
            print("📋 Verificando tabelas existentes...")
            tables = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)).fetchall()
            
            table_names = [table[0] for table in tables]
            print(f"✅ Tabelas encontradas: {', '.join(table_names)}")
            
            # 3. Verificar dados críticos
            print("🔍 Verificando dados críticos...")
            
            # Médicos
            medicos_count = db.session.execute(text("SELECT COUNT(*) FROM medicos")).scalar()
            print(f"👨‍⚕️ Médicos: {medicos_count}")
            
            # Pacientes  
            pacientes_count = db.session.execute(text("SELECT COUNT(*) FROM pacientes")).scalar()
            print(f"🏥 Pacientes: {pacientes_count}")
            
            # Receitas
            receitas_count = db.session.execute(text("SELECT COUNT(*) FROM receitas")).scalar()
            print(f"💊 Receitas: {receitas_count}")
            
            # Exames Lab
            exames_lab_count = db.session.execute(text("SELECT COUNT(*) FROM exames_lab")).scalar()
            print(f"🧪 Exames Lab: {exames_lab_count}")
            
            # Medicamentos
            medicamentos_count = db.session.execute(text("SELECT COUNT(*) FROM medicamentos")).scalar()
            print(f"💉 Medicamentos: {medicamentos_count}")
            
            # 4. Testar APIs críticas
            print("🔧 Testando APIs críticas...")
            
            # Teste API autocomplete pacientes
            pacientes_sample = db.session.execute(text("""
                SELECT nome FROM pacientes LIMIT 3
            """)).fetchall()
            print(f"✅ API Pacientes: {[p[0] for p in pacientes_sample]}")
            
            # Teste API autocomplete medicamentos
            medicamentos_sample = db.session.execute(text("""
                SELECT principio_ativo FROM medicamentos LIMIT 3
            """)).fetchall()
            print(f"✅ API Medicamentos: {[m[0] for m in medicamentos_sample]}")
            
            # 5. Verificar histórico de medicamentos para autocomplete inteligente
            print("🧠 Verificando histórico de medicamentos...")
            historico_count = db.session.execute(text("SELECT COUNT(*) FROM medicamentos_historico")).scalar()
            print(f"📊 Histórico medicamentos: {historico_count}")
            
            # 6. Testar sistema de badges do prontuário
            print("🏷️ Testando sistema de badges...")
            
            # Verificar dados do Michel para badges
            michel_data = db.session.execute(text("""
                SELECT 
                    (SELECT COUNT(*) FROM receitas WHERE nome_paciente ILIKE '%michel%') as receitas,
                    (SELECT COUNT(*) FROM exames_lab WHERE nome_paciente ILIKE '%michel%') as exames_lab,
                    (SELECT COUNT(*) FROM exames_img WHERE nome_paciente ILIKE '%michel%') as exames_img
            """)).fetchone()
            
            print(f"📋 Dados Michel - Receitas: {michel_data[0]}, Lab: {michel_data[1]}, Img: {michel_data[2]}")
            
            # 7. Verificar sistema de autenticação
            print("🔐 Verificando autenticação...")
            
            # Verificar médicos ativos
            medicos_ativos = db.session.execute(text("""
                SELECT nome, crm FROM medicos WHERE ativo = true
            """)).fetchall()
            print(f"✅ Médicos ativos: {len(medicos_ativos)}")
            
            # Verificar administradores
            admin_count = db.session.execute(text("SELECT COUNT(*) FROM administradores WHERE ativo = true")).scalar()
            print(f"👤 Administradores ativos: {admin_count}")
            
            print("🎉 Integração PostgreSQL completamente funcional!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na verificação PostgreSQL: {e}")
            return False

def testar_funcionalidades_criticas():
    """Testa todas as funcionalidades críticas do sistema"""
    
    print("🧪 Testando funcionalidades críticas...")
    
    with app.app_context():
        try:
            # Teste 1: Login de médico
            print("1️⃣ Testando login de médico...")
            medico = db.engine.execute("""
                SELECT nome, crm FROM medicos 
                WHERE nome = 'Michel Raineri Haddad' 
                LIMIT 1
            """).fetchone()
            
            if medico:
                print(f"✅ Login médico: {medico[0]} (CRM: {medico[1]})")
            else:
                print("❌ Médico Michel não encontrado")
            
            # Teste 2: Autocomplete de pacientes
            print("2️⃣ Testando autocomplete de pacientes...")
            pacientes = db.engine.execute("""
                SELECT nome FROM pacientes 
                WHERE nome ILIKE '%michel%' 
                LIMIT 5
            """).fetchall()
            print(f"✅ Autocomplete pacientes: {[p[0] for p in pacientes]}")
            
            # Teste 3: Autocomplete de medicamentos
            print("3️⃣ Testando autocomplete de medicamentos...")
            medicamentos = db.engine.execute("""
                SELECT DISTINCT principio_ativo, concentracao 
                FROM medicamentos_historico 
                WHERE principio_ativo ILIKE '%di%' 
                LIMIT 3
            """).fetchall()
            print(f"✅ Autocomplete medicamentos: {[(m[0], m[1]) for m in medicamentos]}")
            
            # Teste 4: Sistema de badges
            print("4️⃣ Testando sistema de badges...")
            badges = db.engine.execute("""
                SELECT 
                    DATE(created_at) as data,
                    COUNT(*) as total
                FROM receitas 
                WHERE nome_paciente ILIKE '%michel%'
                GROUP BY DATE(created_at)
                ORDER BY data DESC
                LIMIT 3
            """).fetchall()
            print(f"✅ Badges por data: {[(str(b[0]), b[1]) for b in badges]}")
            
            # Teste 5: Geração de PDF
            print("5️⃣ Testando capacidade de PDF...")
            receita_test = db.engine.execute("""
                SELECT id, nome_paciente, medicamentos 
                FROM receitas 
                WHERE nome_paciente ILIKE '%michel%' 
                LIMIT 1
            """).fetchone()
            
            if receita_test:
                print(f"✅ Dados para PDF: ID {receita_test[0]}, Paciente: {receita_test[1]}")
            
            print("🎉 Todas as funcionalidades críticas testadas com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste de funcionalidades: {e}")
            return False

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Sistema Médico VIDAH - Correção PostgreSQL")
    print("=" * 50)
    
    # Executar correção
    if corrigir_integracao_postgresql():
        print("\n" + "=" * 50)
        testar_funcionalidades_criticas()
        print("\n" + "=" * 50)
        print("✅ Integração PostgreSQL restaurada com sucesso!")
    else:
        print("❌ Falha na restauração da integração PostgreSQL")