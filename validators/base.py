"""
Validadores base do Sistema Médico VIDAH
"""
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from core.logging import get_logger

logger = get_logger('validators')


class ValidationError(Exception):
    """Exceção customizada para erros de validação"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class BaseValidator:
    """Classe base para todos os validadores"""
    
    def __init__(self, required: bool = True, nullable: bool = False):
        self.required = required
        self.nullable = nullable
    
    def validate(self, value: Any, field_name: str = None) -> Any:
        """Método principal de validação"""
        if value is None:
            if self.required and not self.nullable:
                raise ValidationError(f"Campo obrigatório", field_name)
            return None
        
        return self._validate_value(value, field_name)
    
    def _validate_value(self, value: Any, field_name: str = None) -> Any:
        """Método a ser implementado pelos validadores específicos"""
        raise NotImplementedError


class StringValidator(BaseValidator):
    """Validador para strings"""
    
    def __init__(self, min_length: int = 0, max_length: int = None, 
                 pattern: str = None, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        if not isinstance(value, str):
            raise ValidationError(f"Deve ser uma string", field_name)
        
        # Sanitizar entrada
        value = value.strip()
        
        if len(value) < self.min_length:
            raise ValidationError(
                f"Deve ter pelo menos {self.min_length} caracteres", 
                field_name
            )
        
        if self.max_length and len(value) > self.max_length:
            raise ValidationError(
                f"Deve ter no máximo {self.max_length} caracteres", 
                field_name
            )
        
        if self.pattern and not self.pattern.match(value):
            raise ValidationError(f"Formato inválido", field_name)
        
        return value


class EmailValidator(StringValidator):
    """Validador para emails"""
    
    def __init__(self, **kwargs):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        super().__init__(pattern=email_pattern, max_length=120, **kwargs)
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        value = super()._validate_value(value, field_name)
        return value.lower()


class CPFValidator(BaseValidator):
    """Validador para CPF"""
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        if not isinstance(value, str):
            raise ValidationError(f"CPF deve ser uma string", field_name)
        
        # Remover formatação
        cpf = re.sub(r'[^0-9]', '', value)
        
        if len(cpf) != 11:
            raise ValidationError(f"CPF deve ter 11 dígitos", field_name)
        
        # Verificar se não é uma sequência de números iguais
        if cpf == cpf[0] * 11:
            raise ValidationError(f"CPF inválido", field_name)
        
        # Validar dígitos verificadores
        if not self._validate_cpf_digits(cpf):
            raise ValidationError(f"CPF inválido", field_name)
        
        # Retornar formatado
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    
    def _validate_cpf_digits(self, cpf: str) -> bool:
        """Valida os dígitos verificadores do CPF"""
        # Primeiro dígito
        sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
        
        if int(cpf[9]) != digit1:
            return False
        
        # Segundo dígito
        sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
        
        return int(cpf[10]) == digit2


class CRMValidator(BaseValidator):
    """Validador para CRM"""
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        if not isinstance(value, str):
            raise ValidationError(f"CRM deve ser uma string", field_name)
        
        # Padrão: números-UF (ex: 123456-SP)
        pattern = r'^\d{4,6}-[A-Z]{2}$'
        if not re.match(pattern, value.upper()):
            raise ValidationError(f"CRM deve ter o formato 123456-UF", field_name)
        
        return value.upper()


class DateValidator(BaseValidator):
    """Validador para datas"""
    
    def __init__(self, format: str = "%d/%m/%Y", **kwargs):
        super().__init__(**kwargs)
        self.format = format
    
    def _validate_value(self, value: Any, field_name: str = None) -> datetime:
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, str):
            try:
                return datetime.strptime(value, self.format)
            except ValueError:
                raise ValidationError(
                    f"Data deve estar no formato {self.format}", 
                    field_name
                )
        
        raise ValidationError(f"Data deve ser string ou datetime", field_name)


class IntegerValidator(BaseValidator):
    """Validador para inteiros"""
    
    def __init__(self, min_value: int = None, max_value: int = None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
    
    def _validate_value(self, value: Any, field_name: str = None) -> int:
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Deve ser um número inteiro", field_name)
        
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(
                f"Deve ser maior ou igual a {self.min_value}", 
                field_name
            )
        
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(
                f"Deve ser menor ou igual a {self.max_value}", 
                field_name
            )
        
        return value


class MedicationValidator(BaseValidator):
    """Validador específico para medicamentos"""
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        if not isinstance(value, str):
            raise ValidationError(f"Medicamento deve ser uma string", field_name)
        
        value = value.strip()
        
        if len(value) < 2:
            raise ValidationError(f"Nome do medicamento muito curto", field_name)
        
        # Verificar caracteres perigosos
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')']
        if any(char in value for char in dangerous_chars):
            raise ValidationError(f"Caracteres não permitidos no medicamento", field_name)
        
        return value


class CompositeValidator:
    """Validador para múltiplos campos"""
    
    def __init__(self, validators: Dict[str, BaseValidator]):
        self.validators = validators
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida um dicionário de dados"""
        validated_data = {}
        errors = {}
        
        for field_name, validator in self.validators.items():
            try:
                value = data.get(field_name)
                validated_data[field_name] = validator.validate(value, field_name)
            except ValidationError as e:
                errors[field_name] = e.message
                logger.warning(f"Validation error for {field_name}: {e.message}")
        
        if errors:
            raise ValidationError(f"Erros de validação: {errors}")
        
        return validated_data


# Funções helper para sanitização
def sanitize_input(value: str) -> str:
    """Sanitiza entrada removendo caracteres perigosos"""
    if not isinstance(value, str):
        return str(value)
    
    # Remover tags HTML/XML
    value = re.sub(r'<[^>]+>', '', value)
    
    # Remover caracteres perigosos
    dangerous_chars = ['<', '>', '"', "'", '&', ';']
    for char in dangerous_chars:
        value = value.replace(char, '')
    
    return value.strip()


def validate_file_upload(file, allowed_extensions: set, max_size: int) -> bool:
    """Valida upload de arquivo"""
    if not file or not file.filename:
        return False
    
    # Verificar extensão
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        raise ValidationError(f"Extensão {ext} não permitida")
    
    # Verificar tamanho (se possível)
    file.seek(0, 2)  # Ir para o final
    size = file.tell()
    file.seek(0)  # Voltar ao início
    
    if size > max_size:
        raise ValidationError(f"Arquivo muito grande (máximo: {max_size} bytes)")
    
    return True