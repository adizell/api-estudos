# app/schemas/specie_schemas.py

from app.utils.input_validation import InputValidator
from typing import Optional
from pydantic import (
    field_validator,
    PositiveInt,
    BaseModel,
    constr,
    Field,
)


# Base schema para Specie com validações
class SpecieBase(BaseModel):
    name: constr(min_length=1, max_length=100)  # Validação para garantir que o nome não seja vazio ou muito longo

    @field_validator('name')
    def validate_name_security(cls, v):
        is_valid, error_msg = InputValidator.validate_name(v)
        if not is_valid:
            raise ValueError(error_msg)
        return InputValidator.sanitize_name(v)


# Schema para criação de uma Specie
class SpecieCreate(BaseModel):
    name: str

    class Config:
        from_attributes = True  # Substitui orm_mode


# Schema para atualização de Specie
class SpecieUpdate(SpecieBase):
    name: Optional[
        constr(min_length=1, max_length=100)] = None  # Permite que o nome seja opcional durante a atualização


# Schema de saída para Specie (inclui ID e Slug)
class SpecieOutput(SpecieBase):
    id: PositiveInt  # Garante que o ID seja sempre um número positivo
    slug: str  # Slug gerado a partir do nome
    is_active: bool = Field(..., description="Indica se a espécie está ativa")

    class Config:
        from_attributes = True  # Para suportar a conversão automática do modelo SQLAlchemy para Pydantic


# Schema para atualização de status da Specie
class SpecieStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="Novo status para a espécie (ativo/inativo)")
