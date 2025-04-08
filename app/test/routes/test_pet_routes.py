from fastapi.testclient import TestClient
from fastapi import status
from app.db.models import Pet as PetModel
from app.main import app

client = TestClient(app)
headers = {"Authorization": "Bearer token"}
client.headers = headers


def test_add_pet_route(db_session, species_on_db):
    body = {
        "name": species_on_db[0].name,  # Nome da espécie
        "pet": {
            "name": "Katarina",
            "species_id": species_on_db[0].id,  # Adiciona species_id
            "sex": "F",
            "date_birth": "2023-04-28T00:00:00",
            "castrated": True,
            "public": True,
            "pro": True,
        },
    }

    response = client.post("/pet/add", json=body)

    assert response.status_code == status.HTTP_201_CREATED

    pets_on_db = db_session.query(PetModel).all()

    assert len(pets_on_db) == 1

    db_session.delete(pets_on_db[0])
    db_session.commit()


def test_add_pet_route_invalid_specie(db_session):
    body = {
        "name": "invalid",
        "pet": {
            "name": "Katarina",
            "species_id": 999,  # ID de espécie inválido
            "sex": "F",
            "date_birth": "2023-04-28T00:00:00",
            "castrated": True,
            "public": True,
            "pro": True,
        },
    }

    response = client.post("/pet/add", json=body)

    assert response.status_code == status.HTTP_404_NOT_FOUND

    pet_on_db = db_session.query(PetModel).all()

    assert len(pet_on_db) == 0


def test_update_pet_route(db_session, pet_on_db):
    body = {
        "name": "Updated Katarina",
        "species_id": 1,
        "sex": "F",
        "date_birth": "2023-04-28T00:00:00",
        "castrated": True,
        "public": True,
        "pro": True,
    }

    response = client.put(f"/pet/update/{pet_on_db.id}", json=body)

    assert response.status_code == status.HTTP_200_OK

    db_session.refresh(pet_on_db)

    pet_on_db.name == "Updated Katarina"
    pet_on_db.sex == "F"
    pet_on_db.date_birth == "2023-04-28T00:00:00"


def test_update_pet_route_invalid_id():
    body = {
        "name": "Updated Katarina",
        "species_id": 1,
        "sex": "F",
        "date_birth": "2023-04-28T00:00:00",
        "castrated": True,
        "public": True,
        "pro": True,
    }

    response = client.put(f"/pet/update/1", json=body)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_pet_route(db_session, pet_on_db):
    response = client.delete('/pet/delete/{pet_on_db.id}')

    assert response.status_code == status.HTTP_200_OK

    pets_on_db = db_session.query(PetModel).all

    assert len(pets_on_db) == 0


def test_delete_pet_route_invalid_id():
    response = client.delete('/pet/delete/1')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_pets_route(pets_on_db):
    response = client.get('/pet/list')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 4

    assert data[0] == {
        "id": pets_on_db[0].id,
        "name": pets_on_db[0].name,
        "slug": pets_on_db[0].slug,
        "sex": pets_on_db[0].sex,
        "castrated": pets_on_db[0].castrated,
        "public": pets_on_db[0].public,
        "pro": pets_on_db[0].pro,
        "date_birth": pets_on_db[0].date_birth,
        "specie": {
            'name': pets_on_db[0].specie.name,
        }
    }


def test_list_pets_route_with_search(pets_on_db):
    response = client.get('/pet/list?search=Katarina')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1

    assert data[0] == {
        "id": pets_on_db[0].id,
        "name": pets_on_db[0].name,
        "slug": pets_on_db[0].slug,
        "sex": pets_on_db[0].sex,
        "castrated": pets_on_db[0].castrated,
        "public": pets_on_db[0].public,
        "pro": pets_on_db[0].pro,
        "date_birth": pets_on_db[0].date_birth,
        "specie": {
            'name': pets_on_db[0].specie.name,
        }
    }
