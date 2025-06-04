#!/usr/bin/env python3
"""
Correção de redirecionamentos para manter páginas na mesma localização
"""

import os
import re
from datetime import datetime

def corrigir_redirecionamentos():
    """Corrige redirecionamentos em todas as rotas do sistema"""
    
    print("=== CORREÇÃO DE REDIRECIONAMENTOS ===\n")
    
    # Mapear redirecionamentos que devem permanecer na mesma página
    correcoes_redirecionamento = {
        'routes/receita.py': {
            'apos_salvar': 'receita.receita',
            'apos_erro': 'receita.receita',
            'template': 'receita.html'
        },
        'routes/exames.py': {
            'apos_salvar': 'exames.exames_lab',
            'apos_erro': 'exames.exames_lab', 
            'template': 'exames_lab.html'
        },
        'routes/agenda.py': {
            'apos_salvar': 'agenda.agenda',
            'apos_erro': 'agenda.agenda',
            'template': 'agenda.html'
        },
        'routes/relatorios.py': {
            'apos_salvar': 'relatorios.relatorio_medico',
            'apos_erro': 'relatorios.relatorio_medico',
            'template': 'relatorio_medico.html'
        }
    }
    
    correcoes_aplicadas = 0
    
    for arquivo, config in correcoes_redirecionamento.items():
        if os.path.exists(arquivo):
            print(f"Corrigindo {arquivo}...")
            
            try:
                # Backup
                backup_path = f"{arquivo}.redirect_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                with open(arquivo, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                content_original = content
                
                # Aplicar correções
                content = corrigir_success_redirects(content, config)
                content = corrigir_error_redirects(content, config)
                
                if content != content_original:
                    with open(arquivo, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✓ {arquivo} - Redirecionamentos corrigidos")
                    correcoes_aplicadas += 1
                else:
                    print(f"  - {arquivo} - Já estava correto")
                    os.remove(backup_path)
                    
            except Exception as e:
                print(f"  ❌ Erro em {arquivo}: {e}")
    
    print(f"\nArquivos corrigidos: {correcoes_aplicadas}")

def corrigir_success_redirects(content, config):
    """Corrige redirecionamentos após sucesso para permanecer na página"""
    
    # Padrões de sucesso que redirecionam
    patterns = [
        r'flash\([^)]+[\'"]success[\'"][^)]*\)\s*return\s+redirect\([^)]+\)',
        r'logging\.info\([^)]+\)\s*return\s+redirect\([^)]+\)',
        r'db\.session\.commit\(\)\s*[^r]*return\s+redirect\([^)]+\)'
    ]
    
    template = config.get('template', 'template.html')
    
    for pattern in patterns:
        # Encontrar matches
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in reversed(list(matches)):
            match_text = match.group(0)
            
            # Extrair a mensagem de flash se existir
            flash_match = re.search(r'flash\(([^)]+)\)', match_text)
            flash_line = flash_match.group(0) if flash_match else ''
            
            # Substituir redirect por render_template
            if 'redirect(' in match_text:
                # Manter flash e logging, mas substituir redirect
                new_text = match_text.replace(
                    re.search(r'return\s+redirect\([^)]+\)', match_text).group(0),
                    f"return render_template('{template}')"
                )
                
                content = content[:match.start()] + new_text + content[match.end():]
    
    return content

def corrigir_error_redirects(content, config):
    """Corrige redirecionamentos após erro para permanecer na página"""
    
    template = config.get('template', 'template.html')
    
    # Padrões de erro que redirecionam
    error_patterns = [
        r'flash\([^)]+[\'"]error[\'"][^)]*\)\s*return\s+redirect\([^)]+\)',
        r'except[^:]*:\s*[^r]*return\s+redirect\([^)]+\)'
    ]
    
    for pattern in error_patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in reversed(list(matches)):
            match_text = match.group(0)
            
            if 'redirect(' in match_text:
                new_text = match_text.replace(
                    re.search(r'return\s+redirect\([^)]+\)', match_text).group(0),
                    f"return render_template('{template}')"
                )
                
                content = content[:match.start()] + new_text + content[match.end():]
    
    return content

def verificar_redirecionamentos_existentes():
    """Verifica redirecionamentos atuais no sistema"""
    
    print("=== VERIFICAÇÃO DE REDIRECIONAMENTOS ATUAIS ===\n")
    
    arquivos_rota = [
        'routes/receita.py',
        'routes/exames.py', 
        'routes/agenda.py',
        'routes/relatorios.py',
        'routes/pacientes.py'
    ]
    
    problemas_encontrados = []
    
    for arquivo in arquivos_rota:
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"Analisando {arquivo}:")
            
            # Procurar por redirecionamentos após flash de sucesso
            success_redirects = re.findall(
                r'flash\([^)]+[\'"]success[\'"][^)]*\)\s*[^r]*return\s+redirect\([^)]+\)',
                content, re.MULTILINE | re.DOTALL
            )
            
            if success_redirects:
                print(f"  ⚠ Encontrados {len(success_redirects)} redirecionamentos após sucesso")
                problemas_encontrados.extend([(arquivo, 'success', r) for r in success_redirects])
            
            # Procurar por redirecionamentos após flash de erro
            error_redirects = re.findall(
                r'flash\([^)]+[\'"]error[\'"][^)]*\)\s*[^r]*return\s+redirect\([^)]+\)',
                content, re.MULTILINE | re.DOTALL
            )
            
            if error_redirects:
                print(f"  ⚠ Encontrados {len(error_redirects)} redirecionamentos após erro")
                problemas_encontrados.extend([(arquivo, 'error', r) for r in error_redirects])
            
            if not success_redirects and not error_redirects:
                print(f"  ✓ Sem problemas de redirecionamento")
            
            print()
    
    return problemas_encontrados

if __name__ == "__main__":
    problemas = verificar_redirecionamentos_existentes()
    
    if problemas:
        print(f"Encontrados {len(problemas)} redirecionamentos problemáticos")
        print("Iniciando correção...\n")
        corrigir_redirecionamentos()
    else:
        print("Nenhum problema de redirecionamento encontrado!")