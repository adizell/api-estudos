# app/schemas/pet_schemas.py
from typing import Optional
from uuid import UUID

from pydantic import Field, constr, PositiveInt
from datetime import datetime
from enum import Enum
from app.schemas.base import CustomBaseModel


class SexEnum(str, Enum):
    M = 'M'
    F = 'F'


class PetBase(CustomBaseModel):
    name: constr(min_length=1, max_length=100)
    sex: SexEnum
    castrated: bool = Field(default=False)
    public: bool = Field(default=False)
    pro: bool = Field(default=False)
    date_birth: datetime
    specie_id: PositiveInt

    # Adicione estes campos para permitir a seleção de categorias
    category_environment_id: Optional[int] = None
    category_condition_id: Optional[int] = None
    category_purpose_id: Optional[int] = None
    category_habitat_id: Optional[int] = None
    category_origin_id: Optional[int] = None
    category_size_id: Optional[int] = None
    category_age_id: Optional[int] = None


class PetCreate(PetBase):
    """Schema usado para criação de um pet."""
    # Aqui não tem owner_id. Ele será determinado pelo token do usuário.


class PetUpdate(PetBase):
    """Schema usado para atualização de um pet (todos campos opcionais)."""
    name: constr(min_length=1, max_length=100) | None = None
    sex: SexEnum | None = None
    castrated: bool | None = None
    public: bool | None = None
    pro: bool | None = None
    date_birth: datetime | None = None
    specie_id: PositiveInt | None = None


class PetOutput(PetBase):
    id: UUID
    slug: str
    owner_id: UUID  # Mostra quem é o dono
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
