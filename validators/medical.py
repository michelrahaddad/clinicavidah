"""
Validadores específicos para dados médicos
"""
import re
from typing import List, Dict, Any
from validators.base import BaseValidator, ValidationError, CompositeValidator
from core.logging import get_logger

logger = get_logger('validators.medical')


class PrescriptionValidator(CompositeValidator):
    """Validador completo para prescrições médicas"""
    
    def __init__(self):
        from validators.base import StringValidator, IntegerValidator, MedicationValidator
        
        validators = {
            'nome_paciente': StringValidator(min_length=2, max_length=100),
            'medicamentos': MedicationListValidator(),
            'posologias': StringListValidator(min_items=1),
            'vias': ViaAdministracaoValidator(),
            'duracoes': StringListValidator(min_items=1),
            'observacoes': StringValidator(max_length=500, required=False)
        }
        super().__init__(validators)


class MedicationListValidator(BaseValidator):
    """Validador para lista de medicamentos"""
    
    def _validate_value(self, value: Any, field_name: str = None) -> List[str]:
        if isinstance(value, str):
            # Split por vírgula se for string
            medications = [med.strip() for med in value.split(',') if med.strip()]
        elif isinstance(value, list):
            medications = [str(med).strip() for med in value if str(med).strip()]
        else:
            raise ValidationError("Lista de medicamentos deve ser string ou lista", field_name)
        
        if not medications:
            raise ValidationError("Pelo menos um medicamento é obrigatório", field_name)
        
        # Validar cada medicamento
        validated_medications = []
        for i, med in enumerate(medications):
            if len(med) < 2:
                raise ValidationError(f"Medicamento {i+1} muito curto", field_name)
            
            # Verificar padrão básico de medicamento
            if not re.match(r'^[a-zA-ZÀ-ÿ0-9\s\-\.]+$', med):
                raise ValidationError(f"Medicamento {i+1} contém caracteres inválidos", field_name)
            
            validated_medications.append(med)
        
        return validated_medications


class StringListValidator(BaseValidator):
    """Validador para listas de strings"""
    
    def __init__(self, min_items: int = 0, max_items: int = None, **kwargs):
        super().__init__(**kwargs)
        self.min_items = min_items
        self.max_items = max_items
    
    def _validate_value(self, value: Any, field_name: str = None) -> List[str]:
        if isinstance(value, str):
            items = [item.strip() for item in value.split(',') if item.strip()]
        elif isinstance(value, list):
            items = [str(item).strip() for item in value if str(item).strip()]
        else:
            raise ValidationError("Deve ser string ou lista", field_name)
        
        if len(items) < self.min_items:
            raise ValidationError(f"Mínimo de {self.min_items} itens obrigatório", field_name)
        
        if self.max_items and len(items) > self.max_items:
            raise ValidationError(f"Máximo de {self.max_items} itens permitido", field_name)
        
        return items


class ViaAdministracaoValidator(BaseValidator):
    """Validador para vias de administração"""
    
    VALID_VIAS = {
        'oral', 'sublingual', 'intravenosa', 'intramuscular', 
        'subcutanea', 'topica', 'oftálmica', 'nasal', 'retal', 
        'vaginal', 'inalatoria', 'transdérmica'
    }
    
    def _validate_value(self, value: Any, field_name: str = None) -> List[str]:
        if isinstance(value, str):
            vias = [via.strip().lower() for via in value.split(',') if via.strip()]
        elif isinstance(value, list):
            vias = [str(via).strip().lower() for via in value if str(via).strip()]
        else:
            raise ValidationError("Vias de administração devem ser string ou lista", field_name)
        
        validated_vias = []
        for via in vias:
            if via not in self.VALID_VIAS:
                # Permitir "oral" como padrão se não reconhecida
                validated_vias.append('oral')
                logger.warning(f"Via de administração '{via}' não reconhecida, usando 'oral'")
            else:
                validated_vias.append(via)
        
        return validated_vias


class ExamValidator(CompositeValidator):
    """Validador para exames médicos"""
    
    def __init__(self):
        from validators.base import StringValidator
        
        validators = {
            'nome_paciente': StringValidator(min_length=2, max_length=100),
            'tipo_exame': ExamTypeValidator(),
            'exames_solicitados': ExamListValidator(),
            'observacoes': StringValidator(max_length=500, required=False),
            'urgente': BooleanValidator(required=False)
        }
        super().__init__(validators)


class ExamTypeValidator(BaseValidator):
    """Validador para tipos de exame"""
    
    VALID_TYPES = {'laboratorial', 'imagem', 'cardiológico', 'neurológico', 'outros'}
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        if not isinstance(value, str):
            raise ValidationError("Tipo de exame deve ser string", field_name)
        
        value = value.lower().strip()
        
        if value not in self.VALID_TYPES:
            raise ValidationError(f"Tipo de exame deve ser um de: {', '.join(self.VALID_TYPES)}", field_name)
        
        return value


class ExamListValidator(BaseValidator):
    """Validador para lista de exames"""
    
    def _validate_value(self, value: Any, field_name: str = None) -> List[str]:
        if isinstance(value, str):
            exams = [exam.strip() for exam in value.split(',') if exam.strip()]
        elif isinstance(value, list):
            exams = [str(exam).strip() for exam in value if str(exam).strip()]
        else:
            raise ValidationError("Lista de exames deve ser string ou lista", field_name)
        
        if not exams:
            raise ValidationError("Pelo menos um exame é obrigatório", field_name)
        
        # Validar cada exame
        validated_exams = []
        for i, exam in enumerate(exams):
            if len(exam) < 3:
                raise ValidationError(f"Exame {i+1} muito curto", field_name)
            
            validated_exams.append(exam)
        
        return validated_exams


class BooleanValidator(BaseValidator):
    """Validador para valores booleanos"""
    
    def _validate_value(self, value: Any, field_name: str = None) -> bool:
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ('true', '1', 'sim', 'yes', 'on'):
                return True
            elif value in ('false', '0', 'não', 'no', 'off', ''):
                return False
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        raise ValidationError("Valor deve ser booleano", field_name)


class PatientValidator(CompositeValidator):
    """Validador completo para dados de paciente"""
    
    def __init__(self):
        from validators.base import StringValidator, CPFValidator, IntegerValidator, EmailValidator
        
        validators = {
            'nome': StringValidator(min_length=2, max_length=100),
            'cpf': CPFValidator(required=False),
            'idade': IntegerValidator(min_value=0, max_value=150, required=False),
            'email': EmailValidator(required=False),
            'telefone': PhoneValidator(required=False),
            'endereco': StringValidator(max_length=200, required=False),
            'cidade_uf': StringValidator(max_length=100, required=False)
        }
        super().__init__(validators)


class PhoneValidator(BaseValidator):
    """Validador para telefones"""
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        if not isinstance(value, str):
            raise ValidationError("Telefone deve ser string", field_name)
        
        # Remover formatação
        phone = re.sub(r'[^0-9]', '', value)
        
        if len(phone) < 10 or len(phone) > 11:
            raise ValidationError("Telefone deve ter 10 ou 11 dígitos", field_name)
        
        # Formatar telefone
        if len(phone) == 10:
            return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
        else:
            return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"


class CIDValidator(BaseValidator):
    """Validador para códigos CID-10"""
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        if not isinstance(value, str):
            raise ValidationError("Código CID deve ser string", field_name)
        
        # Padrão CID-10: letra + número + ponto + número
        pattern = r'^[A-Z]\d{2}(\.\d)?$'
        value = value.upper().strip()
        
        if not re.match(pattern, value):
            raise ValidationError("Código CID deve ter o formato A00.0", field_name)
        
        return value


class MedicalCertificateValidator(CompositeValidator):
    """Validador para atestados médicos"""
    
    def __init__(self):
        from validators.base import StringValidator, IntegerValidator, DateValidator
        
        validators = {
            'nome_paciente': StringValidator(min_length=2, max_length=100),
            'cid_codigo': CIDValidator(required=False),
            'cid_descricao': StringValidator(min_length=5, max_length=200, required=False),
            'dias_afastamento': IntegerValidator(min_value=1, max_value=365),
            'data_inicio': DateValidator(required=False),
            'observacoes': StringValidator(max_length=500, required=False)
        }
        super().__init__(validators)


# Factory function para obter validadores
def get_validator(validator_type: str) -> CompositeValidator:
    """Factory para obter validadores por tipo"""
    validators = {
        'prescription': PrescriptionValidator,
        'exam': ExamValidator,
        'patient': PatientValidator,
        'certificate': MedicalCertificateValidator
    }
    
    if validator_type not in validators:
        raise ValueError(f"Tipo de validador '{validator_type}' não encontrado")
    
    return validators[validator_type]()