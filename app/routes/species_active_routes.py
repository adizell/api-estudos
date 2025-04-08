# app/routes/species_active_routes.py
"""
Rotas para consulta de espécies ativas.

Este módulo define endpoints simplificados para obter espécies ativas
que podem ser usadas em formulários de cadastro/edição de pets.
"""

import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.routes.deps import get_session, get_current_user
from app.db.models.user.user_model import User
from app.security.permissions import require_permission
from app.schemas.specie_schemas import SpecieOutput
from app.use_cases.specie_use_cases import SpecieUseCases

# Configurar logger
logger = logging.getLogger(__name__)

# Definir o router com dependência global
router = APIRouter(
    prefix="/active-species",
    tags=["Active Species"],
    dependencies=[Depends(get_current_user)]
)


@router.get(
    "/",
    response_model=List[SpecieOutput],
    status_code=status.HTTP_200_OK,
    summary="List Active Species - Listar espécies ativas para seleção",
    description=(
            "Lista todas as espécies ativas registradas no sistema. "
            "Útil para povoar dropdowns de seleção. "
            "Requer autenticação via token do `user` e permissão 'list_species'."
    ),
)
async def list_active_species(
        db_session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("list_species")),
):
    """
    Lista espécies ativas para seleção em formulários.

    Args:
        db_session: Sessão do banco de dados (injetada)
        current_user: Usuário autenticado (injetado)
        _: Flag de verificação de permissão (injetado)

    Returns:
        Lista de espécies ativas ordenadas por nome
    """
    logger.info(f"Listando espécies ativas para usuário: {current_user.email}")
    uc = SpecieUseCases(db_session)
    # Filtra apenas espécies ativas
    return uc.list_species(is_active=True)
