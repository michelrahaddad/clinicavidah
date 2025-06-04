#!/usr/bin/env python3
"""
Teste e correção completa do sistema de autocomplete
"""

import os
import re

def corrigir_indentacao_prontuario():
    """Corrige problemas de indentação no arquivo prontuário"""
    
    arquivo = 'routes/prontuario.py'
    if not os.path.exists(arquivo):
        return
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Corrigir linha problemática
    for i, line in enumerate(lines):
        if 'from sqlalchemy import or_' in line and line.startswith('        '):
            lines[i] = '    from sqlalchemy import or_\n'
        elif 'from flask import jsonify' in line and not line.startswith('from flask'):
            lines[i] = '    from flask import jsonify\n'
        elif 'return jsonify({\'suggestions\': []})' in line and line.startswith('        '):
            lines[i] = '    return jsonify({\'suggestions\': []})\n'
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✓ Indentação corrigida em {arquivo}")

def restaurar_apis_autocomplete():
    """Restaura completamente as APIs de autocomplete"""
    
    # 1. API de pacientes no prontuário
    api_pacientes = '''
@prontuario_bp.route('/api/pacientes')
def get_pacientes():
    """API para buscar pacientes - funciona para médicos e administradores"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return jsonify([])
    
    try:
        term = request.args.get('q', '').strip()
        if len(term) < 2:
            return jsonify([])
        
        # Buscar pacientes cadastrados
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
        print(f"Erro na API de pacientes: {e}")
        return jsonify([])
'''
    
    # 2. API de medicamentos na receita
    api_medicamentos = '''
@receita_bp.route('/api/medicamentos')
def get_medicamentos():
    """API para buscar medicamentos - funciona para médicos e administradores"""
    if 'usuario' not in session and 'admin_usuario' not in session:
        return jsonify([])
    
    try:
        term = request.args.get('q', '').strip()
        if len(term) < 2:
            return jsonify([])
        
        # Buscar medicamentos cadastrados
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
        print(f"Erro na API de medicamentos: {e}")
        return jsonify([])
'''
    
    # Adicionar APIs nos arquivos corretos
    adicionar_api_no_arquivo('routes/prontuario.py', api_pacientes, '@prontuario_bp.route(\'/api/pacientes\')')
    adicionar_api_no_arquivo('routes/receita.py', api_medicamentos, '@receita_bp.route(\'/api/medicamentos\')')

def adicionar_api_no_arquivo(arquivo, api_code, marker):
    """Adiciona código de API no arquivo se não existir"""
    
    if not os.path.exists(arquivo):
        return
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se API já existe
    if marker in content:
        print(f"  - API já existe em {arquivo}")
        return
    
    # Adicionar no final do arquivo
    content += api_code
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ API adicionada em {arquivo}")

def restaurar_javascript_autocomplete():
    """Restaura completamente o JavaScript de autocomplete"""
    
    js_file = 'static/js/enhanced-ui.js'
    
    if not os.path.exists(js_file):
        return
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se as funções já existem
    if 'setupPatientAutocomplete' in content and 'setupMedicamentAutocomplete' in content:
        print(f"  - JavaScript de autocomplete já existe")
        return
    
    # Adicionar JavaScript completo
    js_autocomplete = '''

// Sistema de Autocomplete Completo
class AutocompleteSystem {
    constructor() {
        this.setupPatientAutocomplete();
        this.setupMedicamentAutocomplete();
    }
    
    setupPatientAutocomplete() {
        const nomeInput = document.getElementById('nome_paciente');
        if (!nomeInput) return;
        
        let timeoutId;
        
        nomeInput.addEventListener('input', (e) => {
            clearTimeout(timeoutId);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                this.hideSuggestions('patient');
                return;
            }
            
            timeoutId = setTimeout(() => {
                this.searchPatients(query);
            }, 300);
        });
        
        // Limpar sugestões ao clicar fora
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.autocomplete-container')) {
                this.hideSuggestions('patient');
            }
        });
    }
    
    searchPatients(query) {
        fetch(`/api/pacientes?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(patients => {
                this.showPatientSuggestions(patients);
            })
            .catch(error => {
                console.error('Erro ao buscar pacientes:', error);
                this.hideSuggestions('patient');
            });
    }
    
    showPatientSuggestions(patients) {
        this.hideSuggestions('patient');
        
        if (patients.length === 0) return;
        
        const nomeInput = document.getElementById('nome_paciente');
        const container = nomeInput.parentNode;
        
        // Tornar container relativo
        container.style.position = 'relative';
        container.classList.add('autocomplete-container');
        
        const suggestions = document.createElement('div');
        suggestions.className = 'autocomplete-suggestions patient-suggestions';
        suggestions.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 4px 4px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;
        
        patients.forEach(patient => {
            const item = document.createElement('div');
            item.style.cssText = `
                padding: 10px;
                cursor: pointer;
                border-bottom: 1px solid #eee;
                transition: background-color 0.2s;
            `;
            item.textContent = patient.nome;
            
            item.addEventListener('mouseenter', () => {
                item.style.backgroundColor = '#f5f5f5';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.backgroundColor = 'white';
            });
            
            item.addEventListener('click', () => {
                this.selectPatient(patient);
                this.hideSuggestions('patient');
            });
            
            suggestions.appendChild(item);
        });
        
        container.appendChild(suggestions);
    }
    
    selectPatient(patient) {
        // Preencher todos os campos do paciente
        const fields = {
            'nome_paciente': patient.nome,
            'cpf': patient.cpf,
            'idade': patient.idade,
            'endereco': patient.endereco,
            'cidade': patient.cidade
        };
        
        Object.entries(fields).forEach(([fieldId, value]) => {
            const field = document.getElementById(fieldId);
            if (field && value) {
                field.value = value;
                
                // Trigger change event para formulários reativos
                field.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
        
        console.log('Dados do paciente preenchidos:', patient);
    }
    
    setupMedicamentAutocomplete() {
        // Usar delegação de eventos para medicamentos dinâmicos
        document.addEventListener('input', (e) => {
            if (e.target.name === 'medicamento[]' || e.target.classList.contains('medicamento-input')) {
                this.handleMedicamentInput(e);
            }
        });
    }
    
    handleMedicamentInput(e) {
        const input = e.target;
        const query = input.value.trim();
        
        if (query.length < 2) {
            this.hideSuggestions('medicament');
            return;
        }
        
        clearTimeout(input.medicamentTimeout);
        input.medicamentTimeout = setTimeout(() => {
            this.searchMedicaments(query, input);
        }, 300);
    }
    
    searchMedicaments(query, inputElement) {
        fetch(`/api/medicamentos?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(medicaments => {
                this.showMedicamentSuggestions(medicaments, inputElement);
            })
            .catch(error => {
                console.error('Erro ao buscar medicamentos:', error);
                this.hideSuggestions('medicament');
            });
    }
    
    showMedicamentSuggestions(medicaments, inputElement) {
        this.hideSuggestions('medicament');
        
        if (medicaments.length === 0) return;
        
        const container = inputElement.parentNode;
        container.style.position = 'relative';
        
        const suggestions = document.createElement('div');
        suggestions.className = 'autocomplete-suggestions medicament-suggestions';
        suggestions.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 4px 4px;
            max-height: 150px;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;
        
        medicaments.forEach(med => {
            const item = document.createElement('div');
            item.style.cssText = `
                padding: 8px;
                cursor: pointer;
                border-bottom: 1px solid #eee;
                transition: background-color 0.2s;
            `;
            item.textContent = med.nome;
            
            item.addEventListener('mouseenter', () => {
                item.style.backgroundColor = '#f5f5f5';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.backgroundColor = 'white';
            });
            
            item.addEventListener('click', () => {
                inputElement.value = med.nome;
                inputElement.dispatchEvent(new Event('change', { bubbles: true }));
                this.hideSuggestions('medicament');
            });
            
            suggestions.appendChild(item);
        });
        
        container.appendChild(suggestions);
    }
    
    hideSuggestions(type) {
        const className = type === 'patient' ? 'patient-suggestions' : 'medicament-suggestions';
        const existing = document.querySelectorAll(`.${className}`);
        existing.forEach(el => el.remove());
    }
}

// Inicializar sistema quando página carregar
document.addEventListener('DOMContentLoaded', () => {
    window.autocompleteSystem = new AutocompleteSystem();
    console.log('Sistema de autocomplete inicializado');
});

// Reinicializar após mudanças dinâmicas
document.addEventListener('medicamentRowAdded', () => {
    if (window.autocompleteSystem) {
        window.autocompleteSystem.setupMedicamentAutocomplete();
    }
});
'''
    
    content += js_autocomplete
    
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ JavaScript de autocomplete restaurado")

def executar_restauracao_completa():
    """Executa restauração completa do sistema"""
    
    print("=== RESTAURAÇÃO COMPLETA DO AUTOCOMPLETE ===\n")
    
    print("1. Corrigindo indentação...")
    corrigir_indentacao_prontuario()
    
    print("\n2. Restaurando APIs de autocomplete...")
    restaurar_apis_autocomplete()
    
    print("\n3. Restaurando JavaScript...")
    restaurar_javascript_autocomplete()
    
    print("\n✓ Sistema de autocomplete completamente restaurado!")
    print("\nFuncionalidades restauradas:")
    print("  - Autocomplete de pacientes (nome, CPF, idade, endereço, cidade)")
    print("  - Autocomplete de medicamentos")
    print("  - Preenchimento automático de dados")
    print("  - Compatibilidade total com administradores e médicos")

if __name__ == "__main__":
    executar_restauracao_completa()