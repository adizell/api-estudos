import pytest
from pydantic import ValidationError
from app.schemas.pet_schemas import PetCreate, PetUpdate, PetOutput, SexEnum
from datetime import datetime


# Teste para criação válida de Pet
def test_valid_pet_create():
    pet_data = {
        "name": "Katarina",
        "sex": "F",
        "castrated": True,
        "public": True,
        "pro": False,
        "date_birth": "2020-01-01",
        "specie_id": 1
    }

    pet = PetCreate(**pet_data)

    assert pet.name == "Katarina"
    assert pet.sex == SexEnum.F
    assert pet.castrated is True
    assert pet.public is True
    assert pet.pro is False
    assert pet.date_birth == datetime(2020, 1, 1)
    assert pet.specie_id == 1


# Teste para criação inválida de Pet (sem nome)
def test_invalid_pet_create_missing_name():
    pet_data = {
        "sex": "M",
        "castrated": True,
        "public": True,
        "pro": False,
        "date_birth": "2020-01-01",
        "specie_id": 1
    }

    with pytest.raises(ValidationError):
        PetCreate(**pet_data)


# Teste para atualização válida de Pet
def test_valid_pet_update():
    update_data = {
        "name": "Updated Pet",
        "sex": "M",
        "castrated": False,
        "public": False,
        "pro": True,
        "date_birth": "2021-01-01",
        "specie_id": 2
    }

    pet = PetUpdate(**update_data)

    assert pet.name == "Updated Pet"
    assert pet.sex == SexEnum.M
    assert pet.castrated is False
    assert pet.public is False
    assert pet.pro is True
    assert pet.date_birth == datetime(2021, 1, 1)
    assert pet.specie_id == 2


# Teste para validação de saída de Pet
def test_pet_output_schema():
    output_data = {
        "id": 1,
        "name": "Katarina",
        "slug": "katarina",
        "sex": "F",
        "castrated": True,
        "public": True,
        "pro": False,
        "date_birth": "2020-01-01",
        "created_at": "2020-01-01T10:00:00",
        "updated_at": "2020-01-01T10:00:00",
        "specie_id": 1
    }

    pet_output = PetOutput(**output_data)

    assert pet_output.id == 1
    assert pet_output.name == "Katarina"
    assert pet_output.slug == "katarina"
    assert pet_output.sex == SexEnum.F
    assert pet_output.castrated is True
    assert pet_output.public is True
    assert pet_output.pro is False
    assert pet_output.date_birth == datetime(2020, 1, 1)
    assert pet_output.created_at == datetime(2020, 1, 1, 10, 0, 0)
    assert pet_output.updated_at == datetime(2020, 1, 1, 10, 0, 0)
    assert pet_output.specie_id == 1
