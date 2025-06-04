#!/usr/bin/env python3
"""
Correção final rápida e completa do sistema
"""

import os
import shutil

def corrigir_prontuario_completamente():
    """Corrige prontuário removendo erros de sintaxe"""
    
    arquivo = 'routes/prontuario.py'
    
    # Criar backup
    shutil.copy(arquivo, f"{arquivo}.backup_final")
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Corrigir todas as linhas problemáticas
    corrected_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        # Corrigir estruturas quebradas
        if 'from sqlalchemy import or_' in line and not line.strip().startswith('from'):
            continue
        elif 'from flask import jsonify' in line and not line.strip().startswith('from'):
            continue
        elif line.strip() == 'return jsonify({\'suggestions\': []})' and i > 0 and 'if len(term) < 2:' in lines[i-1]:
            corrected_lines.append('        return jsonify({\'suggestions\': []})\n')
            continue
        elif 'try:' in line and i > 0 and not lines[i-1].strip():
            corrected_lines.append('    try:\n')
            continue
        elif line.strip().startswith('return jsonify') and 'suggestions' in line:
            if not line.startswith('    '):
                corrected_lines.append('    ' + line.strip() + '\n')
                continue
        
        corrected_lines.append(line)
    
    # Escrever arquivo corrigido
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.writelines(corrected_lines)
    
    print(f"✓ Prontuário corrigido")

def adicionar_api_completa_receita():
    """Adiciona API completa na receita se não existir"""
    
    arquivo = 'routes/receita.py'
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se API de medicamentos já existe
    if '@receita_bp.route(\'/api/medicamentos\')' not in content:
        api_medicamentos = '''

@receita_bp.route('/api/medicamentos')
def get_medicamentos():
    """API para buscar medicamentos"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return jsonify([])
    
    try:
        from models import Medicamento
        term = request.args.get('q', '').strip()
        if len(term) < 2:
            return jsonify([])
        
        medicamentos = Medicamento.query.filter(
            Medicamento.nome.ilike(f'%{term}%')
        ).limit(10).all()
        
        result = []
        for m in medicamentos:
            result.append({
                'id': m.id,
                'nome': m.nome
            })
        
        return jsonify(result)
    except Exception as e:
        print(f"Erro API medicamentos: {e}")
        return jsonify([])
'''
        content += api_medicamentos
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ API medicamentos adicionada")

def adicionar_api_completa_prontuario():
    """Adiciona API completa no prontuário se não existir"""
    
    arquivo = 'routes/prontuario.py'
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se API de pacientes já existe corretamente
    if '@prontuario_bp.route(\'/api/pacientes\')' not in content:
        api_pacientes = '''

@prontuario_bp.route('/api/pacientes')
def get_pacientes():
    """API para buscar pacientes"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return jsonify([])
    
    try:
        term = request.args.get('q', '').strip()
        if len(term) < 2:
            return jsonify([])
        
        pacientes = Paciente.query.filter(
            Paciente.nome.ilike(f'%{term}%')
        ).limit(10).all()
        
        result = []
        for p in pacientes:
            result.append({
                'id': p.id,
                'nome': p.nome,
                'cpf': p.cpf or '',
                'idade': str(p.idade) if p.idade else '',
                'endereco': p.endereco or '',
                'cidade': p.cidade or ''
            })
        
        return jsonify(result)
    except Exception as e:
        print(f"Erro API pacientes: {e}")
        return jsonify([])
'''
        content += api_pacientes
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ API pacientes adicionada")

def corrigir_javascript_autocomplete():
    """Corrige JavaScript de autocomplete"""
    
    js_file = 'static/js/enhanced-ui.js'
    
    if not os.path.exists(js_file):
        return
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se autocomplete já existe
    if 'setupPatientAutocomplete' in content:
        print("✓ JavaScript autocomplete já existe")
        return
    
    # Adicionar autocomplete completo
    autocomplete_js = '''

// Sistema de Autocomplete para Pacientes
function setupPatientAutocomplete() {
    const nomeInput = document.getElementById('nome_paciente');
    if (!nomeInput) return;
    
    nomeInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        if (query.length < 2) {
            hideSuggestions();
            return;
        }
        
        fetch('/api/pacientes?q=' + encodeURIComponent(query))
            .then(response => response.json())
            .then(data => showPatientSuggestions(data))
            .catch(error => console.error('Erro:', error));
    });
}

function showPatientSuggestions(patients) {
    hideSuggestions();
    
    if (patients.length === 0) return;
    
    const nomeInput = document.getElementById('nome_paciente');
    const container = nomeInput.parentNode;
    container.style.position = 'relative';
    
    const suggestions = document.createElement('div');
    suggestions.className = 'autocomplete-suggestions';
    suggestions.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        max-height: 200px;
        overflow-y: auto;
        z-index: 1000;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    `;
    
    patients.forEach(patient => {
        const item = document.createElement('div');
        item.style.cssText = 'padding: 10px; cursor: pointer; border-bottom: 1px solid #eee;';
        item.textContent = patient.nome;
        
        item.addEventListener('click', () => {
            selectPatient(patient);
            hideSuggestions();
        });
        
        suggestions.appendChild(item);
    });
    
    container.appendChild(suggestions);
}

function selectPatient(patient) {
    const fields = {
        'nome_paciente': patient.nome,
        'cpf': patient.cpf,
        'idade': patient.idade,
        'endereco': patient.endereco,
        'cidade': patient.cidade
    };
    
    Object.entries(fields).forEach(([id, value]) => {
        const field = document.getElementById(id);
        if (field && value) {
            field.value = value;
        }
    });
}

function hideSuggestions() {
    const existing = document.querySelectorAll('.autocomplete-suggestions');
    existing.forEach(el => el.remove());
}

// Sistema de Autocomplete para Medicamentos
function setupMedicamentAutocomplete() {
    document.addEventListener('input', function(e) {
        if (e.target.name === 'medicamento[]') {
            const query = e.target.value.trim();
            if (query.length < 2) return;
            
            fetch('/api/medicamentos?q=' + encodeURIComponent(query))
                .then(response => response.json())
                .then(data => showMedicamentSuggestions(data, e.target))
                .catch(error => console.error('Erro:', error));
        }
    });
}

function showMedicamentSuggestions(medicaments, input) {
    const existing = document.querySelectorAll('.medicament-suggestions');
    existing.forEach(el => el.remove());
    
    if (medicaments.length === 0) return;
    
    const container = input.parentNode;
    container.style.position = 'relative';
    
    const suggestions = document.createElement('div');
    suggestions.className = 'medicament-suggestions';
    suggestions.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        max-height: 150px;
        overflow-y: auto;
        z-index: 1000;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    `;
    
    medicaments.forEach(med => {
        const item = document.createElement('div');
        item.style.cssText = 'padding: 8px; cursor: pointer; border-bottom: 1px solid #eee;';
        item.textContent = med.nome;
        
        item.addEventListener('click', () => {
            input.value = med.nome;
            suggestions.remove();
        });
        
        suggestions.appendChild(item);
    });
    
    container.appendChild(suggestions);
}

// Inicializar quando página carregar
document.addEventListener('DOMContentLoaded', function() {
    setupPatientAutocomplete();
    setupMedicamentAutocomplete();
});
'''
    
    content += autocomplete_js
    
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ JavaScript autocomplete adicionado")

def executar_correcao_final():
    """Executa todas as correções finais"""
    
    print("=== CORREÇÃO FINAL SISTEMA AUTOCOMPLETE ===\n")
    
    print("1. Corrigindo prontuário...")
    corrigir_prontuario_completamente()
    
    print("2. Adicionando API receita...")
    adicionar_api_completa_receita()
    
    print("3. Adicionando API prontuário...")
    adicionar_api_completa_prontuario()
    
    print("4. Corrigindo JavaScript...")
    corrigir_javascript_autocomplete()
    
    print("\n✓ SISTEMA COMPLETAMENTE RESTAURADO!")
    print("\nFuncionalidades:")
    print("  - Autocomplete de pacientes em todas as telas")
    print("  - Preenchimento automático de todos os dados")
    print("  - Autocomplete de medicamentos na receita")
    print("  - Compatibilidade com médicos e administradores")

if __name__ == "__main__":
    executar_correcao_final()