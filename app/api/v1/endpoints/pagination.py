# app/api/v1/endpoints/pagination.py
"""
Endpoints com suporte avançado de paginação.

Este módulo contém rotas com diferentes estratégias de paginação para
pets e species, oferecendo opções avançadas além das rotas padrão.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi_pagination import Page, LimitOffsetPage, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from app.api.deps import get_db_session, get_current_user
from app.db.models.pet_model import Pet
from app.db.models.specie_model import Specie
from app.db.models.user.user_model import User
from app.schemas.pet_schemas import PetOutput
from app.schemas.specie_schemas import SpecieOutput
from app.utils.pagination import pagination_params, limit_offset_params
from app.security.permissions import require_permission, require_permission_or_superuser

# Router para paginação de pets
pet_pagination_router = APIRouter(
    prefix="/pagination/pet",
    tags=["Pet Pagination"],
    dependencies=[Depends(get_current_user)]
)

# Router para paginação de species
specie_pagination_router = APIRouter(
    prefix="/pagination/specie",
    tags=["Specie Pagination"]
)


def get_pet_query(db: Session, user: User):
    """
    Retorna a query de pets com base na permissão do usuário.
    - Superusuários veem todos os pets.
    - Usuários comuns veem apenas seus próprios pets.
    """
    query = db.query(Pet)
    if not user.is_superuser:
        query = query.filter(Pet.owner_id == user.id)
    return query


def get_specie_query(db: Session) -> Session.query:
    """
    Retorna uma query de espécies para paginação.
    """
    return db.query(Specie)


# Rotas de paginação para pets

@pet_pagination_router.get(
    "/list",
    response_model=Page[PetOutput],
    summary="List Pets - Listar pets do usuário com paginação",
    description=(
            "Retorna uma lista paginada de pets vinculados ao usuário autenticado.\n"
            "- Se for superusuário, retorna todos os pets.\n"
            "- Caso contrário, apenas os pets do usuário logado.\n"
            "Requer permissão 'list_pets' ou ser superusuário."
    ),
    dependencies=[Depends(require_permission("list_pets"))],
)
def list_pets(
        db_session: Session = Depends(get_db_session),
        current_user: User = Depends(get_current_user),
        params=Depends(pagination_params),
):
    return sqlalchemy_paginate(get_pet_query(db_session, current_user), params)


@pet_pagination_router.get(
    "/list/limit-offset",
    response_model=LimitOffsetPage[PetOutput],
    summary="List Pets (Limit-Offset) - Listar pets com limit e offset",
    description=(
            "Retorna uma lista paginada de pets vinculados ao usuário autenticado.\n"
            "- Se for superusuário, retorna todos os pets.\n"
            "- Caso contrário, apenas os pets do usuário logado.\n"
            "Requer permissão 'list_pets' ou ser superusuário."
    ),
    dependencies=[Depends(require_permission("list_pets"))],
)
def list_pets_limit_offset(
        db_session: Session = Depends(get_db_session),
        current_user: User = Depends(get_current_user),
        params=Depends(limit_offset_params),
):
    return sqlalchemy_paginate(get_pet_query(db_session, current_user), params)


# Rotas de paginação para species

@specie_pagination_router.get(
    "/list",
    response_model=Page[SpecieOutput],
    summary="List Species - Listar espécies com paginação",
    description=(
            "Retorna uma lista paginada de todas as espécies cadastradas no sistema.\n"
            "- Requer autenticação com token JWT do usuário.\n"
            "- Somente usuários com permissão `list_species` ou superusuários podem acessar."
    ),
)
def list_species(
        db_session: Session = Depends(get_db_session),
        current_user: User = Depends(require_permission_or_superuser("list_species")),
        params=Depends(pagination_params),
):
    return sqlalchemy_paginate(get_specie_query(db_session), params)


@specie_pagination_router.get(
    "/list/limit-offset",
    response_model=LimitOffsetPage[SpecieOutput],
    summary="List Species (Limit/Offset) - Listar espécies com offset",
    description=(
            "Retorna uma lista paginada de espécies usando estratégia de limit/offset.\n"
            "- Requer autenticação com token JWT do usuário.\n"
            "- Somente usuários com permissão `list_species` ou superusuários podem acessar."
    ),
)
def list_species_offset(
        db_session: Session = Depends(get_db_session),
        current_user: User = Depends(require_permission_or_superuser("list_species")),
        params=Depends(limit_offset_params),
):
    return sqlalchemy_paginate(get_specie_query(db_session), params)


# Adicionar paginação aos routers
add_pagination(pet_pagination_router)
add_pagination(specie_pagination_router)
