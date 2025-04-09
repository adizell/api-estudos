# app/routes/pagination_specie.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi_pagination import Page, LimitOffsetPage, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from app.api.deps import get_db_session
from app.security.permissions import require_permission_or_superuser
from app.db.models.specie_model import Specie
from app.db.models.user.user_model import User
from app.schemas.specie_schemas import SpecieOutput
from app.utils.pagination import pagination_params, limit_offset_params

router = APIRouter(
    prefix="/pag_specie",
    tags=["Pagination Species"]
)


# Reutilizável para as duas rotas
def get_specie_query(db: Session) -> Session.query:
    return db.query(Specie)


@router.get(
    "/list",
    response_model=Page[SpecieOutput],
    summary="List Species - Listar espécies",
    include_in_schema=False,
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


@router.get(
    "/list/limit-offset",
    response_model=LimitOffsetPage[SpecieOutput],
    summary="List Species (Limit/Offset) - Listar espécies com offset",
    include_in_schema=False,
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


add_pagination(router)
