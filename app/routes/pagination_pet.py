# app/routes/pagination_pet.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi_pagination import Page, LimitOffsetPage, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from app.api.deps import get_db_session, get_current_user
from app.db.models.pet_model import Pet
from app.db.models.user.user_model import User
from app.schemas.pet_schemas import PetOutput
from app.utils.pagination import pagination_params, limit_offset_params
from app.security.permissions import require_permission  # ✅ permissões do usuário

router = APIRouter(
    prefix="/pag_pet",
    tags=["Pagination Pets"],
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


@router.get(
    "/list",
    response_model=Page[PetOutput],
    summary="List Pets - Listar pets do usuário",
    description=(
            "Retorna uma lista paginada de pets vinculados ao usuário autenticado.\n"
            "- Se for superusuário, retorna todos os pets.\n"
            "- Caso contrário, apenas os pets do usuário logado.\n"
            "Requer permissão 'list_pets' ou ser superusuário."
    ),
    dependencies=[Depends(require_permission("list_pets"))],  # ✅ restrição de permissão
)
def list_pets(
        db_session: Session = Depends(get_db_session),
        current_user: User = Depends(get_current_user),
        params=Depends(pagination_params),
):
    return sqlalchemy_paginate(get_pet_query(db_session, current_user), params)


@router.get(
    "/list/limit-offset",
    response_model=LimitOffsetPage[PetOutput],
    summary="List Pets (Limit-Offset) - Listar pets com limit e offset",
    description=(
            "Retorna uma lista paginada de pets vinculados ao usuário autenticado.\n"
            "- Se for superusuário, retorna todos os pets.\n"
            "- Caso contrário, apenas os pets do usuário logado.\n"
            "Requer permissão 'list_pets' ou ser superusuário."
    ),
    dependencies=[Depends(require_permission("list_pets"))],  # ✅ restrição de permissão
)
def list_pets_limit_offset(
        db_session: Session = Depends(get_db_session),
        current_user: User = Depends(get_current_user),
        params=Depends(limit_offset_params),
):
    return sqlalchemy_paginate(get_pet_query(db_session, current_user), params)


add_pagination(router)
