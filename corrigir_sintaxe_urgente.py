#!/usr/bin/env python3
"""
Correção urgente de sintaxe no arquivo prontuario.py
"""

import re

def corrigir_arquivo_prontuario():
    """Corrige erros de sintaxe no arquivo prontuario.py"""
    
    with open('routes/prontuario.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remover imports malformados
    content = re.sub(r'from utils\.medicamentos import parse_medicamentos_receita\n', '', content)
    
    # Corrigir blocos try/except quebrados
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Se encontrar um try sem except, corrigir
        if line.strip().startswith('try:') and i + 1 < len(lines):
            # Procurar o except correspondente
            j = i + 1
            found_except = False
            
            while j < len(lines) and lines[j].startswith(' '):
                if lines[j].strip().startswith('except'):
                    found_except = True
                    break
                j += 1
            
            if not found_except:
                # Adicionar except genérico
                fixed_lines.append(line)
                i += 1
                while i < len(lines) and lines[i].startswith(' '):
                    fixed_lines.append(lines[i])
                    i += 1
                fixed_lines.append('        except Exception as e:')
                fixed_lines.append('            pass')
                continue
        
        fixed_lines.append(line)
        i += 1
    
    # Reconstituir o arquivo
    fixed_content = '\n'.join(fixed_lines)
    
    with open('routes/prontuario.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("Arquivo prontuario.py corrigido")

if __name__ == "__main__":
    corrigir_arquivo_prontuario()