# app/use_cases/user_use_cases.py

from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.hash import bcrypt
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from app.db.models.user.user_model import User
from app.db.models.pet_model import Pet
from app.db.models.auth.auth_group_model import AuthGroup
from app.schemas.user_schema import UserCreate, UserUpdate, UserSelfUpdate, TokenData
from app.security.auth_user_manager import UserAuthManager
import logging

logger = logging.getLogger(__name__)


class UserUseCases:
    def __init__(self, db_session: Session):
        self.db = db_session

    def _get_user_by_id(self, user_id: UUID) -> User:
        """Obtém um usuário pelo ID ou lança uma exceção se não existir"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )
        return user

    def _get_group_by_name(self, name: str) -> AuthGroup:
        """
        Retorna o grupo de permissões pelo nome.
        Lança erro se não encontrado.
        """
        group = self.db.query(AuthGroup).filter(AuthGroup.name == name).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Grupo '{name}' não encontrado. Verifique a carga inicial (seed).",
            )
        return group

    def register_user(self, user_input: UserCreate) -> User:
        """
        Cria um novo usuário e associa ao grupo 'user'.
        """
        try:
            # Verificar se o email já existe
            existing_user = self.db.query(User).filter_by(email=user_input.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Este email já está em uso.",
                )

            # Criar o usuário (a validação já ocorre no Pydantic schema)
            new_user = User(
                email=user_input.email,
                password=UserAuthManager.hash_password(user_input.password),
                is_superuser=False,  # Segurança garantida
            )

            # Obter o grupo de usuário padrão
            user_group = self._get_group_by_name("user")
            new_user.groups.append(user_group)

            # Salvar no banco
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
        except HTTPException:
            # Repassar exceções HTTP
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Erro ao registrar usuário: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao registrar o usuário. Tente novamente.",
            ) from e

    def login_user(self, user_input: UserCreate) -> TokenData:
        """
        Autentica o usuário com email e senha.
        Retorna token se válido, ou levanta exceções se inválido.
        """
        try:
            user: User = self.db.query(User).filter(User.email == user_input.email).first()

            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email ou senha inválidos"
                )

            if not UserAuthManager.verify_password(user_input.password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email ou senha inválidos"
                )

            # Incluir expires_delta para calcular expires_at
            from datetime import datetime, timedelta
            expires_delta = timedelta(minutes=120)  # 2 horas de validade
            expires_at = datetime.utcnow() + expires_delta

            # Criar o token com o tempo de expiração
            token = UserAuthManager.create_access_token(
                subject=str(user.id),
                expires_delta=expires_delta
            )

            # Retornar TokenData com o expires_at
            return TokenData(
                access_token=token,
                expires_at=expires_at
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Erro ao fazer login: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro durante o processo de login. Tente novamente."
            )

    def list_users(self, current_user: User, params: Params, order: str = "desc"):
        """
        Lista paginada de usuários ordenados por data de criação (asc|desc).
        Apenas superusuários têm acesso.
        """
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas superusuários podem listar todos os usuários."
            )

        query = self.db.query(User)
        query = query.order_by(User.created_at.desc() if order == "desc" else User.created_at.asc())
        return sqlalchemy_paginate(query, params)

    def update_self(self, user_id: UUID, data: UserSelfUpdate) -> User:
        """
        Permite que um usuário atualize seu próprio perfil.
        Requer senha atual para confirmar alterações.
        """
        user = self._get_user_by_id(user_id)

        # Se tentar alterar senha, verificar senha atual
        if data.password and not data.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para alterar a senha, é necessário fornecer a senha atual."
            )

        # Verificar senha atual se for fornecida
        if data.current_password:
            if not bcrypt.verify(data.current_password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Senha atual incorreta."
                )

        # Atualizar campos
        if data.email is not None:
            # Verificar se novo email já existe
            existing = self.db.query(User).filter(
                User.email == data.email,
                User.id != user_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Este email já está em uso."
                )
            user.email = data.email

        if data.password is not None:
            user.password = bcrypt.hash(data.password)

        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar o usuário."
            ) from e

    def update_user(self, user_id: UUID, data: UserUpdate) -> User:
        """
        Permite que um administrador atualize qualquer usuário.
        """
        user = self._get_user_by_id(user_id)

        # Atualizar campos
        if data.email is not None:
            # Verificar se novo email já existe
            existing = self.db.query(User).filter(
                User.email == data.email,
                User.id != user_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Este email já está em uso."
                )
            user.email = data.email

        if data.password is not None:
            user.password = bcrypt.hash(data.password)

        if data.is_active is not None:
            user.is_active = data.is_active

        if data.is_superuser is not None:
            user.is_superuser = data.is_superuser

        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar o usuário."
            ) from e

    def deactivate_user(self, user_id: UUID) -> dict:
        """
        Desativa um usuário (soft delete).
        """
        user = self._get_user_by_id(user_id)

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário já está inativo."
            )

        user.is_active = False

        try:
            self.db.commit()
            return {"message": f"Usuário '{user.email}' desativado com sucesso."}
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao desativar o usuário."
            ) from e

    def reactivate_user(self, user_id: UUID) -> dict:
        """
        Reativa um usuário previamente desativado.
        """
        user = self._get_user_by_id(user_id)

        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário já está ativo."
            )

        user.is_active = True

        try:
            self.db.commit()
            return {"message": f"Usuário '{user.email}' reativado com sucesso."}
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao reativar o usuário."
            ) from e

    def delete_user_permanently(self, user_id: UUID) -> dict:
        """
        Exclui permanentemente um usuário.
        Não permite excluir usuários com pets vinculados.
        """
        user = self._get_user_by_id(user_id)

        # Verificar se usuário possui pets
        pets_count = self.db.query(Pet).filter(Pet.owner_id == user_id).count()
        if pets_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível excluir o usuário porque ele possui {pets_count} pet(s) vinculado(s). "
                       f"Transfira os pets para outro usuário ou remova-os antes de excluir."
            )

        try:
            # Remover usuário de todos os grupos e permissões
            user.groups = []
            user.permissions = []

            # Deletar o usuário
            self.db.delete(user)
            self.db.commit()

            return {"message": f"Usuário '{user.email}' excluído permanentemente."}
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao excluir o usuário permanentemente."
            ) from e
