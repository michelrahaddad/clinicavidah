
from app import app, db
from models import *
from datetime import date, datetime

def criar_dados_michel():
    with app.app_context():
        # Verificar se Michel médico existe
        medico = db.session.query(Medico).filter(Medico.nome.ilike('%michel%')).first()
        if not medico:
            print("Médico Michel não encontrado")
            return
        
        nome_paciente = "Michel Raineri HAddad"
        data_teste = date(2025, 6, 4)
        
        # Criar exames laboratoriais se não existirem
        exames_lab_existentes = db.session.query(ExameLab).filter(
            ExameLab.nome_paciente.ilike(f'%{nome_paciente}%'),
            ExameLab.data == data_teste
        ).count()
        
        if exames_lab_existentes == 0:
            for i in range(4):
                exame_lab = ExameLab(
                    nome_paciente=nome_paciente,
                    data=data_teste,
                    exames_solicitados=f"Hemograma completo {i+1}, Glicose, Creatinina",
                    observacoes=f"Exame laboratorial {i+1} para check-up",
                    created_at=datetime.now()
                )
                db.session.add(exame_lab)
        
        # Criar exames de imagem se não existirem
        exames_img_existentes = db.session.query(ExameImg).filter(
            ExameImg.nome_paciente.ilike(f'%{nome_paciente}%'),
            ExameImg.data == data_teste
        ).count()
        
        if exames_img_existentes == 0:
            tipos_exame = ["Raio-X Tórax", "Ultrassom Abdome", "Tomografia", "Ressonância"]
            for i in range(4):
                exame_img = ExameImg(
                    nome_paciente=nome_paciente,
                    data=data_teste,
                    tipo_exame=tipos_exame[i % len(tipos_exame)],
                    local_exame="Clínica VIDAH",
                    observacoes=f"Exame de imagem {i+1}",
                    created_at=datetime.now()
                )
                db.session.add(exame_img)
        
        # Criar relatórios se não existirem
        relatorios_existentes = db.session.query(RelatorioMedico).filter(
            RelatorioMedico.nome_paciente.ilike(f'%{nome_paciente}%'),
            RelatorioMedico.data == data_teste
        ).count()
        
        if relatorios_existentes == 0:
            for i in range(2):
                relatorio = RelatorioMedico(
                    nome_paciente=nome_paciente,
                    data=data_teste,
                    diagnostico=f"Diagnóstico {i+1}: Hipertensão controlada",
                    tratamento=f"Tratamento {i+1}: Medicação anti-hipertensiva",
                    observacoes=f"Relatório médico {i+1}",
                    created_at=datetime.now()
                )
                db.session.add(relatorio)
        
        # Criar atestado se não existir
        atestados_existentes = db.session.query(AtestadoMedico).filter(
            AtestadoMedico.nome_paciente.ilike(f'%{nome_paciente}%'),
            AtestadoMedico.data == data_teste
        ).count()
        
        if atestados_existentes == 0:
            atestado = AtestadoMedico(
                nome_paciente=nome_paciente,
                data=data_teste,
                dias_afastamento=3,
                cid_codigo="Z51.1",
                motivo="Repouso médico",
                observacoes="Atestado de repouso",
                created_at=datetime.now()
            )
            db.session.add(atestado)
        
        # Criar formulário alto custo se não existir
        alto_custo_existentes = db.session.query(FormularioAltoCusto).filter(
            FormularioAltoCusto.nome_paciente.ilike(f'%{nome_paciente}%'),
            FormularioAltoCusto.data == data_teste
        ).count()
        
        if alto_custo_existentes == 0:
            alto_custo = FormularioAltoCusto(
                nome_paciente=nome_paciente,
                data=data_teste,
                medicamento="Adalimumab 40mg",
                cid_codigo="M06.9",
                justificativa="Artrite reumatoide refratária",
                observacoes="Medicamento de alto custo",
                created_at=datetime.now()
            )
            db.session.add(alto_custo)
        
        try:
            db.session.commit()
            print("✅ Dados de teste criados com sucesso!")
            
            # Verificar dados criados
            receitas = db.session.query(Receita).filter(Receita.nome_paciente.ilike(f'%{nome_paciente}%')).count()
            lab = db.session.query(ExameLab).filter(ExameLab.nome_paciente.ilike(f'%{nome_paciente}%')).count()
            img = db.session.query(ExameImg).filter(ExameImg.nome_paciente.ilike(f'%{nome_paciente}%')).count()
            rel = db.session.query(RelatorioMedico).filter(RelatorioMedico.nome_paciente.ilike(f'%{nome_paciente}%')).count()
            ate = db.session.query(AtestadoMedico).filter(AtestadoMedico.nome_paciente.ilike(f'%{nome_paciente}%')).count()
            alt = db.session.query(FormularioAltoCusto).filter(FormularioAltoCusto.nome_paciente.ilike(f'%{nome_paciente}%')).count()
            
            print(f"Resumo para {nome_paciente}:")
            print(f"  💊 Receitas: {receitas}")
            print(f"  🧪 Exames Lab: {lab}")
            print(f"  🩻 Exames Img: {img}")
            print(f"  🧾 Relatórios: {rel}")
            print(f"  📄 Atestados: {ate}")
            print(f"  💰💊 Alto Custo: {alt}")
            
        except Exception as e:
            print(f"Erro ao criar dados: {e}")
            db.session.rollback()

if __name__ == '__main__':
    criar_dados_michel()
