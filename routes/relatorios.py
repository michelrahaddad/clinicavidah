from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, make_response
from models import Receita, ExameLab, ExameImg, Consulta, Paciente, Medico
from main import db
from datetime import datetime, timedelta
import logging
from io import BytesIO
import base64

def sanitizar_entrada(valor):
    """Sanitiza entrada de usuário"""
    if not valor:
        return ""
    import re
    valor = re.sub(r'[<>"\']', '', str(valor))
    return valor.strip()

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/relatorios')
def dashboard_relatorios():
    """Dashboard principal de relatórios"""
    try:
        # Verifica autenticação
        if not session.get('usuario') and not session.get('admin_usuario'):
            flash('Acesso negado. Faça login primeiro.', 'error')
            return redirect(url_for('auth.login'))
        
        # Dados para dashboard
        hoje = datetime.now().date()
        inicio_mes = hoje.replace(day=1)
        
        # Estatísticas gerais
        total_receitas = db.session.query(Receita).count()
        total_exames_lab = db.session.query(ExameLab).count()
        total_exames_img = db.session.query(ExameImg).count()
        total_consultas = db.session.query(Consulta).count()
        total_pacientes = db.session.query(Paciente).count()
        
        # Estatísticas do mês atual
        receitas_mes = db.session.query(Receita).filter(
            Receita.data >= inicio_mes
        ).count()
        
        exames_lab_mes = db.session.query(ExameLab).filter(
            ExameLab.data >= inicio_mes
        ).count()
        
        exames_img_mes = db.session.query(ExameImg).filter(
            ExameImg.data >= inicio_mes
        ).count()
        
        consultas_mes = db.session.query(Consulta).filter(
            Consulta.data_consulta >= inicio_mes
        ).count()
        
        # Dados para gráficos
        ultimos_7_dias = []
        for i in range(7):
            data = hoje - timedelta(days=i)
            receitas_dia = db.session.query(Receita).filter(
                Receita.data == data
            ).count()
            ultimos_7_dias.append({
                'data': data.strftime('%d/%m'),
                'receitas': receitas_dia
            })
        
        ultimos_7_dias.reverse()
        
        return render_template('relatorios/dashboard.html',
                             total_receitas=total_receitas,
                             total_exames_lab=total_exames_lab,
                             total_exames_img=total_exames_img,
                             total_consultas=total_consultas,
                             total_pacientes=total_pacientes,
                             receitas_mes=receitas_mes,
                             exames_lab_mes=exames_lab_mes,
                             exames_img_mes=exames_img_mes,
                             consultas_mes=consultas_mes,
                             ultimos_7_dias=ultimos_7_dias)
        
    except Exception as e:
        logging.error(f"Erro no dashboard de relatórios: {e}")
        flash('Erro ao carregar relatórios', 'error')
        return redirect(url_for('dashboard'))

@relatorios_bp.route('/relatorios/detalhado')
def relatorio_detalhado():
    """Relatório detalhado com filtros"""
    try:
        # Obtém filtros
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        tipo_relatorio = request.args.get('tipo', 'receitas')
        medico_id = request.args.get('medico_id', '')
        
        # Query base
        if tipo_relatorio == 'receitas':
            query = db.session.query(Receita).join(Paciente).join(Medico)
        elif tipo_relatorio == 'exames_lab':
            query = db.session.query(ExameLab).join(Paciente).join(Medico)
        elif tipo_relatorio == 'exames_img':
            query = db.session.query(ExameImg).join(Paciente).join(Medico)
        elif tipo_relatorio == 'consultas':
            query = db.session.query(Consulta).join(Paciente).join(Medico)
        else:
            query = db.session.query(Receita).join(Paciente).join(Medico)
        
        # Aplica filtros de data
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                if tipo_relatorio == 'consultas':
                    query = query.filter(Consulta.data_consulta >= data_inicio_obj)
                else:
                    query = query.filter(getattr(query.column_descriptions[0]['type'], 'data') >= data_inicio_obj)
            except:
                pass
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                if tipo_relatorio == 'consultas':
                    query = query.filter(Consulta.data_consulta <= data_fim_obj)
                else:
                    query = query.filter(getattr(query.column_descriptions[0]['type'], 'data') <= data_fim_obj)
            except:
                pass
        
        # Aplica filtro de médico
        if medico_id:
            query = query.filter(Medico.id == medico_id)
        
        # Executa query
        resultados = query.order_by(
            getattr(query.column_descriptions[0]['type'], 'data', 
                   getattr(query.column_descriptions[0]['type'], 'data_consulta', 
                          getattr(query.column_descriptions[0]['type'], 'created_at'))).desc()
        ).all()
        
        # Busca médicos para filtro
        medicos = db.session.query(Medico).all()
        
        return render_template('relatorios/detalhado.html',
                             resultados=resultados,
                             medicos=medicos,
                             tipo_relatorio=tipo_relatorio,
                             data_inicio=data_inicio,
                             data_fim=data_fim,
                             medico_id=medico_id)
        
    except Exception as e:
        logging.error(f"Erro no relatório detalhado: {e}")
        flash('Erro ao gerar relatório detalhado', 'error')
        return redirect(url_for('relatorios.dashboard_relatorios'))

@relatorios_bp.route('/relatorios/exportar')
def exportar_relatorio():
    """Exporta relatório em formato PDF/Excel"""
    try:
        # Implementação para exportação
        # Por enquanto retorna JSON com dados
        
        tipo = request.args.get('tipo', 'receitas')
        formato = request.args.get('formato', 'json')
        
        if tipo == 'receitas':
            dados = db.session.query(Receita).join(Paciente).join(Medico).all()
            dados_export = []
            for receita in dados:
                dados_export.append({
                    'data': receita.data.strftime('%d/%m/%Y') if receita.data else '',
                    'paciente': receita.paciente.nome,
                    'medico': receita.medico.nome,
                    'medicamentos': len(receita.medicamentos.split('\n')) if receita.medicamentos else 0
                })
        
        if formato == 'json':
            response = make_response(jsonify(dados_export))
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename=relatorio_{tipo}_{datetime.now().strftime("%Y%m%d")}.json'
            return response
        
        return jsonify({'success': True, 'dados': dados_export})
        
    except Exception as e:
        logging.error(f"Erro ao exportar relatório: {e}")
        return jsonify({'success': False, 'error': str(e)})

@relatorios_bp.route('/relatorios/estatisticas')
def estatisticas_avancadas():
    """Estatísticas avançadas do sistema"""
    try:
        # Estatísticas por período
        hoje = datetime.now().date()
        ultimo_mes = hoje - timedelta(days=30)
        ultimo_ano = hoje - timedelta(days=365)
        
        # Crescimento mensal
        receitas_ultimo_mes = db.session.query(Receita).filter(
            Receita.data >= ultimo_mes
        ).count()
        
        receitas_mes_anterior = db.session.query(Receita).filter(
            Receita.data >= (ultimo_mes - timedelta(days=30)),
            Receita.data < ultimo_mes
        ).count()
        
        crescimento_receitas = 0
        if receitas_mes_anterior > 0:
            crescimento_receitas = ((receitas_ultimo_mes - receitas_mes_anterior) / receitas_mes_anterior) * 100
        
        # Top medicamentos mais prescritos
        # Implementação simplificada - seria necessário parser dos medicamentos
        
        # Top médicos mais ativos
        medicos_ativos = db.session.query(
            Medico.nome,
            db.func.count(Receita.id).label('total_receitas')
        ).join(Receita).group_by(Medico.id, Medico.nome).order_by(
            db.func.count(Receita.id).desc()
        ).limit(10).all()
        
        return render_template('relatorios/estatisticas.html',
                             crescimento_receitas=crescimento_receitas,
                             medicos_ativos=medicos_ativos,
                             receitas_ultimo_mes=receitas_ultimo_mes)
        
    except Exception as e:
        logging.error(f"Erro nas estatísticas: {e}")
        flash('Erro ao carregar estatísticas', 'error')
        return redirect(url_for('relatorios.dashboard_relatorios'))