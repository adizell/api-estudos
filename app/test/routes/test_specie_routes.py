import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.models.specie_model import Specie as SpecieModel
from app.db.connection import Session

client = TestClient(app)
headers = {"Authorization": "Bearer token"}
client.headers = headers


@pytest.fixture()
def clean_db(db_session):
    db_session.query(SpecieModel).delete()  # Limpa todas as espécies
    db_session.commit()


# Fixtures de setup para criar a sessão do banco e popular com espécies
@pytest.fixture()
def db_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture()
def species_on_db(db_session):
    db_session.query(SpecieModel).delete()  # Limpa o DB antes de popular
    db_session.commit()

    species = [
        SpecieModel(name="Cat"),
        SpecieModel(name="Dog"),
    ]
    for specie in species:
        specie.generate_slug()  # Garante que o slug seja gerado
        db_session.add(specie)

    db_session.commit()

    yield species

    # Limpeza das espécies após o teste
    db_session.query(SpecieModel).delete()
    db_session.commit()


# Testes para rota de listar espécies
def test_list_species_empty(db_session):
    # Certifica-se de que o banco de dados está vazio antes do teste
    db_session.query(SpecieModel).delete()
    db_session.commit()

    response = client.get("/specie/list")
    assert response.status_code == 200
    assert response.json() == []


def test_list_species(species_on_db):
    response = client.get("/specie/list")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Cat"
    assert response.json()[1]["name"] == "Dog"


# Teste para adicionar espécie
def test_add_specie(db_session):
    specie_data = {
        "name": "Fish"
    }
    response = client.post("/specie/add", json=specie_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Fish"
    assert data["slug"] == "fish"  # Verifique se o slug foi gerado corretamente


# Teste para não permitir duplicação de espécies
def test_add_duplicate_specie(species_on_db):
    specie_data = {
        "name": "Cat"
    }
    response = client.post("/specie/add", json=specie_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Specie with name 'Cat' already exists"


# Teste para deletar espécie existente
def test_delete_specie(species_on_db):
    specie_id = species_on_db[0].id
    response = client.delete(f"/specie/delete/{specie_id}")
    assert response.status_code == 200
    assert response.json() == {"detail": "Specie deleted successfully"}


# Teste para deletar espécie inexistente
def test_delete_nonexistent_specie():
    response = client.delete("/specie/delete/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Specie with ID 999 not found"}


# Teste para atualizar espécie existente
def test_update_specie(species_on_db):
    specie_id = species_on_db[0].id
    update_data = {
        "name": "Big Cat"
    }
    response = client.put(f"/specie/update/{specie_id}", json=update_data)
    assert response.status_code == 200

    # Verifica se o nome foi atualizado corretamente
    response = client.get("/specie/list")
    updated_specie = next(item for item in response.json() if item["id"] == specie_id)
    assert updated_specie["name"] == "Big Cat"


# Teste para atualizar espécie inexistente
def test_update_nonexistent_specie():
    update_data = {
        "name": "Big Fish"
    }
    response = client.put("/specie/update/999", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Specie with ID 999 not found"}
