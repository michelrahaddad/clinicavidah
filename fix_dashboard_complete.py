"""
Script para corrigir completamente o dashboard e restaurar funcionalidade total
"""
import re

def fix_dashboard_models():
    """Corrige todas as referências de modelos no dashboard"""
    
    with open('blueprints/dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir todas as referências ExamesLab -> ExameLab
    content = content.replace('ExamesLab', 'ExameLab')
    content = content.replace('ExamesImg', 'ExameImg')
    content = content.replace('Atestado', 'AtestadoMedico')
    
    # Corrigir queries problemáticas
    content = re.sub(
        r'Receita\.medico == user',
        'Receita.id_medico == medico.id',
        content
    )
    
    content = re.sub(
        r'ExameLab\.medico == user',
        'ExameLab.id_medico == medico.id',
        content
    )
    
    content = re.sub(
        r'ExameImg\.medico == user',
        'ExameImg.id_medico == medico.id',
        content
    )
    
    # Adicionar função sanitize_input se não existir
    if 'def sanitize_input(' not in content:
        sanitize_function = """
def sanitize_input(text):
    \"\"\"Sanitiza entrada do usuário\"\"\"
    if not text:
        return ""
    return str(text).strip()

"""
        # Inserir após os imports
        import_end = content.find('logger = logging.getLogger(__name__)')
        if import_end != -1:
            insert_pos = content.find('\n', import_end) + 1
            content = content[:insert_pos] + sanitize_function + content[insert_pos:]
    
    # Salvar arquivo corrigido
    with open('blueprints/dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Dashboard corrigido com sucesso!")

def fix_activities_function():
    """Corrige especificamente a função get_recent_activities"""
    
    with open('blueprints/dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar e corrigir a função get_recent_activities
    activities_pattern = r'def get_recent_activities\(user_type, user\):.*?return activities'
    
    new_activities_function = '''def get_recent_activities(user_type, user):
    """Busca atividades recentes do usuário"""
    activities = []
    
    try:
        if user_type == 'admin':
            # Atividades administrativas
            receitas = db.session.query(Receita).order_by(Receita.data_criacao.desc()).limit(5).all()
            for receita in receitas:
                activities.append({
                    'tipo': 'Receita',
                    'descricao': f'Receita para {receita.nome_paciente}',
                    'data': receita.data_criacao.strftime('%d/%m/%Y %H:%M') if receita.data_criacao else receita.data,
                    'medico': receita.medico_nome
                })
        else:
            # Atividades do médico
            user_name = user.get('nome') if isinstance(user, dict) else user
            medico = db.session.query(Medico).filter_by(nome=user_name).first()
            
            if medico:
                receitas = db.session.query(Receita).filter_by(id_medico=medico.id).order_by(Receita.data_criacao.desc()).limit(5).all()
                for receita in receitas:
                    activities.append({
                        'tipo': 'Receita',
                        'descricao': f'Receita para {receita.nome_paciente}',
                        'data': receita.data_criacao.strftime('%d/%m/%Y %H:%M') if receita.data_criacao else receita.data,
                        'medico': receita.medico_nome
                    })
                
                # Adicionar exames
                exames_lab = db.session.query(ExameLab).filter_by(id_medico=medico.id).order_by(ExameLab.created_at.desc()).limit(3).all()
                for exame in exames_lab:
                    activities.append({
                        'tipo': 'Exame Lab',
                        'descricao': f'Exames para {exame.nome_paciente}',
                        'data': exame.created_at.strftime('%d/%m/%Y %H:%M') if exame.created_at else exame.data,
                        'medico': exame.medico_nome
                    })
        
    except Exception as e:
        logger.error(f"Error getting activities: {str(e)}")
    
    return activities'''
    
    # Substituir a função
    content = re.sub(activities_pattern, new_activities_function, content, flags=re.DOTALL)
    
    # Salvar arquivo corrigido
    with open('blueprints/dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Função de atividades corrigida!")

def fix_chart_data_function():
    """Corrige a função get_chart_data"""
    
    with open('blueprints/dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar e corrigir a função get_chart_data
    chart_pattern = r'def get_chart_data\(user_type, user\):.*?return chart_data'
    
    new_chart_function = '''def get_chart_data(user_type, user):
    """Dados para gráficos do dashboard"""
    chart_data = {
        'labels': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        'receitas': [0, 0, 0, 0, 0, 0],
        'exames': [0, 0, 0, 0, 0, 0]
    }
    
    try:
        from datetime import datetime, timedelta
        now = datetime.now()
        
        if user_type == 'admin':
            # Dados administrativos dos últimos 6 meses
            for i in range(6):
                month_start = (now.replace(day=1) - timedelta(days=30*i))
                month_end = month_start + timedelta(days=30)
                
                receitas_count = db.session.query(func.count(Receita.id)).filter(
                    Receita.data_criacao >= month_start,
                    Receita.data_criacao < month_end
                ).scalar() or 0
                
                exames_count = (
                    db.session.query(func.count(ExameLab.id)).filter(
                        ExameLab.created_at >= month_start,
                        ExameLab.created_at < month_end
                    ).scalar() or 0
                ) + (
                    db.session.query(func.count(ExameImg.id)).filter(
                        ExameImg.created_at >= month_start,
                        ExameImg.created_at < month_end
                    ).scalar() or 0
                )
                
                chart_data['receitas'][5-i] = receitas_count
                chart_data['exames'][5-i] = exames_count
        else:
            # Dados do médico
            user_name = user.get('nome') if isinstance(user, dict) else user
            medico = db.session.query(Medico).filter_by(nome=user_name).first()
            
            if medico:
                for i in range(6):
                    month_start = (now.replace(day=1) - timedelta(days=30*i))
                    month_end = month_start + timedelta(days=30)
                    
                    receitas_count = db.session.query(func.count(Receita.id)).filter(
                        Receita.id_medico == medico.id,
                        Receita.data_criacao >= month_start,
                        Receita.data_criacao < month_end
                    ).scalar() or 0
                    
                    chart_data['receitas'][5-i] = receitas_count
        
    except Exception as e:
        logger.error(f"Error getting chart data: {str(e)}")
    
    return chart_data'''
    
    # Substituir a função
    content = re.sub(chart_pattern, new_chart_function, content, flags=re.DOTALL)
    
    # Salvar arquivo corrigido
    with open('blueprints/dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Função de gráficos corrigida!")

if __name__ == '__main__':
    fix_dashboard_models()
    fix_activities_function()
    fix_chart_data_function()
    print("Dashboard completamente restaurado!")