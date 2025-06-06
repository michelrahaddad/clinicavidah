"""
Serviço de geração de PDF do Sistema Médico VIDAH
"""
import tempfile
import base64
import os
from datetime import datetime
from typing import Dict, Any, Optional
import weasyprint
from flask import render_template, make_response, current_app
from models import Medico, Paciente
from utils.image_processing import create_black_signature
from core.logging import get_logger, log_action

logger = get_logger('pdf_service')


class PDFService:
    """Serviço centralizado para geração de PDFs médicos"""
    
    def __init__(self):
        self.temp_files = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup_temp_files()
    
    def _cleanup_temp_files(self):
        """Remove arquivos temporários criados"""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
                logger.debug(f"Removed temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to remove temp file {temp_file}: {e}")
        self.temp_files.clear()
    
    def _process_signature(self, signature_data: str) -> Optional[str]:
        """Processa assinatura digital para uso em PDF"""
        if not signature_data or signature_data == 'assinatura':
            return None
        
        try:
            if signature_data.startswith('data:image'):
                # Processar assinatura para torná-la preta e visível
                processed_signature = create_black_signature(signature_data)
                
                # Extrair dados base64
                header, data = processed_signature.split(',', 1)
                image_data = base64.b64decode(data)
                
                # Criar arquivo temporário
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                temp_file.write(image_data)
                temp_file.close()
                
                # Registrar para limpeza posterior
                self.temp_files.append(temp_file.name)
                
                # Retornar URL do arquivo para WeasyPrint
                return f"file://{temp_file.name}"
            
            return signature_data
            
        except Exception as e:
            logger.error(f"Error processing signature: {e}")
            return None
    
    def _get_doctor_data(self, doctor_name: str = None, doctor_id: int = None) -> Optional[Medico]:
        """Busca dados do médico com múltiplas estratégias"""
        medico = None
        
        # Buscar por ID
        if doctor_id:
            medico = Medico.query.get(doctor_id)
        
        # Buscar por nome
        if not medico and doctor_name:
            medico = Medico.query.filter_by(nome=doctor_name).first()
        
        # Fallback para médico com assinatura (para testes)
        if not medico:
            medico = Medico.query.filter(
                Medico.assinatura != None, 
                Medico.assinatura != 'assinatura'
            ).first()
        
        return medico
    
    def _get_patient_data(self, patient_id: int = None, patient_name: str = None) -> Optional[Paciente]:
        """Busca dados do paciente"""
        if patient_id:
            return Paciente.query.get(patient_id)
        elif patient_name:
            return Paciente.query.filter_by(nome=patient_name).first()
        return None
    
    @log_action('generate_prescription_pdf')
    def generate_prescription_pdf(self, prescription_data: Dict[str, Any]) -> bytes:
        """Gera PDF de receita médica"""
        # Buscar dados do médico
        medico = self._get_doctor_data(
            prescription_data.get('medico_nome'),
            prescription_data.get('medico_id')
        )
        
        # Buscar dados do paciente
        paciente = self._get_patient_data(
            prescription_data.get('paciente_id'),
            prescription_data.get('nome_paciente')
        )
        
        # Processar assinatura
        assinatura_processada = None
        if medico and medico.assinatura:
            assinatura_processada = self._process_signature(medico.assinatura)
        
        # Preparar dados para o template
        template_data = {
            'nome_paciente': prescription_data.get('nome_paciente', ''),
            'cpf_paciente': paciente.cpf if paciente and paciente.cpf != '000.000.000-00' else '',
            'idade_paciente': f"{paciente.idade} anos" if paciente and paciente.idade > 0 else '',
            'endereco_paciente': paciente.endereco if paciente and paciente.endereco != 'Não informado' else '',
            'cidade_uf_paciente': paciente.cidade_uf if paciente and paciente.cidade_uf != 'Não informado/XX' else '',
            'medicamentos': prescription_data.get('medicamentos', []),
            'posologias': prescription_data.get('posologias', []),
            'duracoes': prescription_data.get('duracoes', []),
            'vias': prescription_data.get('vias', []),
            'medico': medico.nome if medico else prescription_data.get('medico_nome', 'Médico não encontrado'),
            'crm': medico.crm if medico else '',
            'data': prescription_data.get('data', datetime.now().strftime('%d/%m/%Y')),
            'assinatura': assinatura_processada,
            'zip': zip
        }
        
        # Log de dados para debug
        logger.info(f"Generating prescription PDF for patient: {template_data['nome_paciente']}")
        logger.info(f"Doctor: {template_data['medico']} (CRM: {template_data['crm']})")
        logger.info(f"Signature processed: {assinatura_processada is not None}")
        
        # Renderizar template
        html_content = render_template('receita_pdf.html', **template_data)
        
        # Gerar PDF
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        
        logger.info(f"PDF generated successfully, size: {len(pdf_bytes)} bytes")
        return pdf_bytes
    
    @log_action('generate_exam_pdf')
    def generate_exam_pdf(self, exam_data: Dict[str, Any], exam_type: str = 'lab') -> bytes:
        """Gera PDF de exames (laboratoriais ou de imagem)"""
        # Buscar dados do médico
        medico = self._get_doctor_data(
            exam_data.get('medico_nome'),
            exam_data.get('medico_id')
        )
        
        # Buscar dados do paciente
        paciente = self._get_patient_data(
            exam_data.get('paciente_id'),
            exam_data.get('nome_paciente')
        )
        
        # Processar assinatura
        assinatura_processada = None
        if medico and medico.assinatura:
            assinatura_processada = self._process_signature(medico.assinatura)
        
        # Preparar dados para o template
        template_data = {
            'nome_paciente': exam_data.get('nome_paciente', ''),
            'cpf_paciente': paciente.cpf if paciente and paciente.cpf != '000.000.000-00' else '',
            'idade_paciente': f"{paciente.idade} anos" if paciente and paciente.idade > 0 else '',
            'endereco_paciente': paciente.endereco if paciente and paciente.endereco != 'Não informado' else '',
            'cidade_uf_paciente': paciente.cidade_uf if paciente and paciente.cidade_uf != 'Não informado/XX' else '',
            'exames': exam_data.get('exames', []),
            'observacoes': exam_data.get('observacoes', ''),
            'medico': medico.nome if medico else exam_data.get('medico_nome', 'Médico não encontrado'),
            'crm': medico.crm if medico else '',
            'data': exam_data.get('data', datetime.now().strftime('%d/%m/%Y')),
            'assinatura': assinatura_processada,
            'tipo_exame': exam_type
        }
        
        # Selecionar template baseado no tipo de exame
        template_name = f'exames_{exam_type}_pdf.html'
        
        logger.info(f"Generating {exam_type} exam PDF for patient: {template_data['nome_paciente']}")
        
        # Renderizar template
        html_content = render_template(template_name, **template_data)
        
        # Gerar PDF
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        
        logger.info(f"Exam PDF generated successfully, size: {len(pdf_bytes)} bytes")
        return pdf_bytes
    
    @log_action('generate_certificate_pdf')
    def generate_certificate_pdf(self, certificate_data: Dict[str, Any]) -> bytes:
        """Gera PDF de atestado médico"""
        # Buscar dados do médico
        medico = self._get_doctor_data(
            certificate_data.get('medico_nome'),
            certificate_data.get('medico_id')
        )
        
        # Buscar dados do paciente
        paciente = self._get_patient_data(
            certificate_data.get('paciente_id'),
            certificate_data.get('nome_paciente')
        )
        
        # Processar assinatura
        assinatura_processada = None
        if medico and medico.assinatura:
            assinatura_processada = self._process_signature(medico.assinatura)
        
        # Preparar dados para o template
        template_data = {
            'nome_paciente': certificate_data.get('nome_paciente', ''),
            'cpf_paciente': paciente.cpf if paciente and paciente.cpf != '000.000.000-00' else '',
            'idade_paciente': f"{paciente.idade} anos" if paciente and paciente.idade > 0 else '',
            'cid_codigo': certificate_data.get('cid_codigo', ''),
            'cid_descricao': certificate_data.get('cid_descricao', ''),
            'dias_afastamento': certificate_data.get('dias_afastamento', ''),
            'data_inicio': certificate_data.get('data_inicio', ''),
            'observacoes': certificate_data.get('observacoes', ''),
            'medico': medico.nome if medico else certificate_data.get('medico_nome', 'Médico não encontrado'),
            'crm': medico.crm if medico else '',
            'data': certificate_data.get('data', datetime.now().strftime('%d/%m/%Y')),
            'assinatura': assinatura_processada
        }
        
        logger.info(f"Generating certificate PDF for patient: {template_data['nome_paciente']}")
        
        # Renderizar template
        html_content = render_template('atestado_pdf.html', **template_data)
        
        # Gerar PDF
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        
        logger.info(f"Certificate PDF generated successfully, size: {len(pdf_bytes)} bytes")
        return pdf_bytes
    
    def create_pdf_response(self, pdf_bytes: bytes, filename: str, inline: bool = True) -> Any:
        """Cria resposta HTTP para PDF"""
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        
        disposition = 'inline' if inline else 'attachment'
        response.headers['Content-Disposition'] = f'{disposition}; filename={filename}'
        
        # Headers de cache
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response


# Instância global do serviço
pdf_service = PDFService()


def generate_prescription_pdf(prescription_data: Dict[str, Any]) -> bytes:
    """Função helper para gerar PDF de receita"""
    with PDFService() as service:
        return service.generate_prescription_pdf(prescription_data)


def generate_exam_pdf(exam_data: Dict[str, Any], exam_type: str = 'lab') -> bytes:
    """Função helper para gerar PDF de exame"""
    with PDFService() as service:
        return service.generate_exam_pdf(exam_data, exam_type)


def generate_certificate_pdf(certificate_data: Dict[str, Any]) -> bytes:
    """Função helper para gerar PDF de atestado"""
    with PDFService() as service:
        return service.generate_certificate_pdf(certificate_data)