# app/services/specie_services.py
"""
Casos de uso para operações com Espécies.

Este módulo contém a lógica de negócios relacionada à manipulação
de entidades Specie, integrando com o banco de dados e aplicando regras de negócio.
"""

import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.utils.input_validation import validate_and_sanitize_slug, InputValidator

from app.db.models.specie_model import Specie
from app.schemas.specie_schemas import SpecieCreate, SpecieUpdate
from app.core.middleware.exceptions import (
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
    DatabaseOperationException,
    InvalidInputException
)

# Configurar logger
logger = logging.getLogger(__name__)


class SpecieServices:
    """
    Casos de uso para operações com Espécies.

    Esta classe implementa toda a lógica de negócios relacionada
    à manipulação de entidades Specie, como adicionar, listar, atualizar e excluir.
    """

    def __init__(self, db_session: Session):
        """
        Inicializa o caso de uso com uma sessão de banco de dados.

        Args:
            db_session: Sessão SQLAlchemy ativa
        """
        self.db_session = db_session

    def _get_specie_by_id(self, specie_id: int) -> Specie:
        """
        Busca uma espécie pelo ID.

        Args:
            specie_id: ID da espécie

        Returns:
            Objeto Specie

        Raises:
            ResourceNotFoundException: Se a espécie não for encontrada
        """
        specie = self.db_session.query(Specie).filter(Specie.id == specie_id).first()
        if not specie:
            logger.warning(f"Espécie não encontrada: ID {specie_id}")
            raise ResourceNotFoundException(
                detail="Espécie não encontrada",
                resource_id=specie_id
            )
        return specie

    def _generate_slug_from_name(self, name: str) -> str:
        """
        Gera um slug a partir do nome da espécie.

        Args:
            name: Nome da espécie

        Returns:
            Slug gerado
        """
        # Usa o validador de slug para garantir segurança
        return validate_and_sanitize_slug(name)

    def list_species(self, name: Optional[str] = None, is_active: Optional[bool] = None) -> List[Specie]:
        """
        Lista espécies com filtros opcionais.

        Args:
            name: Filtra por nome (parcial)
            is_active: Filtra por status ativo

        Returns:
            Lista de objetos Specie

        Raises:
            DatabaseOperationException: Se houver erro ao consultar o banco
        """
        try:
            query = self.db_session.query(Specie)

            # Aplica filtros
            if name:
                query = query.filter(Specie.name.ilike(f"%{name}%"))

            if is_active is not None:
                query = query.filter(Specie.is_active == is_active)

            # Executa a query
            return query.order_by(Specie.name).all()

        except SQLAlchemyError as e:
            logger.error(f"Erro ao listar espécies: {str(e)}")
            raise DatabaseOperationException(original_error=e)

    def add_specie(self, specie_input: SpecieCreate) -> Specie:
        """
        Adiciona uma nova espécie.

        Args:
            specie_input: Dados da espécie

        Returns:
            Espécie criada

        Raises:
            ResourceAlreadyExistsException: Se já existir uma espécie com o mesmo nome/slug
            DatabaseOperationException: Se houver erro ao salvar no banco
            InvalidInputException: Se os dados de entrada forem inválidos
        """
        try:
            # Sanitiza o nome e valida
            sanitized_name = InputValidator.sanitize_name(specie_input.name)
            is_valid, error_msg = InputValidator.validate_name(sanitized_name)

            if not is_valid:
                logger.warning(f"Tentativa de criar espécie com nome inválido: {specie_input.name}")
                raise InvalidInputException(detail=error_msg)

            # Gera o slug usando a função de validação mais segura
            slug = validate_and_sanitize_slug(sanitized_name)

            # Verifica se já existe uma espécie com o mesmo nome ou slug
            existing = (
                self.db_session.query(Specie)
                .filter((Specie.name == sanitized_name) | (Specie.slug == slug))
                .first()
            )

            if existing:
                logger.warning(f"Tentativa de criar espécie duplicada: {sanitized_name}")
                raise ResourceAlreadyExistsException(
                    detail=f"Já existe uma espécie com nome '{sanitized_name}' ou slug '{slug}'"
                )

            # Cria a espécie com o nome sanitizado
            new_specie = Specie(name=sanitized_name, slug=slug, is_active=True)
            self.db_session.add(new_specie)
            self.db_session.commit()
            self.db_session.refresh(new_specie)

            logger.info(f"Espécie criada com sucesso: {new_specie.id} - {new_specie.name}")
            return new_specie

        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"Erro de integridade ao criar espécie: {str(e)}")
            raise ResourceAlreadyExistsException(
                detail=f"Já existe uma espécie com esse nome ou slug"
            )
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Erro ao criar espécie: {str(e)}")
            raise DatabaseOperationException(original_error=e)
        except InvalidInputException:
            # Repassa a exceção
            self.db_session.rollback()
            raise
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Erro inesperado ao criar espécie: {str(e)}")
            raise

    def update_specie(self, specie_id: int, specie_input: SpecieUpdate) -> Specie:
        """
        Atualiza uma espécie existente.

        Args:
            specie_id: ID da espécie
            specie_input: Dados atualizados

        Returns:
            Espécie atualizada

        Raises:
            ResourceNotFoundException: Se a espécie não for encontrada
            ResourceAlreadyExistsException: Se o novo nome/slug já existir
            DatabaseOperationException: Se houver erro ao salvar no banco
        """
        try:
            # Busca a espécie
            specie = self._get_specie_by_id(specie_id)

            # Se o nome foi fornecido, atualiza o nome e o slug
            if specie_input.name:
                # Gera o novo slug
                new_slug = self._generate_slug_from_name(specie_input.name)

                # Verifica se já existe outra espécie com o mesmo nome ou slug
                existing = (
                    self.db_session.query(Specie)
                    .filter(
                        ((Specie.name == specie_input.name) | (Specie.slug == new_slug))
                        & (Specie.id != specie_id)
                    )
                    .first()
                )

                if existing:
                    logger.warning(f"Tentativa de atualizar espécie para nome/slug duplicado: {specie_input.name}")
                    raise ResourceAlreadyExistsException(
                        detail=f"Já existe uma espécie com nome '{specie_input.name}' ou slug '{new_slug}'"
                    )

                # Atualiza o nome e o slug
                specie.name = specie_input.name
                specie.slug = new_slug

            # Salva no banco
            self.db_session.commit()
            self.db_session.refresh(specie)

            logger.info(f"Espécie atualizada com sucesso: {specie.id}")
            return specie

        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"Erro de integridade ao atualizar espécie: {str(e)}")
            raise ResourceAlreadyExistsException(
                detail=f"Já existe uma espécie com esse nome ou slug"
            )
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Erro ao atualizar espécie: {str(e)}")
            raise DatabaseOperationException(original_error=e)

    def toggle_specie_status(self, specie_id: int, active: bool) -> Specie:
        """
        Ativa ou desativa uma espécie.

        Args:
            specie_id: ID da espécie
            active: Status desejado (True para ativo, False para inativo)

        Returns:
            Espécie atualizada

        Raises:
            ResourceNotFoundException: Se a espécie não for encontrada
            DatabaseOperationException: Se houver erro ao salvar no banco
        """
        try:
            # Busca a espécie
            specie = self._get_specie_by_id(specie_id)

            # Verifica se o status já é o desejado
            if specie.is_active == active:
                logger.info(f"Espécie {specie_id} já está com status is_active={active}")
                return specie

            # Atualiza o status
            specie.is_active = active
            self.db_session.commit()
            self.db_session.refresh(specie)

            status_text = "ativada" if active else "desativada"
            logger.info(f"Espécie {specie_id} {status_text} com sucesso")
            return specie

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Erro ao atualizar status da espécie: {str(e)}")
            raise DatabaseOperationException(original_error=e)

    def delete_specie(self, specie_id: int) -> Dict[str, str]:
        """
        Exclui uma espécie.

        Args:
            specie_id: ID da espécie

        Returns:
            Dicionário com mensagem de sucesso

        Raises:
            ResourceNotFoundException: Se a espécie não for encontrada
            DatabaseOperationException: Se houver erro ao excluir do banco ou
                                        se houver pets associados à espécie
        """
        try:
            # Busca a espécie
            specie = self._get_specie_by_id(specie_id)

            # Verifica se há pets associados
            if specie.pets and len(specie.pets) > 0:
                logger.warning(f"Tentativa de excluir espécie com pets associados: {specie_id}")
                raise DatabaseOperationException(
                    detail=f"Não é possível excluir a espécie pois existem {len(specie.pets)} pets associados a ela"
                )

            # Exclui a espécie
            self.db_session.delete(specie)
            self.db_session.commit()

            logger.info(f"Espécie excluída com sucesso: {specie_id}")
            return {"message": "Espécie excluída com sucesso"}

        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"Erro de integridade ao excluir espécie: {str(e)}")
            raise DatabaseOperationException(
                detail="Não é possível excluir a espécie pois ela está sendo referenciada por outros registros"
            )
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Erro ao excluir espécie: {str(e)}")
            raise DatabaseOperationException(original_error=e)
