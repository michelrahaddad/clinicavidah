
from app import app, db
from models import *

with app.app_context():
    # Verificar dados do Michel em todas as tabelas
    paciente_nome = "Michel"
    
    receitas = db.session.query(Receita).filter(Receita.nome_paciente.ilike(f'%{paciente_nome}%')).count()
    exames_lab = db.session.query(ExameLab).filter(ExameLab.nome_paciente.ilike(f'%{paciente_nome}%')).count()
    exames_img = db.session.query(ExameImagem).filter(ExameImagem.nome_paciente.ilike(f'%{paciente_nome}%')).count()
    relatorios = db.session.query(RelatorioMedico).filter(RelatorioMedico.nome_paciente.ilike(f'%{paciente_nome}%')).count()
    atestados = db.session.query(AtestadoMedico).filter(AtestadoMedico.nome_paciente.ilike(f'%{paciente_nome}%')).count()
    alto_custo = db.session.query(FormularioAltoCusto).filter(FormularioAltoCusto.nome_paciente.ilike(f'%{paciente_nome}%')).count()
    
    print(f"Dados encontrados para {paciente_nome}:")
    print(f"  Receitas: {receitas}")
    print(f"  Exames Lab: {exames_lab}")
    print(f"  Exames Imagem: {exames_img}")
    print(f"  Relatórios: {relatorios}")
    print(f"  Atestados: {atestados}")
    print(f"  Alto Custo: {alto_custo}")
    print(f"  Total: {receitas + exames_lab + exames_img + relatorios + atestados + alto_custo}")
