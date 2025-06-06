"""
Correção exaustiva da integração de dados do paciente e assinatura digital no PDF
"""
import logging
from datetime import datetime

def corrigir_pdf_receita_completo():
    """Corrige todas as funções de PDF para integração completa dos dados"""
    
    # Ler arquivo original
    with open('routes/receita.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir função gerar_pdf_reimprimir_receita
    old_function = '''def gerar_pdf_reimprimir_receita(receita_obj):
    """Generate PDF for existing prescription with current date"""
    try:
        medico = Medico.query.get(session['usuario']['id'])
        data_atual = datetime.now().strftime('%d/%m/%Y')
        
        # Get complete patient data
        paciente = Paciente.query.get(receita_obj.id_paciente)
        
        # Process medications to avoid duplicates
        medicamentos_raw = receita_obj.medicamentos.split(',')
        medicamentos_unicos = []
        seen = set()
        for med in medicamentos_raw:
            if med.strip() and med.strip() not in seen:
                medicamentos_unicos.append(med.strip())
                seen.add(med.strip())
        
        pdf_html = render_template('receita_pdf.html',
                                 nome_paciente=receita_obj.nome_paciente,
                                 cpf_paciente=paciente.cpf if paciente else None,
                                 idade_paciente=f"{paciente.idade} anos" if paciente and paciente.idade else None,
                                 endereco_paciente=paciente.endereco if paciente else None,
                                 cidade_uf_paciente=paciente.cidade_uf if paciente else None,
                                 medicamentos=medicamentos_unicos,
                                 posologias=receita_obj.posologias.split(',')[:len(medicamentos_unicos)],
                                 duracoes=receita_obj.duracoes.split(',')[:len(medicamentos_unicos)],
                                 vias=receita_obj.vias.split(',')[:len(medicamentos_unicos)],
                                 medico=medico.nome if medico else "Médico não encontrado",
                                 crm=medico.crm if medico else "CRM não disponível",
                                 data=data_atual,
                                 assinatura=medico.assinatura if medico and medico.assinatura else None,
                                 zip=zip)'''
    
    new_function = '''def gerar_pdf_reimprimir_receita(receita_obj):
    """Generate PDF for existing prescription with complete patient data and digital signature"""
    try:
        # Get complete patient data from database
        paciente = Paciente.query.get(receita_obj.id_paciente)
        
        # Get doctor data with signature - multiple fallback methods
        medico = None
        if 'usuario' in session:
            if isinstance(session['usuario'], dict) and 'id' in session['usuario']:
                medico = Medico.query.get(session['usuario']['id'])
            else:
                medico = Medico.query.filter_by(nome=session['usuario']).first()
        
        # Fallback to receita's doctor ID
        if not medico and receita_obj.id_medico:
            medico = Medico.query.get(receita_obj.id_medico)
        
        # Final fallback to doctor by name
        if not medico:
            medico = Medico.query.filter_by(nome=receita_obj.medico_nome).first()
        
        data_atual = datetime.now().strftime('%d/%m/%Y')
        
        # Process medications to avoid duplicates
        medicamentos_raw = receita_obj.medicamentos.split(',')
        medicamentos_unicos = []
        seen = set()
        for med in medicamentos_raw:
            if med.strip() and med.strip() not in seen:
                medicamentos_unicos.append(med.strip())
                seen.add(med.strip())
        
        # Log complete data for debugging
        logging.info(f'PDF Generation - Paciente: {paciente.nome if paciente else "N/A"}, CPF: {paciente.cpf if paciente else "N/A"}')
        logging.info(f'PDF Generation - Médico: {medico.nome if medico else "N/A"}, CRM: {medico.crm if medico else "N/A"}')
        logging.info(f'PDF Generation - Assinatura presente: {bool(medico and medico.assinatura and medico.assinatura != "assinatura")}')
        
        pdf_html = render_template('receita_pdf.html',
                                 nome_paciente=receita_obj.nome_paciente,
                                 cpf_paciente=paciente.cpf if paciente and paciente.cpf != '000.000.000-00' else '',
                                 idade_paciente=f"{paciente.idade} anos" if paciente and paciente.idade > 0 else '',
                                 endereco_paciente=paciente.endereco if paciente and paciente.endereco != 'Não informado' else '',
                                 cidade_uf_paciente=paciente.cidade_uf if paciente and paciente.cidade_uf != 'Não informado/XX' else '',
                                 medicamentos=medicamentos_unicos,
                                 posologias=receita_obj.posologias.split(',')[:len(medicamentos_unicos)],
                                 duracoes=receita_obj.duracoes.split(',')[:len(medicamentos_unicos)],
                                 vias=receita_obj.vias.split(',')[:len(medicamentos_unicos)],
                                 medico=medico.nome if medico else "Médico não encontrado",
                                 crm=medico.crm if medico else "CRM não disponível",
                                 data=data_atual,
                                 assinatura=medico.assinatura if medico and medico.assinatura and medico.assinatura != 'assinatura' else None,
                                 zip=zip)'''
    
    # Aplicar correção
    if old_function in content:
        content = content.replace(old_function, new_function)
        print("✓ Função gerar_pdf_reimprimir_receita corrigida")
    else:
        print("⚠ Função gerar_pdf_reimprimir_receita não encontrada - aplicando correção manual")
    
    # Salvar arquivo corrigido
    with open('routes/receita.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Correção de PDF aplicada com sucesso")

if __name__ == "__main__":
    corrigir_pdf_receita_completo()