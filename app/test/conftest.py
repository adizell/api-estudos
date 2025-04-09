from datetime import datetime
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.db.connection import Session
from app.db.models import Specie as SpecieModel
from app.db.models import Pet as PetModel
from app.db.models import User as UserModel
import pytest

# from app.services.user_use_cases import crypt_context

crypt_context = CryptContext(schemes=['sha256_crypt'])


@pytest.fixture(scope='function')
def db_session():
    """Cria uma nova sessão de banco de dados para um teste."""
    session = Session()  # Usa SessionLocal para criar uma nova sessão
    try:
        yield session  # Retorna a sessão para uso no teste
        session.commit()  # Commit das alterações se tudo correr bem
    except Exception:
        session.rollback()  # Reverte quaisquer alterações em caso de erro
        raise
    finally:
        session.close()  # Fecha a sessão após o teste


@pytest.fixture(scope='function')
def species_on_db(db_session):
    """Insere espécies no banco de dados para testes, evitando duplicatas."""

    # Define as espécies a serem inseridas
    species = [
        SpecieModel(name="Cat"),
        SpecieModel(name="Dog"),
    ]

    # Verifica se as espécies já existem no banco de dados, buscando pelos nomes
    existing_species_names = {specie.name for specie in db_session.query(SpecieModel).all()}
    new_species = [specie for specie in species if specie.name not in existing_species_names]

    # Adiciona as novas espécies que ainda não estão no banco de dados
    if new_species:
        for specie in new_species:
            specie.generate_slug()
            db_session.add(specie)

        db_session.commit()

    yield species

    # A limpeza será tratada pelo rollback da fixture `db_session`


@pytest.fixture()
def pet_on_db(db_session):
    """Insere um pet associado a uma espécie no banco de dados."""
    specie = SpecieModel(name="Cat")
    specie.generate_slug()
    db_session.add(specie)
    db_session.commit()  # Garante que a espécie seja persistida antes de associar um pet

    pet = PetModel(
        name="Katarina",
        slug="katarina",
        sex="F",
        castrated=True,
        public=True,
        pro=True,
        date_birth=datetime(2020, 1, 1),
        specie_id=specie.id
    )

    db_session.add(pet)
    db_session.commit()  # Garante que o pet seja persistido

    yield pet


@pytest.fixture()
def pets_on_db(db_session):
    """Insere um conjunto de pets associados a uma espécie no banco de dados."""
    # Cria e salva uma espécie única
    specie = SpecieModel(name='Cat')
    specie.generate_slug()
    db_session.add(specie)
    db_session.commit()  # Commit para garantir que a espécie esteja disponível

    # Define os dados dos pets
    pet_data = [
        {"name": "Katarina", "sex": "F", "castrated": True, "public": True, "pro": True,
         "date_birth": datetime(2020, 1, 1)},
        {"name": "Tilina", "sex": "F", "castrated": True, "public": True, "pro": True,
         "date_birth": datetime(2020, 1, 1)},
        {"name": "Insti", "sex": "F", "castrated": True, "public": True, "pro": True,
         "date_birth": datetime(2020, 1, 1)},
        {"name": "Dim", "sex": "F", "castrated": True, "public": True, "pro": True, "date_birth": datetime(2020, 1, 1)},
    ]

    pets = []
    for data in pet_data:
        pet = PetModel(
            name=data["name"],
            slug=data["name"].lower(),  # Gera o slug baseado no nome
            sex=data["sex"],
            castrated=data["castrated"],
            public=data["public"],
            pro=data["pro"],
            date_birth=data["date_birth"],
            specie_id=specie.id  # Associa o pet à espécie criada
        )
        db_session.add(pet)
        pets.append(pet)

    db_session.commit()  # Commit para garantir que todos os pets estejam salvos

    yield pets  # Retorna a lista de pets


@pytest.fixture()
def user_on_db(db_session):
    user = UserModel(
        username='Mandrik',
        password=crypt_context.hash('pass#')
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    yield user

    db_session.delete(user)
    db_session.commit()
