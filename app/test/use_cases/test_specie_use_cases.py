from fastapi import HTTPException

from app.db.connection import Session
from app.use_cases.specie_use_cases import SpecieUseCases
from app.schemas.specie_schemas import SpecieCreate, SpecieUpdate


def test_add_duplicate_specie(db_session):
    use_case = SpecieUseCases(db_session)

    specie_data = SpecieCreate(name="Cat")

    # Adicionando a primeira vez
    use_case.add_specie(specie_data=specie_data)

    # Tentando adicionar novamente a mesma espécie para simular duplicidade
    try:
        use_case.add_specie(specie_data=specie_data)
    except HTTPException as e:
        db_session.rollback()  # Rollback para garantir que a sessão esteja limpa
        assert e.status_code == 400
        assert "Specie with name 'Cat' already exists" in e.detail


def test_delete_existing_specie(db_session: Session):
    use_case = SpecieUseCases(db_session)

    specie_data = SpecieCreate(name="Dog")
    specie = use_case.add_specie(specie_data=specie_data)

    try:
        result = use_case.delete_specie(specie.id)
        assert result == {"message": "Specie deleted successfully"}  # Verifique a mensagem retornada
    except Exception as e:
        db_session.rollback()  # Rollback para garantir que a sessão esteja limpa
        raise e


def test_update_existing_specie(db_session):
    use_case = SpecieUseCases(db_session)

    specie_data = SpecieCreate(name="Fish")
    specie = use_case.add_specie(specie_data=specie_data)

    update_data = SpecieUpdate(name="Updated Fish")

    try:
        updated_specie = use_case.update_specie(specie.id, update_data)  # Remova 'update_data=' para passar diretamente
        assert updated_specie.name == "Updated Fish"
    except Exception as e:
        db_session.rollback()  # Rollback para garantir que a sessão esteja limpa
        raise e
