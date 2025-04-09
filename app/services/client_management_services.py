# app/services/client_management_services.py

import secrets
import logging
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.db.models.client_model import Client
from passlib.context import CryptContext

# Configurar logging
logger = logging.getLogger(__name__)

# Configuração para hashing usando bcrypt
crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ClientManagementServices:
    """
    Use cases para operações administrativas relacionadas aos clients.
    Permite criar novos clients e atualizar a chave secreta.
    """

    def __init__(self, db_session: Session) -> None:
        """
        Inicializa o caso de uso com uma sessão do banco de dados.

        Args:
            db_session: Sessão SQLAlchemy ativa
        """
        self.db_session = db_session

    def create_client(self) -> Dict[str, str]:
        """
        Cria um novo client.

        Gera um client_id e um client_secret (em texto plano),
        armazena o hash do client_secret no banco e retorna as credenciais.

        Returns:
            dict: { "client_id": <client_id>, "client_secret": <client_secret_plain> }

        Raises:
            HTTPException: Se ocorrer erro ao salvar o novo client.
        """
        try:
            # Gerar identificadores únicos
            client_id = secrets.token_urlsafe(16)
            plain_client_secret = secrets.token_urlsafe(32)
            hashed_secret = crypt_context.hash(plain_client_secret)

            # Criar nova instância do client
            new_client = Client(
                client_id=client_id,
                client_secret=hashed_secret,
                is_active=True
            )

            # Persistir no banco de dados
            self.db_session.add(new_client)
            self.db_session.commit()
            self.db_session.refresh(new_client)

            logger.info(f"Novo client criado com ID: {client_id}")

            return {
                "client_id": client_id,
                "client_secret": plain_client_secret
            }

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Erro de banco de dados ao criar client: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao criar client: {str(e)}"
            )
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Erro inesperado ao criar client: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar client"
            )

    def update_client_secret(self, client_id: str) -> Dict[str, str]:
        """
        Atualiza a chave secreta de um client.

        Busca o client pelo client_id, gera uma nova chave secreta,
        armazena o hash no banco e retorna a nova chave em texto plano.

        Args:
            client_id (str): O client_id do client (valor público).

        Returns:
            dict: { "client_id": <client_id>, "new_client_secret": <new_secret_plain> }

        Raises:
            HTTPException: Se o client não for encontrado ou ocorrer erro na atualização.
        """
        try:
            # Busca o client pelo ID
            client_db = self.db_session.query(Client).filter_by(client_id=client_id).first()
            if client_db is None:
                logger.warning(f"Tentativa de atualizar client inexistente: {client_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client não encontrado"
                )

            # Verifica se o client está ativo
            if not client_db.is_active:
                logger.warning(f"Tentativa de atualizar client inativo: {client_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Client está inativo"
                )

            # Gerar e atualizar a chave secreta
            new_secret_plain = secrets.token_urlsafe(32)
            new_secret_hashed = crypt_context.hash(new_secret_plain)
            client_db.client_secret = new_secret_hashed

            self.db_session.commit()
            logger.info(f"Chave secreta atualizada para client: {client_id}")

            return {
                "client_id": client_db.client_id,
                "new_client_secret": new_secret_plain
            }

        except HTTPException:
            # Repassar exceções HTTP já tratadas
            raise
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Erro de banco de dados ao atualizar client: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar client: {str(e)}"
            )
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Erro inesperado ao atualizar client: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar client"
            )
