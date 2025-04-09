import pytest
from datetime import datetime
from app.services.pet_services import PetServices
from app.schemas.pet_schemas import PetCreate, PetUpdate
from app.db.models import Pet as PetModel, Specie as SpecieModel
from fastapi import HTTPException


def test_add_pet_uc(db_session, species_on_db):
    use_case = PetServices(db_session)

    # Aqui, o species_on_db deve ter pelo menos uma espécie
    assert len(species_on_db) > 0, "A lista de espécies está vazia!"

    specie = species_on_db[0]

    pet_data = PetCreate(
        name="Katarina",
        sex="F",
        castrated=True,
        public=True,
        pro=True,
        date_birth="2020-01-01",
        specie_id=specie.id
    )

    new_pet = use_case.add_pet(
        pet=pet_data.name,
        specie_id=pet_data.specie_id,
        sex=pet_data.sex,
        castrated=pet_data.castrated,
        public=pet_data.public,
        pro=pet_data.pro,
        date_birth=pet_data.date_birth
    )

    assert new_pet.name == "Katarina"
    assert new_pet.specie_id == specie.id


def test_add_pet_uc_invalid_specie(db_session):
    use_case = PetServices(db_session)

    pet_data = PetCreate(
        name="Ghost",
        sex="M",
        castrated=False,
        public=True,
        pro=False,
        date_birth="2020-01-01",
        specie_id=9999  # ID inválido
    )

    with pytest.raises(HTTPException) as excinfo:
        use_case.add_pet(
            pet=pet_data.name,
            specie_id=pet_data.specie_id,
            sex=pet_data.sex,
            castrated=pet_data.castrated,
            public=pet_data.public,
            pro=pet_data.pro,
            date_birth=pet_data.date_birth
        )

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Essa espécie não existe"


def test_update_pet(db_session, species_on_db):
    use_case = PetServices(db_session)
    specie = species_on_db[0]

    pet_data = PetCreate(
        name="Katarina",
        sex="F",
        castrated=True,
        public=True,
        pro=True,
        date_birth="2020-01-01",
        specie_id=specie.id
    )

    new_pet = use_case.add_pet(
        pet=pet_data.name,
        specie_id=pet_data.specie_id,
        sex=pet_data.sex,
        castrated=pet_data.castrated,
        public=pet_data.public,
        pro=pet_data.pro,
        date_birth=pet_data.date_birth
    )

    update_data = PetUpdate(
        name="Katarina Updated",
        sex="F",
        castrated=False,
        public=False,
        pro=False,
        date_birth="2021-01-01",
        specie_id=specie.id
    )

    updated_pet = use_case.update_pet(
        id=new_pet.id,
        pet=update_data
    )

    assert updated_pet.name == "Katarina Updated"
    assert updated_pet.castrated is False
    assert updated_pet.public is False
    assert updated_pet.date_birth.strftime('%Y-%m-%d') == "2021-01-01"


def test_update_pet_invalid_id(db_session):
    use_case = PetServices(db_session)

    update_data = PetUpdate(
        name="Non-existent Pet",
        sex="M",
        castrated=True,
        public=True,
        pro=True,
        date_birth="2021-01-01",
        specie_id=1
    )

    with pytest.raises(HTTPException) as excinfo:
        use_case.update_pet(
            id=9999,  # ID inexistente
            pet=update_data
        )

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Esse pet não existe"


def test_delete_pet(db_session, species_on_db):
    use_case = PetServices(db_session)
    specie = species_on_db[0]

    pet_data = PetCreate(
        name="Katarina",
        sex="F",
        castrated=True,
        public=True,
        pro=True,
        date_birth="2020-01-01",
        specie_id=specie.id
    )

    new_pet = use_case.add_pet(
        pet=pet_data.name,
        specie_id=pet_data.specie_id,
        sex=pet_data.sex,
        castrated=pet_data.castrated,
        public=pet_data.public,
        pro=pet_data.pro,
        date_birth=pet_data.date_birth
    )

    result = use_case.delete_pet(id=new_pet.id)
    assert result is True

    pet_in_db = db_session.query(PetModel).filter_by(id=new_pet.id).first()
    assert pet_in_db is None


def test_delete_pet_non_exist(db_session):
    use_case = PetServices(db_session)

    with pytest.raises(HTTPException) as excinfo:
        use_case.delete_pet(id=9999)  # ID inexistente

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Esse pet não existe"


def test_list_pets(db_session, species_on_db):
    use_case = PetServices(db_session)
    specie = species_on_db[0]

    pet_names = ["Katarina", "Tilina", "Insti", "Dim"]
    for name in pet_names:
        pet_data = PetCreate(
            name=name,
            sex="F",
            castrated=True,
            public=True,
            pro=False,
            date_birth="2020-01-01",
            specie_id=specie.id
        )
        use_case.add_pet(
            pet=pet_data.name,
            specie_id=pet_data.specie_id,
            sex=pet_data.sex,
            castrated=pet_data.castrated,
            public=pet_data.public,
            pro=pet_data.pro,
            date_birth=pet_data.date_birth
        )

    pets = use_case.list_pets()
    assert len(pets) == 4
    pet_names_in_db = [pet.name for pet in pets]
    for name in pet_names:
        assert name in pet_names_in_db


def test_list_pets_with_search(db_session, species_on_db):
    use_case = PetServices(db_session)
    specie = species_on_db[0]

    pet_names = ["Katarina", "Tilina", "Insti", "Dim"]
    for name in pet_names:
        pet_data = PetCreate(
            name=name,
            sex="F",
            castrated=True,
            public=True,
            pro=False,
            date_birth="2020-01-01",
            specie_id=specie.id
        )
        use_case.add_pet(
            pet=pet_data.name,
            specie_id=pet_data.specie_id,
            sex=pet_data.sex,
            castrated=pet_data.castrated,
            public=pet_data.public,
            pro=pet_data.pro,
            date_birth=pet_data.date_birth
        )

    pets = use_case.list_pets(search="Kat")
    assert len(pets) == 1
    assert pets[0].name == "Katarina"
