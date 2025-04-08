import pytest
from pydantic import ValidationError
from app.schemas.specie_schemas import SpecieCreate, SpecieOutput


# Teste para validar a criação de uma espécie com dados válidos
def test_valid_specie_create():
    specie_data = {
        "name": "Cachorro"
    }
    specie = SpecieCreate(**specie_data)
    assert specie.name == "Cachorro"


# Teste para garantir que um erro seja gerado ao criar uma espécie sem nome
def test_invalid_specie_create_missing_name():
    specie_data = {}
    with pytest.raises(ValidationError):
        SpecieCreate(**specie_data)


# Teste para garantir que a saída da espécie esteja correta
def test_valid_specie_output():
    specie_data = {
        "id": 1,
        "name": "Cavalo",
        "slug": "cavalo"
    }
    specie_output = SpecieOutput(**specie_data)
    assert specie_output.id == 1
    assert specie_output.name == "Cavalo"
    assert specie_output.slug == "cavalo"


# Teste para garantir que a saída da espécie não aceita dados inválidos
def test_invalid_specie_output_missing_name():
    specie_data = {
        "id": 1,
        "slug": "cavalo"
    }
    with pytest.raises(ValidationError):
        SpecieOutput(**specie_data)
