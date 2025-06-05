#!/usr/bin/env python3
"""
Cria dados completos para o paciente Michel em todas as tabelas médicas
"""

from app import app, db
from models import *
from datetime import datetime, date

def criar_dados_michel_completos():
    """Cria documentos médicos completos para Michel Raineri Haddad"""
    
    with app.app_context():
        # Buscar o médico
        medico = db.session.query(Medico).filter(Medico.nome.ilike('%michel%')).first()
        if not medico:
            print("Médico Michel não encontrado")
            return
        
        paciente_nome = "Michel Raineri Haddad"
        data_hoje = date.today()
        
        print(f"Criando documentos para: {paciente_nome}")
        print(f"Médico: {medico.nome} (ID: {medico.id})")
        
        # 1. Exames Laboratoriais
        try:
            exame_lab = ExameLab(
                medico_id=medico.id,
                nome_paciente=paciente_nome,
                data=data_hoje,
                exames_solicitados="Hemograma completo, Glicose, Colesterol total e frações, Triglicerídeos, Creatinina, Ureia",
                observacoes="Exames de rotina para check-up anual",
                created_at=datetime.now()
            )
            db.session.add(exame_lab)
            print("✓ Exame laboratorial criado")
        except Exception as e:
            print(f"Erro ao criar exame lab: {e}")
        
        # 2. Exames de Imagem
        try:
            exame_img = ExameImg(
                medico_id=medico.id,
                nome_paciente=paciente_nome,
                data=data_hoje,
                tipo_exame="Raio-X de Tórax",
                local_exame="Clínica de Imagem VIDAH",
                observacoes="Investigação de tosse persistente",
                created_at=datetime.now()
            )
            db.session.add(exame_img)
            print("✓ Exame de imagem criado")
        except Exception as e:
            print(f"Erro ao criar exame img: {e}")
        
        # 3. Relatório Médico
        try:
            relatorio = RelatorioMedico(
                medico_id=medico.id,
                nome_paciente=paciente_nome,
                data=data_hoje,
                diagnostico="Hipertensão arterial sistêmica leve",
                tratamento="Dieta hipossódica, exercícios físicos regulares, controle de peso",
                observacoes="Paciente orientado sobre mudanças no estilo de vida",
                created_at=datetime.now()
            )
            db.session.add(relatorio)
            print("✓ Relatório médico criado")
        except Exception as e:
            print(f"Erro ao criar relatório: {e}")
        
        # 4. Atestado Médico
        try:
            atestado = AtestadoMedico(
                medico_id=medico.id,
                nome_paciente=paciente_nome,
                data=data_hoje,
                dias_afastamento=3,
                cid_codigo="Z51.1",
                motivo="Repouso médico para recuperação pós-cirúrgica",
                observacoes="Retorno em 3 dias para reavaliação",
                created_at=datetime.now()
            )
            db.session.add(atestado)
            print("✓ Atestado médico criado")
        except Exception as e:
            print(f"Erro ao criar atestado: {e}")
        
        # 5. Formulário Alto Custo
        try:
            alto_custo = FormularioAltoCusto(
                medico_id=medico.id,
                nome_paciente=paciente_nome,
                data=data_hoje,
                medicamento="Adalimumab 40mg/0,8ml",
                cid_codigo="M06.9",
                justificativa="Artrite reumatoide com falha terapêutica aos DMARDs convencionais",
                observacoes="Paciente com indicação de terapia biológica conforme protocolo",
                created_at=datetime.now()
            )
            db.session.add(alto_custo)
            print("✓ Formulário alto custo criado")
        except Exception as e:
            print(f"Erro ao criar alto custo: {e}")
        
        # Commit todas as mudanças
        try:
            db.session.commit()
            print("\n✅ Todos os documentos criados com sucesso!")
            
            # Verificar dados criados
            receitas = db.session.query(Receita).filter(Receita.nome_paciente.ilike(f'%{paciente_nome}%')).count()
            exames_lab = db.session.query(ExameLab).filter(ExameLab.nome_paciente.ilike(f'%{paciente_nome}%')).count()
            exames_img = db.session.query(ExameImg).filter(ExameImg.nome_paciente.ilike(f'%{paciente_nome}%')).count()
            relatorios = db.session.query(RelatorioMedico).filter(RelatorioMedico.nome_paciente.ilike(f'%{paciente_nome}%')).count()
            atestados = db.session.query(AtestadoMedico).filter(AtestadoMedico.nome_paciente.ilike(f'%{paciente_nome}%')).count()
            alto_custo_count = db.session.query(FormularioAltoCusto).filter(FormularioAltoCusto.nome_paciente.ilike(f'%{paciente_nome}%')).count()
            
            print(f"\nResumo dos dados para {paciente_nome}:")
            print(f"  💊 Receitas: {receitas}")
            print(f"  🧪 Exames Lab: {exames_lab}")
            print(f"  🩻 Exames Imagem: {exames_img}")
            print(f"  🧾 Relatórios: {relatorios}")
            print(f"  📄 Atestados: {atestados}")
            print(f"  💰💊 Alto Custo: {alto_custo_count}")
            print(f"  📋 Total: {receitas + exames_lab + exames_img + relatorios + atestados + alto_custo_count}")
            
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
            db.session.rollback()

if __name__ == '__main__':
    criar_dados_michel_completos()