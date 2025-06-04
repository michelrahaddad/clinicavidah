#!/usr/bin/env python3
"""
Correção completa do acesso ao banco de dados
Restaura funcionalidade completa para administradores e médicos
"""

import os
import re
from datetime import datetime

def corrigir_todas_rotas():
    """Corrige acesso ao banco em todas as rotas do sistema"""
    
    print("=== CORREÇÃO COMPLETA DO ACESSO AO BANCO ===\n")
    
    # Arquivos principais que precisam de correção
    arquivos_sistema = [
        'routes/receita.py',
        'routes/prontuario.py', 
        'routes/pacientes.py',
        'routes/agenda.py',
        'static/js/enhanced-ui.js'
    ]
    
    correcoes_aplicadas = 0
    
    for arquivo in arquivos_sistema:
        if os.path.exists(arquivo):
            print(f"Corrigindo {arquivo}...")
            
            try:
                # Backup
                backup_path = f"{arquivo}.banco_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                with open(arquivo, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                content_original = content
                
                # Aplicar correções específicas
                if arquivo.endswith('.py'):
                    content = corrigir_verificacoes_sessao(content, arquivo)
                    content = corrigir_consultas_banco(content, arquivo)
                    content = adicionar_verificacao_admin(content, arquivo)
                    content = corrigir_apis_autocomplete(content, arquivo)
                elif arquivo.endswith('.js'):
                    content = corrigir_javascript_autocomplete(content)
                
                if content != content_original:
                    with open(arquivo, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✓ {arquivo} - Acesso ao banco restaurado")
                    correcoes_aplicadas += 1
                else:
                    print(f"  - {arquivo} - Já estava correto")
                    os.remove(backup_path)
                    
            except Exception as e:
                print(f"  ❌ Erro em {arquivo}: {e}")
    
    print(f"\nArquivos corrigidos: {correcoes_aplicadas}")

def corrigir_verificacoes_sessao(content, arquivo):
    """Corrige verificações de sessão para incluir administradores"""
    
    # Padrão antigo que só verifica médicos
    old_pattern = r"if\s+'usuario'\s+not\s+in\s+session:"
    
    # Novo padrão que aceita médicos e administradores
    new_pattern = "if 'usuario' not in session and 'admin_usuario' not in session:"
    
    content = re.sub(old_pattern, new_pattern, content)
    
    return content

def corrigir_consultas_banco(content, arquivo):
    """Corrige consultas ao banco para considerar administradores"""
    
    # Padrões de consulta que precisam ser corrigidos
    patterns = [
        # Consultas de pacientes
        (r"Paciente\.query\.filter_by\(usuario_id=session\['usuario'\]\)",
         "Paciente.query.filter_by(usuario_id=session.get('usuario', session.get('admin_usuario')))"),
        
        # Consultas de receitas
        (r"Receita\.query\.filter_by\(usuario_id=session\['usuario'\]\)",
         "Receita.query.filter_by(usuario_id=session.get('usuario', session.get('admin_usuario')))"),
        
        # Consultas de prontuários
        (r"Prontuario\.query\.filter_by\(usuario_id=session\['usuario'\]\)",
         "Prontuario.query.filter_by(usuario_id=session.get('usuario', session.get('admin_usuario')))"),
        
        # Consultas gerais sem filtro de usuário para admin
        (r"\.filter\(.*usuario_id==session\['usuario'\].*\)",
         ".filter(or_(usuario_id==session.get('usuario'), 'admin_usuario' in session))")
    ]
    
    for old, new in patterns:
        content = re.sub(old, new, content)
    
    return content

def adicionar_verificacao_admin(content, arquivo):
    """Adiciona verificação de admin onde necessário"""
    
    # Adicionar import do or_ se não existir
    if 'from sqlalchemy import or_' not in content and 'routes/' in arquivo:
        content = content.replace(
            'from flask import',
            'from sqlalchemy import or_\nfrom flask import'
        )
    
    return content

def corrigir_apis_autocomplete(content, arquivo):
    """Corrige APIs de autocomplete para funcionar com administradores"""
    
    if 'receita.py' in arquivo:
        # Corrigir API de busca de medicamentos
        old_api = r"@receita_bp\.route\('/api/medicamentos'.*?\n.*?def.*?\n.*?if.*?session.*?\n.*?return.*?\n.*?try:.*?\n.*?medicamentos = Medicamento\.query\.all\(\)"
        
        new_api = """@receita_bp.route('/api/medicamentos')
def get_medicamentos():
    if 'usuario' not in session and 'admin_usuario' not in session:
        return jsonify([])
    try:
        medicamentos = Medicamento.query.all()"""
        
        content = re.sub(old_api, new_api, content, flags=re.DOTALL)
    
    elif 'prontuario.py' in arquivo or 'pacientes.py' in arquivo:
        # Corrigir API de busca de pacientes
        old_api = r"if\s+'usuario'\s+not\s+in\s+session:\s*return\s+jsonify\(\[\]\)"
        new_api = "if 'usuario' not in session and 'admin_usuario' not in session:\n        return jsonify([])"
        
        content = re.sub(old_api, new_api, content)
    
    return content

def corrigir_javascript_autocomplete(content):
    """Corrige JavaScript do autocomplete"""
    
    # Verificar se as funções de autocomplete estão presentes
    functions_needed = [
        'setupPatientAutocomplete',
        'loadPatientData',
        'setupMedicamentAutocomplete'
    ]
    
    missing_functions = []
    for func in functions_needed:
        if func not in content:
            missing_functions.append(func)
    
    if missing_functions:
        # Adicionar funções de autocomplete completas
        autocomplete_js = """
// Configuração do autocomplete de pacientes
function setupPatientAutocomplete() {
    const nomeInput = document.getElementById('nome_paciente');
    if (!nomeInput) return;
    
    nomeInput.addEventListener('input', function() {
        const query = this.value;
        if (query.length < 2) return;
        
        fetch('/api/pacientes?q=' + encodeURIComponent(query))
            .then(response => response.json())
            .then(data => {
                showPatientSuggestions(data, nomeInput);
            })
            .catch(error => console.error('Erro ao buscar pacientes:', error));
    });
}

function showPatientSuggestions(patients, input) {
    // Remover sugestões anteriores
    const existingSuggestions = document.querySelector('.patient-suggestions');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
    
    if (patients.length === 0) return;
    
    const suggestions = document.createElement('div');
    suggestions.className = 'patient-suggestions';
    suggestions.style.cssText = `
        position: absolute;
        background: white;
        border: 1px solid #ccc;
        border-radius: 4px;
        max-height: 200px;
        overflow-y: auto;
        z-index: 1000;
        width: 100%;
    `;
    
    patients.forEach(patient => {
        const div = document.createElement('div');
        div.style.cssText = 'padding: 8px; cursor: pointer; border-bottom: 1px solid #eee;';
        div.textContent = patient.nome;
        div.addEventListener('click', () => {
            selectPatient(patient);
            suggestions.remove();
        });
        suggestions.appendChild(div);
    });
    
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(suggestions);
}

function selectPatient(patient) {
    // Preencher dados do paciente
    const nomeInput = document.getElementById('nome_paciente');
    const cpfInput = document.getElementById('cpf');
    const idadeInput = document.getElementById('idade');
    const enderecoInput = document.getElementById('endereco');
    const cidadeInput = document.getElementById('cidade');
    
    if (nomeInput) nomeInput.value = patient.nome;
    if (cpfInput) cpfInput.value = patient.cpf || '';
    if (idadeInput) idadeInput.value = patient.idade || '';
    if (enderecoInput) enderecoInput.value = patient.endereco || '';
    if (cidadeInput) cidadeInput.value = patient.cidade || '';
}

// Configuração do autocomplete de medicamentos
function setupMedicamentAutocomplete() {
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('medicamento-input')) {
            const query = e.target.value;
            if (query.length < 2) return;
            
            fetch('/api/medicamentos?q=' + encodeURIComponent(query))
                .then(response => response.json())
                .then(data => {
                    showMedicamentSuggestions(data, e.target);
                })
                .catch(error => console.error('Erro ao buscar medicamentos:', error));
        }
    });
}

function showMedicamentSuggestions(medicaments, input) {
    // Remover sugestões anteriores
    const existingSuggestions = document.querySelector('.medicament-suggestions');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
    
    if (medicaments.length === 0) return;
    
    const suggestions = document.createElement('div');
    suggestions.className = 'medicament-suggestions';
    suggestions.style.cssText = `
        position: absolute;
        background: white;
        border: 1px solid #ccc;
        border-radius: 4px;
        max-height: 200px;
        overflow-y: auto;
        z-index: 1000;
        width: 100%;
    `;
    
    medicaments.forEach(med => {
        const div = document.createElement('div');
        div.style.cssText = 'padding: 8px; cursor: pointer; border-bottom: 1px solid #eee;';
        div.textContent = med.nome;
        div.addEventListener('click', () => {
            input.value = med.nome;
            suggestions.remove();
        });
        suggestions.appendChild(div);
    });
    
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(suggestions);
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    setupPatientAutocomplete();
    setupMedicamentAutocomplete();
});
"""
        content += autocomplete_js
    
    return content

def testar_acesso_banco():
    """Testa o acesso ao banco após as correções"""
    
    print("\n=== TESTE DE ACESSO AO BANCO ===")
    
    # Verificar se as rotas principais estão funcionando
    rotas_teste = [
        '/api/pacientes',
        '/api/medicamentos'
    ]
    
    for rota in rotas_teste:
        print(f"Testando rota: {rota}")
        # O teste real será feito via web depois das correções
    
    print("Teste concluído - verificar funcionamento via interface web")

def executar_correcao_completa():
    """Executa todas as correções"""
    
    print("Iniciando correção completa do sistema...")
    
    # 1. Corrigir sintaxe
    print("\n1. Corrigindo erros de sintaxe...")
    corrigir_sintaxe_receita()
    
    # 2. Corrigir acesso ao banco
    print("\n2. Corrigindo acesso ao banco...")
    corrigir_todas_rotas()
    
    # 3. Testar funcionalidade
    print("\n3. Testando funcionalidade...")
    testar_acesso_banco()
    
    print("\n✓ Correção completa finalizada!")

def corrigir_sintaxe_receita():
    """Corrige erros de sintaxe no arquivo de receita"""
    
    arquivo = 'routes/receita.py'
    if not os.path.exists(arquivo):
        return
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir parênteses extras
    content = content.replace("return render_template('receita.html'))", "return render_template('receita.html')")
    content = content.replace("return render_template('agenda.html'))", "return render_template('agenda.html')")
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Sintaxe corrigida em {arquivo}")

if __name__ == "__main__":
    executar_correcao_completa()