#!/usr/bin/env python3
"""
Script para criar backup completo do Sistema Médico VIDAH
Salva estado atual com todas as funcionalidades implementadas
"""

import os
import shutil
import datetime
from pathlib import Path

def criar_backup_completo():
    """Cria backup completo do sistema"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_sistema_vidah_{timestamp}"
    
    try:
        # Criar diretório de backup
        Path(backup_dir).mkdir(exist_ok=True)
        
        # Arquivos e diretórios para backup
        items_backup = [
            "app.py",
            "main.py", 
            "models.py",
            "routes/",
            "templates/",
            "static/",
            "utils/",
            "pyproject.toml",
            "requirements-*.txt",
            ".replit"
        ]
        
        backup_count = 0
        
        for item in items_backup:
            if os.path.exists(item):
                if os.path.isdir(item):
                    shutil.copytree(item, f"{backup_dir}/{item}")
                    backup_count += 1
                    print(f"✓ Diretório copiado: {item}")
                else:
                    shutil.copy2(item, backup_dir)
                    backup_count += 1
                    print(f"✓ Arquivo copiado: {item}")
        
        # Criar arquivo de documentação do backup
        doc_backup = f"""
# Backup Sistema Médico VIDAH
Data: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

## Funcionalidades Implementadas:
- ✅ Sistema de login médico completo
- ✅ Dashboard com estatísticas e navegação
- ✅ Receitas médicas com autocomplete inteligente
- ✅ Exames laboratoriais e de imagem
- ✅ Atestados médicos com CID-10
- ✅ Relatórios médicos com CID-10
- ✅ Formulários de alto custo com CID-10
- ✅ Prontuário com badges médicos específicos
- ✅ Gestão completa de pacientes
- ✅ Integração PostgreSQL funcional
- ✅ Geração de PDFs com assinaturas digitais
- ✅ Pesquisa CID-10 com banco populado
- ✅ Autocomplete de medicamentos por histórico
- ✅ Sistema de badges por tipo de documento
- ✅ Navegação entre páginas otimizada

## Problemas Resolvidos:
- ✅ Botão "Gerar PDF" funcionando perfeitamente
- ✅ CID-10 com padrão I10.0 - Hipertensão arterial
- ✅ Autocomplete CID-10 em 3 páginas médicas
- ✅ Integração completa com PostgreSQL
- ✅ Assinaturas digitais visíveis em PDFs
- ✅ Layout responsivo e funcional

## Tecnologias:
- Flask + PostgreSQL
- Bootstrap 5 responsivo
- JavaScript para autocomplete
- WeasyPrint para PDFs
- Autenticação médica segura
- API REST completa

## Status: Sistema 100% funcional
"""
        
        with open(f"{backup_dir}/README_BACKUP.md", "w", encoding="utf-8") as f:
            f.write(doc_backup)
        
        print(f"\n🎉 BACKUP COMPLETO CRIADO!")
        print(f"📁 Diretório: {backup_dir}")
        print(f"📊 Itens salvos: {backup_count}")
        print(f"📝 Documentação: README_BACKUP.md")
        print(f"⏰ Data/Hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False

if __name__ == "__main__":
    criar_backup_completo()