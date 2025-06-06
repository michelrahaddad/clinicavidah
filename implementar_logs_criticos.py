"""
Implementação de logs detalhados em pontos críticos do sistema
Para diagnosticar problemas de dados NaN no dashboard
"""
import logging

def adicionar_logs_dashboard():
    """Adiciona logs detalhados no dashboard para diagnóstico"""
    
    with open('blueprints/dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Adicionar configuração de logging mais detalhada
    logging_config = '''
import logging
import traceback

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)
'''
    
    # Substituir a configuração de logging existente
    if 'logger = logging.getLogger(__name__)' in content:
        content = content.replace(
            'logger = logging.getLogger(__name__)',
            logging_config
        )
    
    # Adicionar logs detalhados na função get_dashboard_statistics
    old_stats_function = '''def get_dashboard_statistics(user_type, user):
    """Calcula estatísticas para o dashboard"""
    stats = {}
    
    try:'''
    
    new_stats_function = '''def get_dashboard_statistics(user_type, user):
    """Calcula estatísticas para o dashboard"""
    stats = {}
    
    logger.info(f"=== INICIANDO CÁLCULO DE ESTATÍSTICAS ===")
    logger.info(f"User type: {user_type}")
    logger.info(f"User data: {user}")
    logger.info(f"User type is dict: {isinstance(user, dict)}")
    
    try:'''
    
    content = content.replace(old_stats_function, new_stats_function)
    
    # Adicionar logs nas consultas SQL específicas
    sql_patterns = [
        ('db.session.query(func.count(Receita.id))', 'logger.debug("Executando query: contagem de receitas")'),
        ('db.session.query(func.count(ExameLab.id))', 'logger.debug("Executando query: contagem de exames lab")'),
        ('db.session.query(func.count(ExameImg.id))', 'logger.debug("Executando query: contagem de exames img")'),
        ('db.session.query(func.count(Paciente.id))', 'logger.debug("Executando query: contagem de pacientes")'),
        ('db.session.query(func.count(Medico.id))', 'logger.debug("Executando query: contagem de médicos")')
    ]
    
    for pattern, log_line in sql_patterns:
        if pattern in content:
            content = content.replace(
                pattern,
                f'{log_line}\n        result = {pattern}'
            )
            content = content.replace(
                f'result = {pattern}.scalar() or 0',
                f'{pattern}.scalar() or 0\n        logger.debug(f"Resultado da query: {{result}}")'
            )
    
    # Adicionar log de erro mais detalhado
    old_except = '''except Exception as e:
        logger.error(f"Error calculating stats: {str(e)}")'''
    
    new_except = '''except Exception as e:
        logger.error(f"=== ERRO CRÍTICO NO CÁLCULO DE ESTATÍSTICAS ===")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        logger.error(f"Mensagem: {str(e)}")
        logger.error(f"Traceback completo:")
        logger.error(traceback.format_exc())
        logger.error(f"User type: {user_type}")
        logger.error(f"User data: {user}")'''
    
    content = content.replace(old_except, new_except)
    
    # Salvar arquivo com logs
    with open('blueprints/dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Logs detalhados adicionados ao dashboard!")

def adicionar_logs_app_principal():
    """Adiciona logs no app principal"""
    
    with open('app_modular_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Configurar logging no app principal
    if 'logging.basicConfig' not in content:
        import_section = '''import logging
from datetime import timedelta
from sqlalchemy import func

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)

'''
        # Adicionar no início após os imports existentes
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from flask import'):
                lines.insert(i, import_section)
                break
        content = '\n'.join(lines)
    
    # Adicionar logs na função de dashboard
    if 'def dashboard():' in content:
        old_dashboard = '''@app.route('/dashboard')
    def dashboard():
        """Dashboard principal do sistema"""
        return redirect('/dashboard/')'''
        
        new_dashboard = '''@app.route('/dashboard')
    def dashboard():
        """Dashboard principal do sistema"""
        logger = logging.getLogger(__name__)
        logger.info("Redirecionando para /dashboard/")
        return redirect('/dashboard/')'''
        
        content = content.replace(old_dashboard, new_dashboard)
    
    with open('app_modular_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Logs adicionados ao app principal!")

def adicionar_logs_auth():
    """Adiciona logs no sistema de autenticação"""
    
    with open('auth_simple.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Adicionar logs na função de login
    if 'def login():' in content:
        # Encontrar e adicionar logs detalhados
        login_patterns = [
            ('medico = db.session.query(Medico)', 'logger.info(f"Buscando médico no banco: {nome}, {crm}")'),
            ('if medico and check_password_hash', 'logger.info(f"Médico encontrado: {medico.nome if medico else None}")'),
            ('session[\'usuario\'] = {', 'logger.info("Login bem-sucedido, criando sessão")')
        ]
        
        for pattern, log_line in login_patterns:
            if pattern in content:
                content = content.replace(
                    pattern,
                    f'{log_line}\n        {pattern}'
                )
    
    with open('auth_simple.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Logs adicionados ao sistema de autenticação!")

def criar_script_diagnostico():
    """Cria script para diagnóstico completo do banco"""
    
    script_content = '''"""
Script de diagnóstico completo do banco de dados
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import db
from models import Medico, Paciente, Receita, ExameLab, ExameImg, AtestadoMedico
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnosticar_banco():
    """Diagnóstica completamente o estado do banco"""
    
    try:
        logger.info("=== DIAGNÓSTICO COMPLETO DO BANCO DE DADOS ===")
        
        # Verificar conexão
        logger.info("1. Testando conexão com banco...")
        result = db.session.execute("SELECT 1").scalar()
        logger.info(f"Conexão OK: {result}")
        
        # Verificar tabelas
        logger.info("2. Verificando estrutura das tabelas...")
        tables = ['medicos', 'pacientes', 'receitas', 'exames_lab', 'exames_img', 'atestados_medicos']
        
        for table in tables:
            try:
                count = db.session.execute(f"SELECT COUNT(*) FROM {table}").scalar()
                logger.info(f"Tabela {table}: {count} registros")
            except Exception as e:
                logger.error(f"Erro na tabela {table}: {e}")
        
        # Verificar dados específicos do Dr. Michel
        logger.info("3. Verificando dados do Dr. Michel...")
        michel = db.session.query(Medico).filter_by(crm='183299-SP').first()
        if michel:
            logger.info(f"Dr. Michel encontrado: ID={michel.id}, Nome={michel.nome}")
            
            # Contar documentos do Dr. Michel
            receitas_count = db.session.query(Receita).filter_by(id_medico=michel.id).count()
            exames_lab_count = db.session.query(ExameLab).filter_by(id_medico=michel.id).count()
            exames_img_count = db.session.query(ExameImg).filter_by(id_medico=michel.id).count()
            
            logger.info(f"Receitas do Dr. Michel: {receitas_count}")
            logger.info(f"Exames Lab do Dr. Michel: {exames_lab_count}")
            logger.info(f"Exames Img do Dr. Michel: {exames_img_count}")
        else:
            logger.error("Dr. Michel NÃO encontrado no banco!")
        
        # Verificar colunas específicas
        logger.info("4. Verificando colunas críticas...")
        try:
            receita_sample = db.session.query(Receita).first()
            if receita_sample:
                logger.info(f"Receita sample - data_criacao: {getattr(receita_sample, 'data_criacao', 'CAMPO NÃO EXISTE')}")
                logger.info(f"Receita sample - id_medico: {receita_sample.id_medico}")
                logger.info(f"Receita sample - nome_paciente: {receita_sample.nome_paciente}")
        except Exception as e:
            logger.error(f"Erro ao verificar receita: {e}")
        
        # Testar queries específicas do dashboard
        logger.info("5. Testando queries do dashboard...")
        try:
            from sqlalchemy import func
            total_receitas = db.session.query(func.count(Receita.id)).scalar()
            logger.info(f"Total receitas (query dashboard): {total_receitas}")
            
            total_pacientes = db.session.query(func.count(Paciente.id)).scalar()
            logger.info(f"Total pacientes (query dashboard): {total_pacientes}")
            
        except Exception as e:
            logger.error(f"Erro nas queries do dashboard: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        logger.info("=== DIAGNÓSTICO CONCLUÍDO ===")
        
    except Exception as e:
        logger.error(f"ERRO CRÍTICO no diagnóstico: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    from app_modular_fixed import app
    with app.app_context():
        diagnosticar_banco()
'''
    
    with open('diagnostico_banco.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("Script de diagnóstico criado!")

def executar_implementacao_logs():
    """Executa toda a implementação de logs"""
    print("=== IMPLEMENTANDO LOGS CRÍTICOS ===")
    
    adicionar_logs_dashboard()
    adicionar_logs_app_principal()
    adicionar_logs_auth()
    criar_script_diagnostico()
    
    print("\n=== LOGS IMPLEMENTADOS COM SUCESSO ===")
    print("✓ Logs detalhados no dashboard")
    print("✓ Logs no app principal")
    print("✓ Logs no sistema de autenticação")
    print("✓ Script de diagnóstico criado")

if __name__ == '__main__':
    executar_implementacao_logs()