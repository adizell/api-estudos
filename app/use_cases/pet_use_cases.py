# app/use_cases/pet_use_cases.py
"""
Casos de uso para operações com Pets.

Este módulo contém a lógica de negócios relacionada à manipulação
de entidades Pet, integrando com o banco de dados e aplicando regras de negócio.
"""

import datetime
import secrets
import string
import uuid
import logging
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.specie_model import Specie
from app.db.models.pet_model import Pet
from app.schemas.pet_schemas import PetUpdate, PetCreate
from app.core.exceptions import (
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
    DatabaseOperationException,
    PermissionDeniedException,
    InvalidInputException
)

# Configurar logger
logger = logging.getLogger(__name__)


class PetUseCases:
    """
    Casos de uso para operações com Pets.

    Esta classe implementa toda a lógica de negócios relacionada
    à manipulação de entidades Pet, como adicionar, listar, atualizar e excluir.
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
        Busca uma espécie pelo ID e verifica se está ativa.

        Args:
            specie_id: ID da espécie

        Returns:
            Objeto Specie

        Raises:
            ResourceNotFoundException: Se a espécie não for encontrada
            InvalidInputException: Se a espécie estiver inativa
        """
        specie = self.db_session.query(Specie).filter(Specie.id == specie_id).first()
        if not specie:
            logger.warning(f"Espécie não encontrada: ID {specie_id}")
            raise ResourceNotFoundException(
                detail=f"A espécie com ID {specie_id} não existe",
                resource_id=specie_id
            )

        # Verifica se a espécie está ativa
        if not specie.is_active:
            logger.warning(f"Tentativa de usar espécie inativa: ID {specie_id}")
            raise InvalidInputException(
                detail=f"A espécie '{specie.name}' (ID: {specie_id}) está inativa e não pode ser utilizada"
            )

        return specie

    def _get_pet_by_id(self, pet_id: UUID) -> Pet:
        """
        Busca um pet pelo ID.

        Args:
            pet_id: UUID do pet

        Returns:
            Objeto Pet

        Raises:
            ResourceNotFoundException: Se o pet não for encontrado
        """
        pet = self.db_session.query(Pet).filter(Pet.id == pet_id).first()
        if not pet:
            logger.warning(f"Pet não encontrado: ID {pet_id}")
            raise ResourceNotFoundException(
                detail="Pet não encontrado",
                resource_id=pet_id
            )
        return pet

    def _generate_unique_slug(self) -> str:
        """
        Gera um slug único para o pet.

        Returns:
            String contendo o slug gerado
        """
        max_attempts = 10
        exclude_chars = "jIloO0"  # Caracteres fáceis de confundir

        for _ in range(max_attempts):
            while True:
                # Gera uma string aleatória de 7 caracteres
                slug_temp = "".join(
                    secrets.choice(string.ascii_letters + string.digits)
                    for _ in range(7)
                )
                # Remove caracteres que podem causar confusão
                slug_temp = "".join(
                    char for char in slug_temp if char not in exclude_chars
                )
                if len(slug_temp) == 7:
                    break

            # Verifica se o slug já existe
            exists = self.db_session.query(Pet).filter(Pet.slug == slug_temp).first()
            if not exists:
                return slug_temp

        # Se falhar após várias tentativas, usa um UUID
        return str(uuid.uuid4().hex)[:15]

    def verify_pet_ownership(self, pet_id: UUID, user_id: UUID) -> bool:
        """
        Verifica se o usuário é dono do pet.

        Args:
            pet_id: UUID do pet
            user_id: UUID do usuário

        Returns:
            True se o usuário for o dono, False caso contrário

        Raises:
            ResourceNotFoundException: Se o pet não for encontrado
        """
        pet = self._get_pet_by_id(pet_id)
        return pet.owner_id == user_id

    def add_pet(
            self,
            name: str,
            sex: str,
            castrated: bool,
            public: bool,
            pro: bool,
            date_birth: datetime.date,
            specie_id: int,
            owner_id: UUID,
            category_environment_id: Optional[int] = None,
            category_condition_id: Optional[int] = None,
            category_purpose_id: Optional[int] = None,
            category_habitat_id: Optional[int] = None,
            category_origin_id: Optional[int] = None,
            category_size_id: Optional[int] = None,
            category_age_id: Optional[int] = None
    ) -> Pet:
        """
        Adiciona um novo pet.

        Args:
            name: Nome do pet
            sex: Sexo do pet ('M' ou 'F')
            castrated: Indica se o pet é castrado
            public: Indica se o pet é público
            pro: Indica se o pet é profissional
            date_birth: Data de nascimento
            specie_id: ID da espécie
            owner_id: ID do dono
            category_environment_id: ID da categoria de ambiente (opcional)
            category_condition_id: ID da categoria de condição (opcional)
            category_purpose_id: ID da categoria de propósito (opcional)
            category_habitat_id: ID da categoria de habitat (opcional)
            category_origin_id: ID da categoria de origem (opcional)
            category_size_id: ID da categoria de tamanho (opcional)
            category_age_id: ID da categoria de idade (opcional)

        Returns:
            Pet criado

        Raises:
            ResourceNotFoundException: Se a espécie não existir
            DatabaseOperationException: Se houver erro ao salvar no banco
        """
        try:
            # Valida a entrada criando um objeto PetCreate
            pet_create = PetCreate(
                name=name,
                sex=sex,
                castrated=castrated,
                public=public,
                pro=pro,
                date_birth=date_birth,
                specie_id=specie_id
            )

            # Verifica se a espécie existe
            self._get_specie_by_id(pet_create.specie_id)

            # Cria o pet
            new_pet = Pet(
                name=pet_create.name,
                sex=pet_create.sex,
                castrated=pet_create.castrated,
                public=pet_create.public,
                pro=pet_create.pro,
                date_birth=pet_create.date_birth,
                specie_id=pet_create.specie_id,
                owner_id=owner_id,
                category_environment_id=category_environment_id,
                category_condition_id=category_condition_id,
                category_purpose_id=category_purpose_id,
                category_habitat_id=category_habitat_id,
                category_origin_id=category_origin_id,
                category_size_id=category_size_id,
                category_age_id=category_age_id,
            )

            # Gera o slug único
            new_pet.slug = self._generate_unique_slug()

            # Salva no banco
            self.db_session.add(new_pet)
            self.db_session.commit()
            self.db_session.refresh(new_pet)

            logger.info(f"Pet criado com sucesso: {new_pet.id} - {new_pet.name}")
            return new_pet

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Erro ao criar pet: {str(e)}")
            raise DatabaseOperationException(original_error=e)
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Erro inesperado ao criar pet: {str(e)}")
            raise

    def list_pets(self, name: Optional[str] = None, slug: Optional[str] = None,
                  specie_id: Optional[int] = None, owner_id: Optional[UUID] = None,
                  is_active: Optional[bool] = None) -> List[Pet]:
        """
        Lista pets com filtros opcionais.

        Args:
            name: Filtra por nome (parcial)
            slug: Filtra por slug exato
            specie_id: Filtra por espécie
            owner_id: Filtra por dono
            is_active: Filtra por status ativo

        Returns:
            Lista de objetos Pet
        """
        try:
            query = self.db_session.query(Pet)

            # Aplica filtros
            if slug:
                query = query.filter(Pet.slug == slug)

            if name:
                query = query.filter(Pet.name.ilike(f"%{name}%"))

            if specie_id:
                query = query.filter(Pet.specie_id == specie_id)

            if owner_id:
                query = query.filter(Pet.owner_id == owner_id)

            if is_active is not None:
                query = query.filter(Pet.is_active == is_active)

            # Executa a query
            return query.order_by(Pet.name).all()

        except SQLAlchemyError as e:
            logger.error(f"Erro ao listar pets: {str(e)}")
            raise DatabaseOperationException(original_error=e)

    def update_pet(self, id: UUID, pet_data: PetUpdate, user_id: UUID = None) -> Pet:
        """
        Atualiza um pet existente.

        Args:
            id: UUID do pet
            pet_data: Dados atualizados
            user_id: UUID do usuário que está fazendo a atualização (opcional)

        Returns:
            Pet atualizado

        Raises:
            ResourceNotFoundException: Se o pet não for encontrado
            PermissionDeniedException: Se o usuário não for o dono do pet
            InvalidInputException: Se a espécie estiver inativa
            DatabaseOperationException: Se houver erro ao salvar no banco
        """
        try:
            # Busca o pet
            existing_pet = self._get_pet_by_id(id)

            # Verifica a propriedade se um user_id for fornecido
            if user_id and existing_pet.owner_id != user_id:
                logger.warning(f"Tentativa de atualização sem permissão: Pet {id}, Usuário {user_id}")
                raise PermissionDeniedException(detail="Você não tem permissão para alterar este pet")

            # Verifica a espécie se for fornecida
            if pet_data.specie_id is not None:
                # Esta chamada já verifica se a espécie está ativa
                self._get_specie_by_id(pet_data.specie_id)

            # Atualiza os campos não nulos
            update_data = pet_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing_pet, field, value)

            # Salva no banco
            self.db_session.commit()
            self.db_session.refresh(existing_pet)

            logger.info(f"Pet atualizado com sucesso: {existing_pet.id}")
            return existing_pet

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Erro ao atualizar pet: {str(e)}")
            raise DatabaseOperationException(original_error=e)

    def delete_pet(self, id: UUID, user_id: UUID = None) -> Dict[str, str]:
        """
        Exclui um pet.

        Args:
            id: UUID do pet
            user_id: UUID do usuário que está fazendo a exclusão (opcional)

        Returns:
            Dicionário com mensagem de sucesso

        Raises:
            ResourceNotFoundException: Se o pet não for encontrado
            PermissionDeniedException: Se o usuário não for o dono do pet
            DatabaseOperationException: Se houver erro ao excluir do banco
        """
        try:
            # Busca o pet
            pet_to_delete = self._get_pet_by_id(id)

            # Verifica a propriedade se um user_id for fornecido
            if user_id and pet_to_delete.owner_id != user_id:
                logger.warning(f"Tentativa de exclusão sem permissão: Pet {id}, Usuário {user_id}")
                raise PermissionDeniedException(detail="Você não tem permissão para excluir este pet")

            # Exclui do banco
            self.db_session.delete(pet_to_delete)
            self.db_session.commit()

            logger.info(f"Pet excluído com sucesso: {id}")
            return {"message": "Pet excluído com sucesso"}

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Erro ao excluir pet: {str(e)}")
            raise DatabaseOperationException(original_error=e)

    def update_pet_categories(self, id: UUID, categories: Dict[str, Any], user_id: UUID = None) -> Pet:
        """
        Atualiza as categorias de um pet.

        Args:
            id: UUID do pet
            categories: Dicionário com as categorias a atualizar
            user_id: UUID do usuário que está fazendo a atualização (opcional)

        Returns:
            Pet atualizado

        Raises:
            ResourceNotFoundException: Se o pet não for encontrado
            PermissionDeniedException: Se o usuário não for o dono do pet
            DatabaseOperationException: Se houver erro ao salvar no banco
        """
        try:
            # Busca o pet
            pet = self._get_pet_by_id(id)

            # Verifica a propriedade se um user_id for fornecido
            if user_id and pet.owner_id != user_id:
                logger.warning(f"Tentativa de atualização sem permissão: Pet {id}, Usuário {user_id}")
                raise PermissionDeniedException(detail="Você não tem permissão para alterar este pet")

            # Atualiza as categorias
            if "category_environment_id" in categories:
                pet.category_environment_id = categories["category_environment_id"]

            if "category_condition_id" in categories:
                pet.category_condition_id = categories["category_condition_id"]

            if "category_purpose_id" in categories:
                pet.category_purpose_id = categories["category_purpose_id"]

            if "category_habitat_id" in categories:
                pet.category_habitat_id = categories["category_habitat_id"]

            if "category_origin_id" in categories:
                pet.category_origin_id = categories["category_origin_id"]

            if "category_size_id" in categories:
                pet.category_size_id = categories["category_size_id"]

            if "category_age_id" in categories:
                pet.category_age_id = categories["category_age_id"]

            # Salva no banco
            self.db_session.commit()
            self.db_session.refresh(pet)

            logger.info(f"Categorias do pet atualizadas com sucesso: {pet.id}")
            return pet

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Erro ao atualizar categorias do pet: {str(e)}")
            raise DatabaseOperationException(original_error=e)
