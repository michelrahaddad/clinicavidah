
class MedicamentoData:
    """Classe auxiliar para estruturar dados de medicamentos"""
    
    def __init__(self, medicamento, posologia, via, frequencia, duracao):
        self.medicamento = medicamento or ''
        self.posologia = posologia or ''
        self.via = via or 'Oral'
        self.frequencia = frequencia or ''
        self.duracao = duracao or ''
    
    def __str__(self):
        return f"{self.medicamento} {self.posologia} - {self.via} - {self.frequencia} - {self.duracao}"

def parse_medicamentos_receita(receita):
    """Parse medications from prescription data"""
    medicamentos = []
    
    if not receita.medicamentos:
        return []
    
    # Parse stored medications
    medicamentos_list = receita.medicamentos.split(',')
    posologias_list = receita.posologias.split(',') if receita.posologias else []
    vias_list = receita.vias.split(',') if receita.vias else []
    duracoes_list = receita.duracoes.split(',') if receita.duracoes else []
    
    # Garantir que todas as listas tenham o mesmo tamanho
    max_len = len(medicamentos_list)
    while len(posologias_list) < max_len:
        posologias_list.append('')
    while len(vias_list) < max_len:
        vias_list.append('Oral')
    while len(duracoes_list) < max_len:
        duracoes_list.append('')
    
    # Criar objetos MedicamentoData
    for i in range(max_len):
        medicamento = MedicamentoData(
            medicamentos_list[i] if i < len(medicamentos_list) else '',
            posologias_list[i] if i < len(posologias_list) else '',
            vias_list[i] if i < len(vias_list) else 'Oral',
            duracoes_list[i] if i < len(duracoes_list) else '',  # Usando duracao como frequencia
            duracoes_list[i] if i < len(duracoes_list) else ''
        )
        medicamentos.append(medicamento)
    
    return medicamentos
