# app/routes/specie.py
"""
Rotas para gerenciamento de Espécies.

Este módulo define os endpoints relacionados a operações com espécies,
como cadastro, listagem, atualização e exclusão.
"""

import logging
from fastapi import APIRouter, Depends, status, Query, Path, Body
from sqlalchemy.orm import Session
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from typing import Optional

from app.api.deps import get_session, get_current_user
from app.services.specie_service import SpecieService
from app.db.models.user.user_model import User
from app.db.models.specie_model import Specie
from app.security.permissions import require_permission
from app.utils.pagination import pagination_params
from app.core.config import settings
from app.schemas.specie_schemas import (
    SpecieCreate,
    SpecieOutput,
    SpecieUpdate,
    SpecieStatusUpdate,
)

# Configurar logger
logger = logging.getLogger(__name__)

# Definir o router com dependência global
router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post(
    "/add",
    include_in_schema=settings.SCHEMA_VISIBILITY,
    response_model=SpecieOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Add Specie - Adicionar nova espécie",
    description=(
            "Adiciona uma nova espécie ao sistema. "
            "Requer autenticação via token do `user` e permissão 'add_specie'."
    ),
)
async def add_specie(
        specie: SpecieCreate,
        current_user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("add_specie")),
        db_session: Session = Depends(get_session),
):
    """
    Adiciona uma nova espécie ao sistema.

    Args:
        specie: Dados da espécie a ser cadastrada
        current_user: Usuário autenticado (injetado)
        _: Flag de verificação de permissão (injetado)
        db_session: Sessão do banco de dados (injetada)

    Returns:
        A espécie cadastrada

    Raises:
        ResourceAlreadyExistsException: Se já existir uma espécie com o mesmo nome/slug
        DatabaseOperationException: Se houver erro ao salvar no banco
    """
    logger.info(f"Cadastrando espécie por usuário: {current_user.email}")
    uc = SpecieService(db_session)
    return uc.add_specie(specie_input=specie)


@router.get(
    "/list",
    response_model=Page[SpecieOutput],
    status_code=status.HTTP_200_OK,
    summary="List Species - Listar espécies cadastradas",
    description=(
            "Lista todas as espécies registradas no sistema com suporte à paginação. "
            "Requer autenticação via token do `user` e permissão 'list_species'."
    ),
)
async def list_species(
        name: Optional[str] = Query(None, description="Filtrar por nome (parcial)"),
        is_active: Optional[bool] = Query(None, description="Filtrar por status ativo/inativo"),
        db_session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("list_species")),
        params=Depends(pagination_params),
):
    """
    Lista espécies com paginação e filtros opcionais.

    Args:
        name: Filtro opcional por nome
        is_active: Filtro opcional por status ativo
        db_session: Sessão do banco de dados (injetada)
        current_user: Usuário autenticado (injetado)
        _: Flag de verificação de permissão (injetado)
        params: Parâmetros de paginação (injetado)

    Returns:
        Página de espécies
    """
    logger.info(f"Listando espécies para usuário: {current_user.email}")

    # Constrói a query base
    query = db_session.query(Specie)

    # Aplica filtros
    if name:
        query = query.filter(Specie.name.ilike(f"%{name}%"))

    if is_active is not None:
        query = query.filter(Specie.is_active == is_active)

    # Aplica a paginação e retorna o resultado
    return sqlalchemy_paginate(query.order_by(Specie.name), params)


@router.get(
    "/{specie_id}",
    response_model=SpecieOutput,
    status_code=status.HTTP_200_OK,
    summary="Get Specie - Obter detalhes de uma espécie",
    description=(
            "Obtém detalhes de uma espécie específica pelo ID. "
            "Requer autenticação via token do `user` e permissão 'list_species'."
    ),
)
async def get_specie_by_id(
        specie_id: int = Path(..., description="ID da espécie", gt=0),
        db_session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("list_species")),
):
    """
    Obtém os detalhes de uma espécie específica pelo ID.

    Args:
        specie_id: ID da espécie
        db_session: Sessão do banco de dados (injetada)
        current_user: Usuário autenticado (injetado)
        _: Flag de verificação de permissão (injetado)

    Returns:
        Detalhes da espécie

    Raises:
        ResourceNotFoundException: Se a espécie não for encontrada
    """
    logger.info(f"Obtendo espécie {specie_id} para usuário: {current_user.email}")
    uc = SpecieService(db_session)
    return uc._get_specie_by_id(specie_id)


@router.put(
    "/{specie_id}",
    include_in_schema=settings.SCHEMA_VISIBILITY,
    response_model=SpecieOutput,
    status_code=status.HTTP_200_OK,
    summary="Update Specie - Atualizar espécie",
    description=(
            "Atualiza os dados de uma espécie existente. "
            "Requer autenticação via token do `user` e permissão 'update_specie'."
    ),
)
async def update_specie(
        specie_id: int = Path(..., description="ID da espécie", gt=0),
        specie_input: SpecieUpdate = None,
        current_user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("update_specie")),
        db_session: Session = Depends(get_session),
):
    """
    Atualiza os dados de uma espécie existente.

    Args:
        specie_id: ID da espécie
        specie_input: Dados a serem atualizados
        current_user: Usuário autenticado (injetado)
        _: Flag de verificação de permissão (injetado)
        db_session: Sessão do banco de dados (injetada)

    Returns:
        Espécie atualizada

    Raises:
        ResourceNotFoundException: Se a espécie não for encontrada
        ResourceAlreadyExistsException: Se o novo nome/slug já existir
        DatabaseOperationException: Se houver erro ao salvar no banco
    """
    logger.info(f"Atualizando espécie {specie_id} por usuário: {current_user.email}")
    uc = SpecieService(db_session)
    return uc.update_specie(specie_id, specie_input)


@router.patch(
    "/{specie_id}/status",
    include_in_schema=settings.SCHEMA_VISIBILITY,
    response_model=SpecieOutput,
    status_code=status.HTTP_200_OK,
    summary="Toggle Specie Status - Ativar/Desativar espécie",
    description=(
            "Ativa ou desativa uma espécie existente. "
            "Requer autenticação via token do `user` e permissão 'update_specie'."
    ),
)
async def toggle_specie_status(
        specie_id: int = Path(..., description="ID da espécie", gt=0),
        status_data: SpecieStatusUpdate = Body(..., description="Status desejado"),
        current_user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("update_specie")),
        db_session: Session = Depends(get_session),
):
    """
    Ativa ou desativa uma espécie.

    Args:
        specie_id: ID da espécie
        status_data: Dados do status (ativo/inativo)
        current_user: Usuário autenticado (injetado)
        _: Flag de verificação de permissão (injetado)
        db_session: Sessão do banco de dados (injetada)

    Returns:
        Espécie atualizada

    Raises:
        ResourceNotFoundException: Se a espécie não for encontrada
        DatabaseOperationException: Se houver erro ao salvar no banco
    """
    action = "ativando" if status_data.is_active else "desativando"
    logger.info(f"{action} espécie {specie_id} por usuário: {current_user.email}")
    uc = SpecieService(db_session)
    return uc.toggle_specie_status(specie_id, status_data.is_active)


@router.delete(
    "/{specie_id}",
    include_in_schema=settings.SCHEMA_VISIBILITY,
    status_code=status.HTTP_200_OK,
    summary="Delete Specie - Remover espécie",
    description=(
            "Remove uma espécie do sistema. "
            "Requer autenticação via token do `user` e permissão 'delete_specie'. "
            "A espécie só pode ser removida se não estiver associada a nenhum pet."
    ),
)
async def delete_specie(
        specie_id: int = Path(..., description="ID da espécie", gt=0),
        current_user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("delete_specie")),
        db_session: Session = Depends(get_session),
):
    """
    Remove uma espécie do sistema.

    Args:
        specie_id: ID da espécie
        current_user: Usuário autenticado (injetado)
        _: Flag de verificação de permissão (injetado)
        db_session: Sessão do banco de dados (injetada)

    Returns:
        Mensagem de sucesso

    Raises:
        ResourceNotFoundException: Se a espécie não for encontrada
        DatabaseOperationException: Se houver erro ao excluir do banco ou
                                    se houver pets associados à espécie
    """
    logger.info(f"Excluindo espécie {specie_id} por usuário: {current_user.email}")
    uc = SpecieService(db_session)
    return uc.delete_specie(specie_id)


# Habilitar a paginação automática
add_pagination(router)
