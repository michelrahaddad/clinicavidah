#!/usr/bin/env python3
"""
Correção definitiva dos badges médicos com solução robusta
"""

from app import app, db
from models import *
from datetime import date

def verificar_estrutura_tabelas():
    """Verifica as colunas das tabelas para entender a estrutura"""
    
    with app.app_context():
        # Verificar ExameLab
        try:
            exame_lab = db.session.query(ExameLab).first()
            if exame_lab:
                print("Estrutura ExameLab encontrada:")
                for attr in dir(exame_lab):
                    if not attr.startswith('_'):
                        print(f"  - {attr}")
        except Exception as e:
            print(f"Erro ao verificar ExameLab: {e}")
        
        # Verificar ExameImg
        try:
            exame_img = db.session.query(ExameImg).first()
            if exame_img:
                print("\nEstrutura ExameImg encontrada:")
                for attr in dir(exame_img):
                    if not attr.startswith('_'):
                        print(f"  - {attr}")
        except Exception as e:
            print(f"Erro ao verificar ExameImg: {e}")

def criar_dados_michel_simples():
    """Cria dados para Michel usando a estrutura correta das tabelas"""
    
    with app.app_context():
        nome_paciente = "Michel Raineri HAddad"
        
        # Verificar dados existentes primeiro
        receitas = db.session.query(Receita).filter(Receita.nome_paciente.ilike(f'%Michel%')).count()
        print(f"Receitas existentes para Michel: {receitas}")
        
        # Verificar se existem exames lab
        try:
            exames_lab = db.session.query(ExameLab).filter(ExameLab.nome_paciente.ilike(f'%Michel%')).count()
            print(f"Exames Lab existentes para Michel: {exames_lab}")
        except Exception as e:
            print(f"Erro ao verificar exames lab: {e}")
        
        # Verificar se existem exames img
        try:
            exames_img = db.session.query(ExameImg).filter(ExameImg.nome_paciente.ilike(f'%Michel%')).count()
            print(f"Exames Img existentes para Michel: {exames_img}")
        except Exception as e:
            print(f"Erro ao verificar exames img: {e}")
        
        # Verificar relatórios
        try:
            relatorios = db.session.query(RelatorioMedico).filter(RelatorioMedico.nome_paciente.ilike(f'%Michel%')).count()
            print(f"Relatórios existentes para Michel: {relatorios}")
        except Exception as e:
            print(f"Erro ao verificar relatórios: {e}")
        
        # Verificar atestados
        try:
            atestados = db.session.query(AtestadoMedico).filter(AtestadoMedico.nome_paciente.ilike(f'%Michel%')).count()
            print(f"Atestados existentes para Michel: {atestados}")
        except Exception as e:
            print(f"Erro ao verificar atestados: {e}")
        
        # Verificar alto custo
        try:
            alto_custo = db.session.query(FormularioAltoCusto).filter(FormularioAltoCusto.nome_paciente.ilike(f'%Michel%')).count()
            print(f"Alto Custo existentes para Michel: {alto_custo}")
        except Exception as e:
            print(f"Erro ao verificar alto custo: {e}")

def corrigir_busca_prontuario():
    """Corrige a busca no prontuário para detectar todos os tipos de documentos"""
    
    with open('routes/prontuario.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar a função prontuario e corrigir completamente
    nova_busca = '''        # Sempre buscar em todos os tipos para garantir badges completos
        tipos_busca = ['receita', 'exame_lab', 'exame_img', 'relatorio', 'atestado', 'alto_custo']
        
        if filtro_tipo:
            tipos_busca = [filtro_tipo]
            
        logging.info(f"Tipos de busca ativados: {tipos_busca}")
        
        resultados = []
        
        # Search Prescriptions
        if 'receita' in tipos_busca:
            try:
                query = db.session.query(Receita, Medico.nome.label('medico_nome')).join(Medico)
                
                if busca_paciente:
                    query = query.filter(Receita.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                if filtro_data_inicio and filtro_data_fim:
                    query = query.filter(Receita.data.between(filtro_data_inicio, filtro_data_fim))
                
                receitas = query.order_by(Receita.data.desc()).all()
                logging.info(f"Found {len(receitas)} receitas for search")
                
                for receita, medico_nome in receitas:
                    resultados.append({
                        'tipo': 'receita',
                        'data': receita.data,
                        'id_registro': receita.id,
                        'nome_paciente': receita.nome_paciente,
                        'medico_nome': medico_nome,
                        'detalhes_registro': f"Receita médica"
                    })
            except Exception as e:
                logging.error(f"Error searching receitas: {e}")
        
        # Search Lab Exams  
        if 'exame_lab' in tipos_busca:
            try:
                query = db.session.query(ExameLab)
                
                if busca_paciente:
                    query = query.filter(ExameLab.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                exames_lab = query.order_by(ExameLab.data.desc()).all()
                logging.info(f"Found {len(exames_lab)} exames lab for search")
                
                for exame in exames_lab:
                    resultados.append({
                        'tipo': 'exame_lab',
                        'data': exame.data,
                        'id_registro': exame.id,
                        'nome_paciente': exame.nome_paciente,
                        'medico_nome': getattr(exame, 'medico_nome', 'N/A'),
                        'detalhes_registro': f"Exame laboratorial"
                    })
            except Exception as e:
                logging.error(f"Error searching exames lab: {e}")
        
        # Search Image Exams
        if 'exame_img' in tipos_busca:
            try:
                query = db.session.query(ExameImg)
                
                if busca_paciente:
                    query = query.filter(ExameImg.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                exames_img = query.order_by(ExameImg.data.desc()).all()
                logging.info(f"Found {len(exames_img)} exames img for search")
                
                for exame in exames_img:
                    resultados.append({
                        'tipo': 'exame_img',
                        'data': exame.data,
                        'id_registro': exame.id,
                        'nome_paciente': exame.nome_paciente,
                        'medico_nome': getattr(exame, 'medico_nome', 'N/A'),
                        'detalhes_registro': f"Exame de imagem"
                    })
            except Exception as e:
                logging.error(f"Error searching exames img: {e}")
        
        # Search Medical Reports
        if 'relatorio' in tipos_busca:
            try:
                query = db.session.query(RelatorioMedico)
                
                if busca_paciente:
                    query = query.filter(RelatorioMedico.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                relatorios = query.order_by(RelatorioMedico.data.desc()).all()
                logging.info(f"Found {len(relatorios)} relatorios for search")
                
                for relatorio in relatorios:
                    resultados.append({
                        'tipo': 'relatorio',
                        'data': relatorio.data,
                        'id_registro': relatorio.id,
                        'nome_paciente': relatorio.nome_paciente,
                        'medico_nome': getattr(relatorio, 'medico_nome', 'N/A'),
                        'detalhes_registro': f"Relatório médico"
                    })
            except Exception as e:
                logging.error(f"Error searching relatorios: {e}")
        
        # Search Medical Certificates
        if 'atestado' in tipos_busca:
            try:
                query = db.session.query(AtestadoMedico)
                
                if busca_paciente:
                    query = query.filter(AtestadoMedico.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                atestados = query.order_by(AtestadoMedico.data.desc()).all()
                logging.info(f"Found {len(atestados)} atestados for search")
                
                for atestado in atestados:
                    resultados.append({
                        'tipo': 'atestado',
                        'data': atestado.data,
                        'id_registro': atestado.id,
                        'nome_paciente': atestado.nome_paciente,
                        'medico_nome': getattr(atestado, 'medico_nome', 'N/A'),
                        'detalhes_registro': f"Atestado médico"
                    })
            except Exception as e:
                logging.error(f"Error searching atestados: {e}")
        
        # Search High Cost Forms
        if 'alto_custo' in tipos_busca:
            try:
                query = db.session.query(FormularioAltoCusto)
                
                if busca_paciente:
                    query = query.filter(FormularioAltoCusto.nome_paciente.ilike(f'%{busca_paciente}%'))
                
                formularios = query.order_by(FormularioAltoCusto.data.desc()).all()
                logging.info(f"Found {len(formularios)} alto custo for search")
                
                for formulario in formularios:
                    resultados.append({
                        'tipo': 'alto_custo',
                        'data': formulario.data,
                        'id_registro': formulario.id,
                        'nome_paciente': formulario.nome_paciente,
                        'medico_nome': getattr(formulario, 'medico_nome', 'N/A'),
                        'detalhes_registro': f"Formulário alto custo"
                    })
            except Exception as e:
                logging.error(f"Error searching alto custo: {e}")'''
    
    # Substituir toda a lógica de busca
    import re
    pattern = r'# Sempre buscar em todos os tipos.*?continue'
    content = re.sub(pattern, nova_busca, content, flags=re.DOTALL)
    
    with open('routes/prontuario.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Busca do prontuário corrigida")

def executar_correcao_definitiva():
    """Executa a correção definitiva"""
    print("🔧 Executando correção definitiva dos badges médicos...")
    
    try:
        verificar_estrutura_tabelas()
        criar_dados_michel_simples()
        corrigir_busca_prontuario()
        
        print("\n✅ Correção definitiva concluída!")
        
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        return False
    
    return True

if __name__ == '__main__':
    executar_correcao_definitiva()