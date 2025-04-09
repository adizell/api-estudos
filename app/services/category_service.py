# app/services/category_service.py
"""
Serviço para gerenciamento de categorias.

Este módulo implementa o serviço para operações com diferentes tipos de categorias,
como Ambiente, Condição, Propósito, etc.
"""

import logging
from slugify import slugify
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Type, Dict, Any, Optional, List

from app.db.models.pet_category_model import PetCategoryBase
from app.schemas.category_schemas import CategoryCreate, CategoryUpdate
from app.core.exceptions import (
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
    DatabaseOperationException,
)

# Configurar logger
logger = logging.getLogger(__name__)


class CategoryService:
    """
    Serviço para gerenciamento de categorias.

    Esta classe implementa operações CRUD para diferentes tipos de categorias
    de pets (ambiente, condição, propósito, etc).
    """

    def __init__(self, db_session: Session, model_class: Type[PetCategoryBase]):
        """
        Inicializa o serviço com uma sessão de banco de dados e a classe do modelo.

        Args:
            db_session: Sessão SQLAlchemy ativa
            model_class: Classe do modelo de categoria
        """
        self.db_session = db_session
        self.model_class = model_class
        self.model_name = model_class.__tablename__.replace('pet_category_', '').capitalize()

    def _get_by_id(self, category_id: int) -> PetCategoryBase:
        """
        Obtém uma categoria pelo ID.

        Args:
            category_id: ID da categoria

        Returns:
            Objeto de categoria

        Raises:
            ResourceNotFoundException: Se a categoria não existir
        """
        category = self.db_session.query(self.model_class).filter(
            self.model_class.id == category_id
        ).first()

        if not category:
            error_msg = f"Categoria {self.model_name} com ID {category_id} não encontrada"
            logger.warning(error_msg)
            raise ResourceNotFoundException(detail=error_msg, resource_id=category_id)

        return category

    def create_category(self, data: CategoryCreate) -> PetCategoryBase:
        """
        Cria uma nova categoria.

        Args:
            data: Dados da categoria

        Returns:
            Nova categoria criada

        Raises:
            ResourceAlreadyExistsException: Se já existir categoria com mesmo nome/slug
            DatabaseOperationException: Em caso de erro no banco de dados
        """
        try:
            # Gera o slug a partir do nome
            slug = slugify(data.name)

            # Verifica se já existe categoria com este nome ou slug
            existing = self.db_session.query(self.model_class).filter(
                (self.model_class.name == data.name) | (self.model_class.slug == slug)
            ).first()

            if existing:
                error_msg = f"Categoria com nome '{data.name}' ou slug '{slug}' já existe"
                logger.warning(error_msg)
                raise ResourceAlreadyExistsException(detail=error_msg)

            # Cria nova categoria
            new_category = self.model_class(name=data.name, slug=slug)
            self.db_session.add(new_category)
            self.db_session.commit()
            self.db_session.refresh(new_category)

            logger.info(f"Categoria {self.model_name} criada: {new_category.name} (ID: {new_category.id})")
            return new_category

        except IntegrityError as e:
            self.db_session.rollback()
            error_msg = f"Erro de integridade ao criar categoria {self.model_name}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseOperationException(detail=error_msg, original_error=e)

        except ResourceAlreadyExistsException:
            self.db_session.rollback()
            raise

        except Exception as e:
            self.db_session.rollback()
            error_msg = f"Erro inesperado ao criar categoria {self.model_name}: {str(e)}"
            logger.exception(error_msg)
            raise DatabaseOperationException(detail=error_msg, original_error=e)

    def list_categories(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> Dict[str, Any]:
        """
        Lista categorias com filtros opcionais.

        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            is_active: Filtro opcional por status ativo

        Returns:
            Dicionário com itens e contagem total

        Raises:
            DatabaseOperationException: Em caso de erro no banco de dados
        """
        try:
            query = self.db_session.query(self.model_class)

            # Aplica filtros
            if is_active is not None:
                query = query.filter(self.model_class.is_active == is_active)

            # Calcula o total para paginação
            total = query.count()

            # Aplica paginação
            items = query.order_by(self.model_class.name).offset(skip).limit(limit).all()

            return {
                "items": items,
                "total": total
            }

        except Exception as e:
            error_msg = f"Erro ao listar categorias {self.model_name}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseOperationException(detail=error_msg, original_error=e)

    def update_category(self, category_id: int, data: CategoryUpdate) -> PetCategoryBase:
        """
        Atualiza uma categoria existente.

        Args:
            category_id: ID da categoria
            data: Dados atualizados

        Returns:
            Categoria atualizada

        Raises:
            ResourceNotFoundException: Se a categoria não existir
            ResourceAlreadyExistsException: Se o novo nome/slug já existir
            DatabaseOperationException: Em caso de erro no banco de dados
        """
        try:
            category = self._get_by_id(category_id)

            if data.name is not None and data.name != category.name:
                # Gera novo slug
                new_slug = slugify(data.name)

                # Verifica se já existe outra categoria com este nome ou slug
                existing = self.db_session.query(self.model_class).filter(
                    ((self.model_class.name == data.name) | (self.model_class.slug == new_slug)) &
                    (self.model_class.id != category_id)
                ).first()

                if existing:
                    error_msg = f"Categoria com nome '{data.name}' ou slug '{new_slug}' já existe"
                    logger.warning(error_msg)
                    raise ResourceAlreadyExistsException(detail=error_msg)

                # Atualiza nome e slug
                category.name = data.name
                category.slug = new_slug

            self.db_session.commit()
            self.db_session.refresh(category)

            logger.info(f"Categoria {self.model_name} atualizada: ID {category_id}")
            return category

        except IntegrityError as e:
            self.db_session.rollback()
            error_msg = f"Erro de integridade ao atualizar categoria {self.model_name}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseOperationException(detail=error_msg, original_error=e)

        except (ResourceNotFoundException, ResourceAlreadyExistsException):
            self.db_session.rollback()
            raise

        except Exception as e:
            self.db_session.rollback()
            error_msg = f"Erro inesperado ao atualizar categoria {self.model_name}: {str(e)}"
            logger.exception(error_msg)
            raise DatabaseOperationException(detail=error_msg, original_error=e)

    def delete_category(self, category_id: int) -> Dict[str, str]:
        """
        Remove uma categoria.

        Args:
            category_id: ID da categoria

        Returns:
            Mensagem de sucesso

        Raises:
            ResourceNotFoundException: Se a categoria não existir
            DatabaseOperationException: Se houver erro no banco de dados
                                       ou se a categoria estiver sendo referenciada
        """
        try:
            category = self._get_by_id(category_id)

            self.db_session.delete(category)
            self.db_session.commit()

            logger.info(f"Categoria {self.model_name} excluída: ID {category_id}")
            return {"message": f"Categoria {self.model_name} com ID {category_id} excluída com sucesso"}

        except IntegrityError as e:
            self.db_session.rollback()
            error_msg = (
                f"Não é possível excluir a categoria pois ela está sendo referenciada por outros registros: {str(e)}"
            )
            logger.error(error_msg)
            raise DatabaseOperationException(detail=error_msg, original_error=e)

        except ResourceNotFoundException:
            self.db_session.rollback()
            raise

        except Exception as e:
            self.db_session.rollback()
            error_msg = f"Erro inesperado ao excluir categoria {self.model_name}: {str(e)}"
            logger.exception(error_msg)
            raise DatabaseOperationException(detail=error_msg, original_error=e)

    def toggle_status(self, category_id: int, active: bool) -> PetCategoryBase:
        """
        Ativa ou desativa uma categoria.

        Args:
            category_id: ID da categoria
            active: Status desejado (True = ativo, False = inativo)

        Returns:
            Categoria atualizada

        Raises:
            ResourceNotFoundException: Se a categoria não existir
            DatabaseOperationException: Em caso de erro no banco de dados
        """
        try:
            category = self._get_by_id(category_id)

            # Atualiza o status
            category.is_active = active
            self.db_session.commit()
            self.db_session.refresh(category)

            status_text = "ativada" if active else "desativada"
            logger.info(f"Categoria {self.model_name} {category_id} {status_text}")
            return category

        except ResourceNotFoundException:
            self.db_session.rollback()
            raise

        except Exception as e:
            self.db_session.rollback()
            error_msg = f"Erro inesperado ao alterar status da categoria {self.model_name}: {str(e)}"
            logger.exception(error_msg)
            raise DatabaseOperationException(detail=error_msg, original_error=e)
