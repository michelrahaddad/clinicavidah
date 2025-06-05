from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from models import Receita, ExameLab, ExameImg, Consulta, Paciente, Medico
from main import db
from datetime import datetime, timedelta
import logging
from sqlalchemy import func, extract

def sanitizar_entrada(valor):
    """Sanitiza entrada de usuário"""
    if not valor:
        return ""
    import re
    valor = re.sub(r'[<>"\']', '', str(valor))
    return valor.strip()

estatisticas_bp = Blueprint('estatisticas', __name__)

@estatisticas_bp.route('/estatisticas')
def dashboard_estatisticas():
    """Dashboard principal de estatísticas"""
    try:
        # Verifica autenticação
        if not session.get('usuario') and not session.get('admin_usuario'):
            flash('Acesso negado. Faça login primeiro.', 'error')
            return redirect(url_for('auth.login'))
        
        hoje = datetime.now().date()
        inicio_ano = hoje.replace(month=1, day=1)
        inicio_mes = hoje.replace(day=1)
        
        # Estatísticas gerais
        total_receitas = db.session.query(Receita).count()
        total_exames_lab = db.session.query(ExameLab).count()
        total_exames_img = db.session.query(ExameImg).count()
        total_consultas = db.session.query(Consulta).count()
        total_pacientes = db.session.query(Paciente).count()
        total_medicos = db.session.query(Medico).count()
        
        # Estatísticas por período
        receitas_ano = db.session.query(Receita).filter(Receita.data >= inicio_ano).count()
        receitas_mes = db.session.query(Receita).filter(Receita.data >= inicio_mes).count()
        receitas_hoje = db.session.query(Receita).filter(Receita.data == hoje).count()
        
        exames_lab_ano = db.session.query(ExameLab).filter(ExameLab.data >= inicio_ano).count()
        exames_lab_mes = db.session.query(ExameLab).filter(ExameLab.data >= inicio_mes).count()
        
        exames_img_ano = db.session.query(ExameImg).filter(ExameImg.data >= inicio_ano).count()
        exames_img_mes = db.session.query(ExameImg).filter(ExameImg.data >= inicio_mes).count()
        
        # Crescimento mensal (últimos 12 meses)
        crescimento_mensal = []
        for i in range(12):
            mes_atual = hoje.replace(day=1) - timedelta(days=30*i)
            mes_anterior = mes_atual - timedelta(days=30)
            
            receitas_mes_calc = db.session.query(Receita).filter(
                Receita.data >= mes_anterior,
                Receita.data < mes_atual
            ).count()
            
            crescimento_mensal.append({
                'mes': mes_atual.strftime('%m/%Y'),
                'receitas': receitas_mes_calc
            })
        
        crescimento_mensal.reverse()
        
        # Top 5 médicos mais ativos
        medicos_ativos = db.session.query(
            Medico.nome,
            func.count(Receita.id).label('total_receitas')
        ).join(Receita).group_by(Medico.id, Medico.nome).order_by(
            func.count(Receita.id).desc()
        ).limit(5).all()
        
        # Distribuição por dia da semana
        distribuicao_semanal = []
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        for i in range(7):
            receitas_dia = db.session.query(Receita).filter(
                extract('dow', Receita.data) == i
            ).count()
            distribuicao_semanal.append({
                'dia': dias_semana[i],
                'receitas': receitas_dia
            })
        
        # Médias
        media_receitas_dia = receitas_ano / 365 if receitas_ano > 0 else 0
        media_receitas_mes = receitas_ano / 12 if receitas_ano > 0 else 0
        
        return render_template('estatisticas/dashboard.html',
                             total_receitas=total_receitas,
                             total_exames_lab=total_exames_lab,
                             total_exames_img=total_exames_img,
                             total_consultas=total_consultas,
                             total_pacientes=total_pacientes,
                             total_medicos=total_medicos,
                             receitas_ano=receitas_ano,
                             receitas_mes=receitas_mes,
                             receitas_hoje=receitas_hoje,
                             exames_lab_ano=exames_lab_ano,
                             exames_lab_mes=exames_lab_mes,
                             exames_img_ano=exames_img_ano,
                             exames_img_mes=exames_img_mes,
                             crescimento_mensal=crescimento_mensal,
                             medicos_ativos=medicos_ativos,
                             distribuicao_semanal=distribuicao_semanal,
                             media_receitas_dia=round(media_receitas_dia, 1),
                             media_receitas_mes=round(media_receitas_mes, 1))
        
    except Exception as e:
        logging.error(f"Erro no dashboard de estatísticas: {e}")
        flash('Erro ao carregar estatísticas', 'error')
        return redirect(url_for('dashboard'))

@estatisticas_bp.route('/estatisticas/comparativo')
def comparativo_periodos():
    """Comparativo entre períodos"""
    try:
        periodo1 = request.args.get('periodo1', 'mes_atual')
        periodo2 = request.args.get('periodo2', 'mes_anterior')
        
        hoje = datetime.now().date()
        
        # Define períodos
        if periodo1 == 'mes_atual':
            inicio_p1 = hoje.replace(day=1)
            fim_p1 = hoje
        elif periodo1 == 'mes_anterior':
            primeiro_dia_mes_anterior = (hoje.replace(day=1) - timedelta(days=1)).replace(day=1)
            inicio_p1 = primeiro_dia_mes_anterior
            fim_p1 = hoje.replace(day=1) - timedelta(days=1)
        elif periodo1 == 'ano_atual':
            inicio_p1 = hoje.replace(month=1, day=1)
            fim_p1 = hoje
        
        if periodo2 == 'mes_anterior':
            primeiro_dia_mes_anterior = (hoje.replace(day=1) - timedelta(days=1)).replace(day=1)
            inicio_p2 = primeiro_dia_mes_anterior
            fim_p2 = hoje.replace(day=1) - timedelta(days=1)
        elif periodo2 == 'ano_anterior':
            inicio_p2 = hoje.replace(year=hoje.year-1, month=1, day=1)
            fim_p2 = hoje.replace(year=hoje.year-1, month=12, day=31)
        
        # Calcula estatísticas para cada período
        def calcular_estatisticas_periodo(inicio, fim):
            receitas = db.session.query(Receita).filter(
                Receita.data >= inicio,
                Receita.data <= fim
            ).count()
            
            exames_lab = db.session.query(ExameLab).filter(
                ExameLab.data >= inicio,
                ExameLab.data <= fim
            ).count()
            
            exames_img = db.session.query(ExameImg).filter(
                ExameImg.data >= inicio,
                ExameImg.data <= fim
            ).count()
            
            return {
                'receitas': receitas,
                'exames_lab': exames_lab,
                'exames_img': exames_img,
                'total': receitas + exames_lab + exames_img
            }
        
        stats_p1 = calcular_estatisticas_periodo(inicio_p1, fim_p1)
        stats_p2 = calcular_estatisticas_periodo(inicio_p2, fim_p2)
        
        # Calcula variações percentuais
        def calcular_variacao(valor1, valor2):
            if valor2 == 0:
                return 100 if valor1 > 0 else 0
            return ((valor1 - valor2) / valor2) * 100
        
        variacoes = {
            'receitas': calcular_variacao(stats_p1['receitas'], stats_p2['receitas']),
            'exames_lab': calcular_variacao(stats_p1['exames_lab'], stats_p2['exames_lab']),
            'exames_img': calcular_variacao(stats_p1['exames_img'], stats_p2['exames_img']),
            'total': calcular_variacao(stats_p1['total'], stats_p2['total'])
        }
        
        return render_template('estatisticas/comparativo.html',
                             periodo1=periodo1,
                             periodo2=periodo2,
                             stats_p1=stats_p1,
                             stats_p2=stats_p2,
                             variacoes=variacoes)
        
    except Exception as e:
        logging.error(f"Erro no comparativo: {e}")
        flash('Erro ao gerar comparativo', 'error')
        return redirect(url_for('estatisticas.dashboard_estatisticas'))

@estatisticas_bp.route('/estatisticas/performance')
def performance_medicos():
    """Análise de performance dos médicos"""
    try:
        periodo = request.args.get('periodo', 'mes')
        medico_id = request.args.get('medico_id', '')
        
        hoje = datetime.now().date()
        
        if periodo == 'mes':
            inicio = hoje.replace(day=1)
        elif periodo == 'trimestre':
            inicio = hoje - timedelta(days=90)
        elif periodo == 'ano':
            inicio = hoje.replace(month=1, day=1)
        else:
            inicio = hoje - timedelta(days=30)
        
        # Query base
        query = db.session.query(
            Medico.id,
            Medico.nome,
            Medico.crm,
            func.count(Receita.id).label('total_receitas'),
            func.count(ExameLab.id).label('total_exames_lab'),
            func.count(ExameImg.id).label('total_exames_img')
        ).outerjoin(Receita, Receita.medico_id == Medico.id)\
         .outerjoin(ExameLab, ExameLab.medico_id == Medico.id)\
         .outerjoin(ExameImg, ExameImg.medico_id == Medico.id)
        
        # Aplica filtro de período
        query = query.filter(
            db.or_(
                Receita.data >= inicio,
                ExameLab.data >= inicio,
                ExameImg.data >= inicio
            )
        )
        
        # Aplica filtro de médico específico se selecionado
        if medico_id:
            query = query.filter(Medico.id == medico_id)
        
        # Agrupa e ordena
        performance = query.group_by(Medico.id, Medico.nome, Medico.crm)\
                          .order_by(func.count(Receita.id).desc()).all()
        
        # Busca todos os médicos para filtro
        medicos = db.session.query(Medico).all()
        
        return render_template('estatisticas/performance.html',
                             performance=performance,
                             medicos=medicos,
                             periodo=periodo,
                             medico_id=medico_id)
        
    except Exception as e:
        logging.error(f"Erro na análise de performance: {e}")
        flash('Erro ao analisar performance', 'error')
        return redirect(url_for('estatisticas.dashboard_estatisticas'))

@estatisticas_bp.route('/api/estatisticas/grafico')
def api_dados_grafico():
    """API para dados de gráficos"""
    try:
        tipo = request.args.get('tipo', 'receitas_mensal')
        
        if tipo == 'receitas_mensal':
            # Últimos 12 meses
            dados = []
            hoje = datetime.now().date()
            
            for i in range(12):
                mes = hoje.replace(day=1) - timedelta(days=30*i)
                mes_seguinte = mes + timedelta(days=32)
                mes_seguinte = mes_seguinte.replace(day=1)
                
                total = db.session.query(Receita).filter(
                    Receita.data >= mes,
                    Receita.data < mes_seguinte
                ).count()
                
                dados.append({
                    'mes': mes.strftime('%m/%Y'),
                    'total': total
                })
            
            dados.reverse()
            return jsonify({'dados': dados})
        
        elif tipo == 'distribuicao_tipos':
            receitas = db.session.query(Receita).count()
            exames_lab = db.session.query(ExameLab).count()
            exames_img = db.session.query(ExameImg).count()
            consultas = db.session.query(Consulta).count()
            
            return jsonify({
                'dados': [
                    {'tipo': 'Receitas', 'total': receitas},
                    {'tipo': 'Exames Lab', 'total': exames_lab},
                    {'tipo': 'Exames Img', 'total': exames_img},
                    {'tipo': 'Consultas', 'total': consultas}
                ]
            })
        
        return jsonify({'dados': []})
        
    except Exception as e:
        logging.error(f"Erro na API de gráficos: {e}")
        return jsonify({'erro': str(e)})