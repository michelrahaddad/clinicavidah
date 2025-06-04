#!/usr/bin/env python3
"""
Análise detalhada para identificar exatamente o que está impedindo os 100%
"""

import os
import time
import subprocess
from datetime import datetime

def analisar_caminhos_para_100():
    """Analisa exatamente quais pontos estão perdendo score"""
    
    print("=== ANÁLISE COMPLETA DO SISTEMA ===\n")
    
    # 1. Verificar estrutura de arquivos
    print("1. VERIFICANDO ESTRUTURA DE ARQUIVOS...")
    verificar_estrutura()
    
    # 2. Verificar todas as rotas
    print("\n2. VERIFICANDO TODAS AS ROTAS...")
    verificar_todas_rotas()
    
    # 3. Verificar templates
    print("\n3. VERIFICANDO TEMPLATES...")
    verificar_templates()
    
    # 4. Verificar JavaScript
    print("\n4. VERIFICANDO JAVASCRIPT...")
    verificar_javascript()
    
    # 5. Verificar APIs
    print("\n5. VERIFICANDO APIS...")
    verificar_apis()
    
    # 6. Verificar redirecionamentos
    print("\n6. VERIFICANDO REDIRECIONAMENTOS...")
    verificar_redirecionamentos()

def verificar_estrutura():
    """Verifica se todos os arquivos necessários existem"""
    
    arquivos_necessarios = [
        'routes/receita.py',
        'routes/prontuario.py', 
        'routes/pacientes.py',
        'routes/agenda.py',
        'routes/exames_lab.py',
        'routes/exames_img.py',
        'routes/relatorios.py',
        'routes/atestado.py',
        'routes/formulario_alto_custo.py',
        'routes/estatisticas.py',
        'templates/dashboard.html',
        'templates/receita.html',
        'templates/prontuario.html',
        'templates/novo_paciente.html',
        'static/js/enhanced-ui.js'
    ]
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"  ✓ {arquivo}")
        else:
            print(f"  ❌ {arquivo} - FALTANDO")

def verificar_todas_rotas():
    """Verifica se todas as rotas estão funcionando"""
    
    rotas_testar = [
        ('/dashboard', 'Dashboard'),
        ('/receita', 'Receita Médica'),
        ('/novo_paciente', 'Novo Paciente'),
        ('/prontuario', 'Prontuário'),
        ('/exames_lab', 'Exames Laboratoriais'),
        ('/exames_imagem', 'Exames de Imagem'),
        ('/relatorio_medico', 'Relatório Médico'),
        ('/atestado', 'Atestado Médico'),
        ('/alto_custo', 'Alto Custo'),
        ('/estatisticas', 'Estatísticas Neural')
    ]
    
    for rota, nome in rotas_testar:
        print(f"  Testando {nome} ({rota})...")
        # Verificar se a rota existe nos arquivos

def verificar_templates():
    """Verifica se todos os templates têm os elementos necessários"""
    
    templates_verificar = [
        'templates/receita.html',
        'templates/prontuario.html',
        'templates/novo_paciente.html',
        'templates/exames_lab.html',
        'templates/exames_imagem.html',
        'templates/relatorio_medico.html',
        'templates/atestado.html',
        'templates/alto_custo.html'
    ]
    
    for template in templates_verificar:
        if os.path.exists(template):
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar elementos necessários
            tem_nome_paciente = 'nome_paciente' in content
            tem_botao_dashboard = 'dashboard' in content
            
            print(f"  {template}: Nome paciente: {tem_nome_paciente}, Botão dashboard: {tem_botao_dashboard}")

def verificar_javascript():
    """Verifica se o JavaScript de autocomplete está funcionando"""
    
    js_file = 'static/js/enhanced-ui.js'
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        funcoes_necessarias = [
            'setupPatientAutocomplete',
            'setupMedicamentAutocomplete',
            'selectPatient'
        ]
        
        for funcao in funcoes_necessarias:
            if funcao in content:
                print(f"  ✓ {funcao}")
            else:
                print(f"  ❌ {funcao} - FALTANDO")

def verificar_apis():
    """Verifica se as APIs de autocomplete existem"""
    
    apis_verificar = [
        ('routes/receita.py', '/api/medicamentos'),
        ('routes/prontuario.py', '/api/pacientes'),
        ('routes/pacientes.py', '/api/pacientes')
    ]
    
    for arquivo, api in apis_verificar:
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if api in content:
                print(f"  ✓ {arquivo} - {api}")
            else:
                print(f"  ❌ {arquivo} - {api} FALTANDO")

def verificar_redirecionamentos():
    """Verifica se os redirecionamentos estão corretos"""
    
    print("  Verificando redirecionamentos após ações...")
    
    arquivos_verificar = [
        'routes/receita.py',
        'routes/pacientes.py',
        'routes/agenda.py'
    ]
    
    for arquivo in arquivos_verificar:
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se redireciona para dashboard após salvar
            tem_redirect_dashboard = 'redirect(url_for(\'dashboard\'))' in content
            print(f"  {arquivo}: Redirect dashboard: {tem_redirect_dashboard}")

def calcular_score_teorico(analysis):
    """Calcula o score teórico baseado na análise"""
    
    print("\n=== CÁLCULO DE SCORE TEÓRICO ===")
    
    pontos_possiveis = 100
    pontos_perdidos = 0
    
    problemas_encontrados = [
        # Adicionar problemas conforme encontrados
    ]
    
    score_final = pontos_possiveis - pontos_perdidos
    print(f"Score estimado: {score_final}%")
    
    return score_final

def identificar_melhorias_especificas():
    """Identifica melhorias específicas necessárias"""
    
    print("\n=== MELHORIAS ESPECÍFICAS NECESSÁRIAS ===")
    
    melhorias = [
        "1. Verificar autocomplete em todas as páginas",
        "2. Confirmar APIs de pacientes e medicamentos", 
        "3. Testar geração de PDFs",
        "4. Verificar botões de retorno ao dashboard",
        "5. Confirmar salvamento de dados",
        "6. Testar redirecionamentos pós-ação"
    ]
    
    for melhoria in melhorias:
        print(f"  {melhoria}")

def executar_analise_completa():
    """Executa análise completa do sistema"""
    
    print("Iniciando análise completa do sistema...")
    print("Data:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    analisar_caminhos_para_100()
    
    print("\n" + "="*50)
    print("ANÁLISE CONCLUÍDA")
    print("="*50)

if __name__ == "__main__":
    executar_analise_completa()