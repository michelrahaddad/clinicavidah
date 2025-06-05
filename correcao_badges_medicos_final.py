#!/usr/bin/env python3
"""
Correção definitiva dos badges médicos no sistema de prontuário
Resolve o problema dos círculos verdes genéricos substituindo por ícones específicos
"""

import os
import re

def corrigir_template_prontuario():
    """Corrige o template principal do prontuário para exibir badges médicos corretos"""
    
    template_path = "templates/prontuario_modern.html"
    
    # Lê o arquivo atual
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove qualquer implementação de círculo verde genérico
    patterns_to_remove = [
        r'<span[^>]*class="[^"]*badge[^"]*"[^>]*>\s*\{\{\s*grupo\.total_documentos\s*\}\}\s*</span>',
        r'<span[^>]*class="[^"]*circle[^"]*"[^>]*>[^<]*</span>',
        r'<div[^>]*class="[^"]*counter[^"]*"[^>]*>[^<]*</div>',
        r'style="[^"]*border-radius:\s*50%[^"]*"',
        r'class="[^"]*rounded-circle[^"]*"'
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Força o uso apenas dos badges médicos específicos
    badges_section = '''                                <div class="document-badges-container">
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
                                </div>'''
    
    # Encontra e substitui a seção de badges
    badges_pattern = r'<td>\s*<div class="document-badges-container">.*?</div>\s*</td>'
    new_badges_td = f'<td>\n{badges_section}\n                            </td>'
    
    content = re.sub(badges_pattern, new_badges_td, content, flags=re.DOTALL)
    
    # Escreve o arquivo corrigido
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Template prontuario_modern.html corrigido")

def corrigir_logica_agrupamento():
    """Corrige a lógica de agrupamento para detectar corretamente todos os tipos de documentos"""
    
    route_path = "routes/prontuario.py"
    
    # Lê o arquivo atual
    with open(route_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Melhora a busca para incluir todos os tipos de documentos
    busca_melhorada = '''        # Buscar em todos os tipos de documentos se não especificado
        if not filtro_tipo:
            tipos_busca = ['receita', 'exame_lab', 'exame_img', 'relatorio', 'atestado', 'alto_custo']
        else:
            tipos_busca = [filtro_tipo]
            
        logging.info(f"Tipos de busca: {tipos_busca}")'''
    
    # Substitui a lógica de tipos de busca
    pattern = r'# Buscar em todos os tipos.*?tipos_busca = \[filtro_tipo\]'
    content = re.sub(pattern, busca_melhorada, content, flags=re.DOTALL)
    
    # Adiciona logs para debug dos contadores
    log_contadores = '''        # Log dos contadores para debug
        for key, grupo in grupos.items():
            if grupo['nome_paciente'].lower().find('michel') >= 0:
                logging.info(f"Debug Michel - {key}: receitas={grupo['contadores']['receita']}, "
                           f"lab={grupo['contadores']['exame_lab']}, img={grupo['contadores']['exame_img']}, "
                           f"relatorios={grupo['contadores']['relatorio']}, atestados={grupo['contadores']['atestado']}, "
                           f"alto_custo={grupo['contadores']['alto_custo']}")'''
    
    # Adiciona os logs antes do return
    pattern = r'(resultados_agrupados\.sort\(key=lambda x: x\[\'data\'\], reverse=True\))'
    replacement = f'{log_contadores}\n        \n        \\1'
    content = re.sub(pattern, replacement, content)
    
    # Escreve o arquivo corrigido
    with open(route_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Lógica de agrupamento corrigida")

def verificar_dados_michel():
    """Verifica se existem dados para o paciente Michel em todas as tabelas"""
    
    verificacao_script = '''
from app import app, db
from models import *

with app.app_context():
    # Verificar dados do Michel em todas as tabelas
    paciente_nome = "Michel"
    
    receitas = db.session.query(Receita).filter(Receita.nome_paciente.ilike(f'%{paciente_nome}%')).count()
    exames_lab = db.session.query(ExameLab).filter(ExameLab.nome_paciente.ilike(f'%{paciente_nome}%')).count()
    exames_img = db.session.query(ExameImagem).filter(ExameImagem.nome_paciente.ilike(f'%{paciente_nome}%')).count()
    relatorios = db.session.query(RelatorioMedico).filter(RelatorioMedico.nome_paciente.ilike(f'%{paciente_nome}%')).count()
    atestados = db.session.query(AtestadoMedico).filter(AtestadoMedico.nome_paciente.ilike(f'%{paciente_nome}%')).count()
    alto_custo = db.session.query(FormularioAltoCusto).filter(FormularioAltoCusto.nome_paciente.ilike(f'%{paciente_nome}%')).count()
    
    print(f"Dados encontrados para {paciente_nome}:")
    print(f"  Receitas: {receitas}")
    print(f"  Exames Lab: {exames_lab}")
    print(f"  Exames Imagem: {exames_img}")
    print(f"  Relatórios: {relatorios}")
    print(f"  Atestados: {atestados}")
    print(f"  Alto Custo: {alto_custo}")
    print(f"  Total: {receitas + exames_lab + exames_img + relatorios + atestados + alto_custo}")
'''
    
    with open('verificar_michel.py', 'w', encoding='utf-8') as f:
        f.write(verificacao_script)
    
    print("✓ Script de verificação criado: verificar_michel.py")

def executar_correcao_completa():
    """Executa todas as correções necessárias"""
    print("🔧 Iniciando correção completa dos badges médicos...")
    
    try:
        corrigir_template_prontuario()
        corrigir_logica_agrupamento()
        verificar_dados_michel()
        
        print("\n✅ Correção completa dos badges médicos concluída!")
        print("\nPróximos passos:")
        print("1. Execute: python verificar_michel.py")
        print("2. Teste o prontuário com busca por 'Michel'")
        print("3. Verifique se os badges aparecem com os ícones corretos:")
        print("   💊 Receitas | 🧪 Exames Lab | 🩻 Exames Imagem")
        print("   🧾 Relatórios | 📄 Atestados | 💰💊 Alto Custo")
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        return False
    
    return True

if __name__ == '__main__':
    executar_correcao_completa()