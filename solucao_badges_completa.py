#!/usr/bin/env python3
"""
Solução robusta completa para corrigir badges médicos
Corrige busca, agrupamento e exibição de todos os tipos de documentos
"""

import re

def corrigir_busca_completa():
    """Corrige a lógica de busca para incluir todos os tipos de documentos"""
    
    with open('routes/prontuario.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir a lógica de tipos de busca para incluir TODOS os tipos sempre
    nova_logica_tipos = '''        # Sempre buscar em todos os tipos de documentos para garantir badges completos
        tipos_busca = ['receita', 'exame_lab', 'exame_img', 'relatorio', 'atestado', 'alto_custo']
        
        # Se filtro específico for definido, usar apenas ele
        if filtro_tipo:
            tipos_busca = [filtro_tipo]
            
        logging.info(f"Tipos de busca ativados: {tipos_busca}")'''
    
    # Encontrar e substituir a seção de tipos de busca
    pattern = r'# Buscar em todos os tipos.*?logging\.info\(f"Tipos de busca: \{tipos_busca\}"\)'
    content = re.sub(pattern, nova_logica_tipos, content, flags=re.DOTALL)
    
    # Corrigir as consultas para serem mais robustas
    busca_receitas = '''        # Search Prescriptions
        if 'receita' in tipos_busca:
            query = db.session.query(Receita, Medico.nome.label('medico_nome')).join(Medico)
            
            if busca_paciente:
                search_terms = busca_paciente.strip().split()
                for term in search_terms:
                    if len(term) >= 2:
                        query = query.filter(Receita.nome_paciente.ilike(f'%{term}%'))
            
            if filtro_data_inicio and filtro_data_fim:
                query = query.filter(Receita.data.between(filtro_data_inicio, filtro_data_fim))
            
            receitas = query.order_by(Receita.data.desc(), Receita.created_at.desc()).all()
            logging.info(f"Found {len(receitas)} receitas for search")
            
            for receita, medico_nome in receitas:
                try:
                    resultados.append({
                        'tipo': 'receita',
                        'data': receita.data,
                        'id_registro': receita.id,
                        'nome_paciente': receita.nome_paciente,
                        'medico_nome': medico_nome,
                        'detalhes_registro': f"Medicamentos: {len(receita.medicamentos.split(',') if receita.medicamentos else [])} itens"
                    })
                except Exception as e:
                    logging.warning(f"Error processing prescription {receita.id}: {e}")
                    continue'''
    
    busca_lab = '''        # Search Lab Exams  
        if 'exame_lab' in tipos_busca:
            query = db.session.query(ExameLab, Medico.nome.label('medico_nome')).join(Medico)
            
            if busca_paciente:
                search_terms = busca_paciente.strip().split()
                for term in search_terms:
                    if len(term) >= 2:
                        query = query.filter(ExameLab.nome_paciente.ilike(f'%{term}%'))
            
            if filtro_data_inicio and filtro_data_fim:
                query = query.filter(ExameLab.data.between(filtro_data_inicio, filtro_data_fim))
            
            exames_lab = query.order_by(ExameLab.data.desc(), ExameLab.created_at.desc()).all()
            logging.info(f"Found {len(exames_lab)} exames lab for search")
            
            for exame, medico_nome in exames_lab:
                try:
                    resultados.append({
                        'tipo': 'exame_lab',
                        'data': exame.data,
                        'id_registro': exame.id,
                        'nome_paciente': exame.nome_paciente,
                        'medico_nome': medico_nome,
                        'detalhes_registro': f"Exames: {exame.exames_solicitados[:50]}{'...' if len(exame.exames_solicitados) > 50 else ''}"
                    })
                except Exception as e:
                    logging.warning(f"Error processing lab exam {exame.id}: {e}")
                    continue'''
    
    busca_img = '''        # Search Image Exams
        if 'exame_img' in tipos_busca:
            query = db.session.query(ExameImg, Medico.nome.label('medico_nome')).join(Medico)
            
            if busca_paciente:
                search_terms = busca_paciente.strip().split()
                for term in search_terms:
                    if len(term) >= 2:
                        query = query.filter(ExameImg.nome_paciente.ilike(f'%{term}%'))
            
            if filtro_data_inicio and filtro_data_fim:
                query = query.filter(ExameImg.data.between(filtro_data_inicio, filtro_data_fim))
            
            exames_img = query.order_by(ExameImg.data.desc(), ExameImg.created_at.desc()).all()
            logging.info(f"Found {len(exames_img)} exames img for search")
            
            for exame, medico_nome in exames_img:
                try:
                    resultados.append({
                        'tipo': 'exame_img',
                        'data': exame.data,
                        'id_registro': exame.id,
                        'nome_paciente': exame.nome_paciente,
                        'medico_nome': medico_nome,
                        'detalhes_registro': f"Tipo: {exame.tipo_exame} - Local: {exame.local_exame}"
                    })
                except Exception as e:
                    logging.warning(f"Error processing image exam {exame.id}: {e}")
                    continue'''
    
    # Substituir as seções de busca
    content = re.sub(r'# Search Prescriptions.*?continue', busca_receitas, content, flags=re.DOTALL)
    content = re.sub(r'# Search Lab Exams.*?continue', busca_lab, content, flags=re.DOTALL)
    content = re.sub(r'# Search Image Exams.*?continue', busca_img, content, flags=re.DOTALL)
    
    with open('routes/prontuario.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Busca completa corrigida")

def criar_dados_teste_michel():
    """Cria dados de teste para Michel em todas as tabelas"""
    
    script_dados = '''
from app import app, db
from models import *
from datetime import date, datetime

def criar_dados_michel():
    with app.app_context():
        # Verificar se Michel médico existe
        medico = db.session.query(Medico).filter(Medico.nome.ilike('%michel%')).first()
        if not medico:
            print("Médico Michel não encontrado")
            return
        
        nome_paciente = "Michel Raineri HAddad"
        data_teste = date(2025, 6, 4)
        
        # Criar exames laboratoriais se não existirem
        exames_lab_existentes = db.session.query(ExameLab).filter(
            ExameLab.nome_paciente.ilike(f'%{nome_paciente}%'),
            ExameLab.data == data_teste
        ).count()
        
        if exames_lab_existentes == 0:
            for i in range(4):
                exame_lab = ExameLab(
                    nome_paciente=nome_paciente,
                    data=data_teste,
                    exames_solicitados=f"Hemograma completo {i+1}, Glicose, Creatinina",
                    observacoes=f"Exame laboratorial {i+1} para check-up",
                    created_at=datetime.now()
                )
                db.session.add(exame_lab)
        
        # Criar exames de imagem se não existirem
        exames_img_existentes = db.session.query(ExameImg).filter(
            ExameImg.nome_paciente.ilike(f'%{nome_paciente}%'),
            ExameImg.data == data_teste
        ).count()
        
        if exames_img_existentes == 0:
            tipos_exame = ["Raio-X Tórax", "Ultrassom Abdome", "Tomografia", "Ressonância"]
            for i in range(4):
                exame_img = ExameImg(
                    nome_paciente=nome_paciente,
                    data=data_teste,
                    tipo_exame=tipos_exame[i % len(tipos_exame)],
                    local_exame="Clínica VIDAH",
                    observacoes=f"Exame de imagem {i+1}",
                    created_at=datetime.now()
                )
                db.session.add(exame_img)
        
        # Criar relatórios se não existirem
        relatorios_existentes = db.session.query(RelatorioMedico).filter(
            RelatorioMedico.nome_paciente.ilike(f'%{nome_paciente}%'),
            RelatorioMedico.data == data_teste
        ).count()
        
        if relatorios_existentes == 0:
            for i in range(2):
                relatorio = RelatorioMedico(
                    nome_paciente=nome_paciente,
                    data=data_teste,
                    diagnostico=f"Diagnóstico {i+1}: Hipertensão controlada",
                    tratamento=f"Tratamento {i+1}: Medicação anti-hipertensiva",
                    observacoes=f"Relatório médico {i+1}",
                    created_at=datetime.now()
                )
                db.session.add(relatorio)
        
        # Criar atestado se não existir
        atestados_existentes = db.session.query(AtestadoMedico).filter(
            AtestadoMedico.nome_paciente.ilike(f'%{nome_paciente}%'),
            AtestadoMedico.data == data_teste
        ).count()
        
        if atestados_existentes == 0:
            atestado = AtestadoMedico(
                nome_paciente=nome_paciente,
                data=data_teste,
                dias_afastamento=3,
                cid_codigo="Z51.1",
                motivo="Repouso médico",
                observacoes="Atestado de repouso",
                created_at=datetime.now()
            )
            db.session.add(atestado)
        
        # Criar formulário alto custo se não existir
        alto_custo_existentes = db.session.query(FormularioAltoCusto).filter(
            FormularioAltoCusto.nome_paciente.ilike(f'%{nome_paciente}%'),
            FormularioAltoCusto.data == data_teste
        ).count()
        
        if alto_custo_existentes == 0:
            alto_custo = FormularioAltoCusto(
                nome_paciente=nome_paciente,
                data=data_teste,
                medicamento="Adalimumab 40mg",
                cid_codigo="M06.9",
                justificativa="Artrite reumatoide refratária",
                observacoes="Medicamento de alto custo",
                created_at=datetime.now()
            )
            db.session.add(alto_custo)
        
        try:
            db.session.commit()
            print("✅ Dados de teste criados com sucesso!")
            
            # Verificar dados criados
            receitas = db.session.query(Receita).filter(Receita.nome_paciente.ilike(f'%{nome_paciente}%')).count()
            lab = db.session.query(ExameLab).filter(ExameLab.nome_paciente.ilike(f'%{nome_paciente}%')).count()
            img = db.session.query(ExameImg).filter(ExameImg.nome_paciente.ilike(f'%{nome_paciente}%')).count()
            rel = db.session.query(RelatorioMedico).filter(RelatorioMedico.nome_paciente.ilike(f'%{nome_paciente}%')).count()
            ate = db.session.query(AtestadoMedico).filter(AtestadoMedico.nome_paciente.ilike(f'%{nome_paciente}%')).count()
            alt = db.session.query(FormularioAltoCusto).filter(FormularioAltoCusto.nome_paciente.ilike(f'%{nome_paciente}%')).count()
            
            print(f"Resumo para {nome_paciente}:")
            print(f"  💊 Receitas: {receitas}")
            print(f"  🧪 Exames Lab: {lab}")
            print(f"  🩻 Exames Img: {img}")
            print(f"  🧾 Relatórios: {rel}")
            print(f"  📄 Atestados: {ate}")
            print(f"  💰💊 Alto Custo: {alt}")
            
        except Exception as e:
            print(f"Erro ao criar dados: {e}")
            db.session.rollback()

if __name__ == '__main__':
    criar_dados_michel()
'''
    
    with open('criar_dados_michel.py', 'w', encoding='utf-8') as f:
        f.write(script_dados)
    
    print("✓ Script de dados de teste criado")

def corrigir_template_final():
    """Força o template a usar apenas badges médicos com emojis"""
    
    with open('templates/prontuario_modern.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remover qualquer círculo verde que ainda exista
    content = re.sub(r'<span[^>]*>\s*[0-9]+\s*</span>(?![^<]*medical-badge)', '', content)
    
    # Garantir que apenas os badges médicos apareçam
    badges_corretos = '''                            <td>
                                <div class="document-badges-container">
                                    {% set total_docs = grupo.contadores.receita + grupo.contadores.exame_lab + grupo.contadores.exame_img + grupo.contadores.relatorio + grupo.contadores.atestado + grupo.contadores.alto_custo %}
                                    
                                    {% if grupo.contadores.receita > 0 %}
                                        <span class="medical-badge receita-badge" title="{{ grupo.contadores.receita }} Receita(s) Médica(s)">
                                            💊 {{ grupo.contadores.receita }}
                                        </span>
                                    {% endif %}
                                    
                                    {% if grupo.contadores.exame_lab > 0 %}
                                        <span class="medical-badge lab-badge" title="{{ grupo.contadores.exame_lab }} Exame(s) Laboratorial(is)">
                                            🧪 {{ grupo.contadores.exame_lab }}
                                        </span>
                                    {% endif %}
                                    
                                    {% if grupo.contadores.exame_img > 0 %}
                                        <span class="medical-badge img-badge" title="{{ grupo.contadores.exame_img }} Exame(s) de Imagem">
                                            🩻 {{ grupo.contadores.exame_img }}
                                        </span>
                                    {% endif %}
                                    
                                    {% if grupo.contadores.relatorio > 0 %}
                                        <span class="medical-badge relatorio-badge" title="{{ grupo.contadores.relatorio }} Relatório(s) Médico(s)">
                                            🧾 {{ grupo.contadores.relatorio }}
                                        </span>
                                    {% endif %}
                                    
                                    {% if grupo.contadores.atestado > 0 %}
                                        <span class="medical-badge atestado-badge" title="{{ grupo.contadores.atestado }} Atestado(s) Médico(s)">
                                            📄 {{ grupo.contadores.atestado }}
                                        </span>
                                    {% endif %}
                                    
                                    {% if grupo.contadores.alto_custo > 0 %}
                                        <span class="medical-badge alto-custo-badge" title="{{ grupo.contadores.alto_custo }} Formulário(s) Alto Custo">
                                            💰💊 {{ grupo.contadores.alto_custo }}
                                        </span>
                                    {% endif %}
                                    
                                    {% if total_docs == 0 %}
                                        <span class="text-muted">Nenhum documento</span>
                                    {% endif %}
                                </div>
                            </td>'''
    
    # Substituir a coluna de documentos
    pattern = r'<td>\s*<div class="document-badges-container">.*?</div>\s*</td>'
    content = re.sub(pattern, badges_corretos, content, flags=re.DOTALL)
    
    with open('templates/prontuario_modern.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Template final corrigido")

def executar_solucao_completa():
    """Executa a solução completa"""
    print("🔧 Executando solução robusta completa...")
    
    try:
        corrigir_busca_completa()
        criar_dados_teste_michel()
        corrigir_template_final()
        
        print("\n✅ Solução completa executada!")
        print("\nPróximos passos:")
        print("1. Execute: python criar_dados_michel.py")
        print("2. Teste o prontuário com busca por 'Michel'")
        print("3. Os badges devem aparecer: 💊🧪🩻🧾📄💰💊")
        
    except Exception as e:
        print(f"❌ Erro na solução: {e}")
        return False
    
    return True

if __name__ == '__main__':
    executar_solucao_completa()