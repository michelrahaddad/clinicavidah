from flask import Blueprint, render_template, make_response, session, redirect, url_for, request
from utils.db import get_dashboard_stats, get_monthly_evolution
from datetime import datetime
import logging

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/relatorio/estatisticas/pdf')
def relatorio_estatisticas_pdf():
    """Generate PDF report of evolution statistics"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        medico_id = session['usuario']['id']
        medico_nome = session['usuario']['nome']
        
        # Get comprehensive statistics
        stats = get_dashboard_stats(medico_id)
        
        # Get period from query params
        periodo = request.args.get('periodo', '12')  # Default 12 months
        
        # Generate report data
        report_data = {
            'medico_nome': medico_nome,
            'data_geracao': datetime.now().strftime('%d/%m/%Y às %H:%M'),
            'periodo_analise': f'Últimos {periodo} meses',
            'stats': stats,
            'resumo_executivo': generate_executive_summary(stats)
        }
        
        # Render PDF template
        html = render_template('relatorio_estatisticas_pdf.html', **report_data)
        
        # Generate PDF using WeasyPrint
        try:
            import weasyprint
            pdf = weasyprint.HTML(string=html).write_pdf()
            
            response = make_response(pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=relatorio_estatisticas_{medico_nome.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.pdf'
            
            logging.info(f'Statistics report generated for doctor: {medico_nome}')
            return response
            
        except Exception as pdf_error:
            logging.error(f'PDF generation error: {pdf_error}')
            return render_template('relatorio_estatisticas_pdf.html', **report_data)
            
    except Exception as e:
        logging.error(f'Statistics report error: {e}')
        return redirect(url_for('dashboard.dashboard'))

def generate_executive_summary(stats):
    """Generate executive summary from statistics"""
    try:
        monthly_data = stats.get('monthly_evolution', {})
        
        if not monthly_data.get('receitas'):
            return {
                'total_documentos': 0,
                'media_mensal': 0,
                'tendencia': 'Sem dados suficientes',
                'mes_mais_produtivo': 'N/A',
                'crescimento': 0
            }
        
        # Calculate totals
        total_receitas = sum(monthly_data['receitas'])
        total_exames_lab = sum(monthly_data['exames_lab'])
        total_exames_img = sum(monthly_data['exames_img'])
        total_documentos = total_receitas + total_exames_lab + total_exames_img
        
        # Calculate monthly average
        months_count = len([x for x in monthly_data['receitas'] if x > 0])
        media_mensal = total_documentos / max(months_count, 1)
        
        # Determine trend
        recent_months = monthly_data['receitas'][-3:]  # Last 3 months
        older_months = monthly_data['receitas'][-6:-3]  # Previous 3 months
        
        recent_avg = sum(recent_months) / 3 if recent_months else 0
        older_avg = sum(older_months) / 3 if older_months else 0
        
        if recent_avg > older_avg * 1.1:
            tendencia = 'Crescimento'
            crescimento = ((recent_avg - older_avg) / max(older_avg, 1)) * 100
        elif recent_avg < older_avg * 0.9:
            tendencia = 'Declínio'
            crescimento = ((recent_avg - older_avg) / max(older_avg, 1)) * 100
        else:
            tendencia = 'Estável'
            crescimento = 0
        
        # Find most productive month
        max_value = 0
        mes_mais_produtivo = 'N/A'
        for i, month in enumerate(monthly_data['months']):
            month_total = (monthly_data['receitas'][i] + 
                          monthly_data['exames_lab'][i] + 
                          monthly_data['exames_img'][i])
            if month_total > max_value:
                max_value = month_total
                mes_mais_produtivo = month
        
        return {
            'total_documentos': total_documentos,
            'media_mensal': round(media_mensal, 1),
            'tendencia': tendencia,
            'mes_mais_produtivo': mes_mais_produtivo,
            'crescimento': round(crescimento, 1)
        }
        
    except Exception as e:
        logging.error(f'Executive summary error: {e}')
        return {
            'total_documentos': 0,
            'media_mensal': 0,
            'tendencia': 'Erro no cálculo',
            'mes_mais_produtivo': 'N/A',
            'crescimento': 0
        }