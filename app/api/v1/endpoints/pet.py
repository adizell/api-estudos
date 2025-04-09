# app/routes/pet.py
"""
Rotas para gerenciamento de Pets.

Este módulo define os endpoints relacionados a operações com pets,
como cadastro, listagem, atualização e exclusão.
"""

import logging
from fastapi import APIRouter, Depends, status, Query, Path
from sqlalchemy.orm import Session
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from typing import Optional
from uuid import UUID

from app.api.deps import get_session, get_current_user
from app.services.pet_services import PetServices
from app.db.models.pet_model import Pet
from app.db.models.user.user_model import User
from app.security.permissions import require_permission
from app.utils.pagination import pagination_params
from app.schemas.pet_schemas import (
    PetCreate,
    PetUpdate,
    PetOutput,
)
from app.db.models.pet_category_model import (
    PetCategoryEnvironment,
    PetCategoryCondition,
    PetCategoryPurpose,
    PetCategoryHabitat,
    PetCategoryOrigin,
    PetCategorySize,
    PetCategoryAge,
)
from app.core.middleware.exceptions import (
    PermissionDeniedException,
)

# Configurar logger
logger = logging.getLogger(__name__)

# Definir o router com dependência global
router = APIRouter(
    prefix="/pet",
    tags=["Pet"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/add",
    response_model=PetOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Add Pet - Cadastrar novo pet",
    description=(
            "Cadastra um novo pet no sistema para o usuário logado. "
            "Requer autenticação via token do `user` e a permissão 'add_pet'."
    ),
)
async def add_pet(
        pet: PetCreate,
        user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("add_pet")),
        db: Session = Depends(get_session),
):
    logger.info(f"Cadastrando pet para usuário: {user.email}")
    uc = PetServices(db_session=db)
    return uc.add_pet(
        name=pet.name,
        specie_id=pet.specie_id,
        sex=pet.sex,
        castrated=pet.castrated,
        public=pet.public,
        pro=pet.pro,
        date_birth=pet.date_birth,
        owner_id=user.id,
        category_environment_id=pet.category_environment_id,
        category_condition_id=pet.category_condition_id,
        category_purpose_id=pet.category_purpose_id,
        category_habitat_id=pet.category_habitat_id,
        category_origin_id=pet.category_origin_id,
        category_size_id=pet.category_size_id,
        category_age_id=pet.category_age_id,
    )


@router.get(
    "/list",
    response_model=Page[PetOutput],
    status_code=status.HTTP_200_OK,
    summary="List Pets - Listar pets do usuário",
    description=(
            "Lista os pets cadastrados pelo usuário autenticado. "
            "Requer autenticação via token do `user` e permissão 'list_pets'. "
            "Retorna os resultados paginados."
    ),
)
async def list_user_pets(
        name: Optional[str] = Query(None, description="Filtrar por nome (parcial)"),
        specie_id: Optional[int] = Query(None, description="Filtrar por espécie"),
        is_active: Optional[bool] = Query(None, description="Filtrar por status"),
        db_session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("list_pets")),
        params=Depends(pagination_params),
):
    """
    Lista os pets do usuário autenticado com paginação.

    Args:
        name: Filtro opcional por nome
        specie_id: Filtro opcional por espécie
        is_active: Filtro opcional por status
        db_session: Sessão do banco de dados (injetada)
        user: Usuário autenticado (injetado)
        _: Flag de verificação de permissão (injetado)
        params: Parâmetros de paginação (injetado)

    Returns:
        Página de pets do usuário
    """
    logger.info(f"Listando pets para usuário: {user.email}")

    # Constrói a query base
    query = db_session.query(Pet).filter(Pet.owner_id == user.id)

    # Aplica filtros
    if name:
        query = query.filter(Pet.name.ilike(f"%{name}%"))

    if specie_id:
        query = query.filter(Pet.specie_id == specie_id)

    if is_active is not None:
        query = query.filter(Pet.is_active == is_active)

    # Aplica a paginação e retorna o resultado
    return sqlalchemy_paginate(query.order_by(Pet.name), params)


@router.get(
    "/categories",
    summary="Get Pet Categories - Obter todas as categorias de pet",
    description="Retorna todas as categorias ativas para seleção no cadastro de pet.",
)
async def get_pet_categories(
        db_session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("list_pets"))
):
    # Buscar todas as categorias ativas de cada tipo
    environment_categories = db_session.query(PetCategoryEnvironment).filter(
        PetCategoryEnvironment.is_active == True).all()
    condition_categories = db_session.query(PetCategoryCondition).filter(PetCategoryCondition.is_active == True).all()
    purpose_categories = db_session.query(PetCategoryPurpose).filter(PetCategoryPurpose.is_active == True).all()
    habitat_categories = db_session.query(PetCategoryHabitat).filter(PetCategoryHabitat.is_active == True).all()
    origin_categories = db_session.query(PetCategoryOrigin).filter(PetCategoryOrigin.is_active == True).all()
    size_categories = db_session.query(PetCategorySize).filter(PetCategorySize.is_active == True).all()
    age_categories = db_session.query(PetCategoryAge).filter(PetCategoryAge.is_active == True).all()

    # Converter para dicionários básicos com id e nome
    def to_dict_list(categories):
        return [{"id": cat.id, "name": cat.name} for cat in categories]

    return {
        "environment": to_dict_list(environment_categories),
        "condition": to_dict_list(condition_categories),
        "purpose": to_dict_list(purpose_categories),
        "habitat": to_dict_list(habitat_categories),
        "origin": to_dict_list(origin_categories),
        "size": to_dict_list(size_categories),
        "age": to_dict_list(age_categories),
    }


@router.get(
    "/{pet_id}",
    response_model=PetOutput,
    status_code=status.HTTP_200_OK,
    summary="Get Pet - Obter detalhes de um pet",
    description=(
            "Obtém detalhes de um pet específico pelo ID. "
            "Requer autenticação via token do `user` e permissão 'list_pets'. "
            "O usuário só pode visualizar seus próprios pets, a menos que seja superusuário."
    ),
)
async def get_pet_by_id(
        pet_id: UUID = Path(..., description="ID do pet"),
        db_session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("list_pets")),
):
    """
    Obtém os detalhes de um pet específico pelo ID.

    Args:
        pet_id: ID do pet
        db_session: Sessão do banco de dados (injetada)
        user: Usuário autenticado (injetado)
        _: Flag de verificação de permissão (injetado)

    Returns:
        Detalhes do pet

    Raises:
        ResourceNotFoundException: Se o pet não for encontrado
        PermissionDeniedException: Se o usuário não for o dono do pet (a menos que seja superusuário)
    """
    logger.info(f"Obtendo pet {pet_id} para usuário: {user.email}")
    uc = PetServices(db_session=db_session)
    pet = uc._get_pet_by_id(pet_id)

    # Verifica se o usuário tem acesso a este pet
    if not user.is_superuser and pet.owner_id != user.id:
        logger.warning(f"Usuário {user.email} tentou acessar pet {pet_id} que não lhe pertence")
        raise PermissionDeniedException(detail="Você não tem permissão para visualizar este pet")

    return pet


@router.put(
    "/{pet_id}",
    response_model=PetOutput,
    status_code=status.HTTP_200_OK,
    summary="Update Pet - Atualizar pet",
    description=(
            "Atualiza os dados de um pet específico, desde que ele pertença ao usuário autenticado. "
            "Requer autenticação via token do `user` e permissão 'update_pet'."
    ),
)
async def update_pet(
        pet_id: UUID = Path(..., description="ID do pet"),
        pet_input: PetUpdate = None,
        current_user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("update_pet")),
        db_session: Session = Depends(get_session),
):
    """
    Atualiza os dados de um pet específico.

    Args:
        pet_id: ID do pet
        pet_input: Dados a serem atualizados
        current_user: Usuário autenticado (injetado)
        _: Flag de verificação de permissão (injetado)
        db_session: Sessão do banco de dados (injetada)

    Returns:
        Pet atualizado

    Raises:
        ResourceNotFoundException: Se o pet não for encontrado
        PermissionDeniedException: Se o usuário não for o dono do pet
        DatabaseOperationException: Se houver erro ao salvar no banco
    """
    logger.info(f"Atualizando pet {pet_id} para usuário: {current_user.email}")
    pet_uc = PetServices(db_session=db_session)
    return pet_uc.update_pet(pet_id, pet_input, current_user.id)


@router.delete(
    "/{pet_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Pet - Remover pet",
    description=(
            "Remove um pet do sistema, desde que pertença ao usuário autenticado. "
            "Requer autenticação via token do `user` e permissão 'delete_pet'."
    ),
)
async def delete_pet(
        pet_id: UUID = Path(..., description="ID do pet"),
        current_user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("delete_pet")),
        db_session: Session = Depends(get_session),
):
    """
    Remove um pet do sistema.

    Args:
        pet_id: ID do pet
        current_user: Usuário autenticado (injetado)
        _: Flag de verificação de permissão (injetado)
        db_session: Sessão do banco de dados (injetada)

    Returns:
        Mensagem de sucesso

    Raises:
        ResourceNotFoundException: Se o pet não for encontrado
        PermissionDeniedException: Se o usuário não for o dono do pet
        DatabaseOperationException: Se houver erro ao excluir do banco
    """
    logger.info(f"Excluindo pet {pet_id} para usuário: {current_user.email}")
    pet_uc = PetServices(db_session=db_session)
    return pet_uc.delete_pet(pet_id, current_user.id)


@router.patch(
    "/{pet_id}/categories",
    response_model=PetOutput,
    status_code=status.HTTP_200_OK,
    summary="Update Pet Categories - Atualizar categorias do pet",
    description=(
            "Atualiza as categorias de um pet específico, desde que ele pertença ao usuário autenticado. "
            "Requer autenticação via token do `user` e permissão 'update_pet'."
    ),
)
async def update_pet_categories(
        pet_id: UUID = Path(..., description="ID do pet"),
        category_environment_id: Optional[int] = Query(None, description="ID da categoria de ambiente"),
        category_condition_id: Optional[int] = Query(None, description="ID da categoria de condição"),
        category_purpose_id: Optional[int] = Query(None, description="ID da categoria de propósito"),
        category_habitat_id: Optional[int] = Query(None, description="ID da categoria de habitat"),
        category_origin_id: Optional[int] = Query(None, description="ID da categoria de origem"),
        category_size_id: Optional[int] = Query(None, description="ID da categoria de tamanho"),
        category_age_id: Optional[int] = Query(None, description="ID da categoria de idade"),
        current_user: User = Depends(get_current_user),
        _: bool = Depends(require_permission("update_pet")),
        db_session: Session = Depends(get_session),
):
    """
    Atualiza as categorias de um pet específico.

    Args:
        pet_id: ID do pet
        category_environment_id: ID da categoria de ambiente
        category_condition_id: ID da categoria de condição
        category_purpose_id: ID da categoria de propósito
        category_habitat_id: ID da categoria de habitat
        category_origin_id: ID da categoria de origem
        category_size_id: ID da categoria de tamanho
        category_age_id: ID da categoria de idade
        current_user: Usuário autenticado (injetado)
        _: Flag de verificação de permissão (injetado)
        db_session: Sessão do banco de dados (injetada)

    Returns:
        Pet atualizado

    Raises:
        ResourceNotFoundException: Se o pet não for encontrado
        PermissionDeniedException: Se o usuário não for o dono do pet
        DatabaseOperationException: Se houver erro ao salvar no banco
    """
    logger.info(f"Atualizando categorias do pet {pet_id} para usuário: {current_user.email}")
    pet_uc = PetServices(db_session=db_session)

    # Constrói o dicionário de categorias com os valores não nulos
    categories = {}
    if category_environment_id is not None:
        categories["category_environment_id"] = category_environment_id
    if category_condition_id is not None:
        categories["category_condition_id"] = category_condition_id
    if category_purpose_id is not None:
        categories["category_purpose_id"] = category_purpose_id
    if category_habitat_id is not None:
        categories["category_habitat_id"] = category_habitat_id
    if category_origin_id is not None:
        categories["category_origin_id"] = category_origin_id
    if category_size_id is not None:
        categories["category_size_id"] = category_size_id
    if category_age_id is not None:
        categories["category_age_id"] = category_age_id

    return pet_uc.update_pet_categories(pet_id, categories, current_user.id)


# Habilitar a paginação automática
add_pagination(router)
