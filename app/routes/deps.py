# app/routes/deps.py

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from contextlib import contextmanager
from uuid import UUID

from app.db.connection import Session as ScopedSession
from app.db.models.user.user_model import User
from app.db.models.client_model import Client
from app.security.auth_user_manager import UserAuthManager
from app.security.auth_client_manager import ClientAuthManager

bearer_scheme = HTTPBearer()


########################################################################
# Gerenciamento de Sessão
########################################################################

@contextmanager
def _session_context():
    session = ScopedSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Session:
    with _session_context() as session:
        yield session


get_db_session = get_session  # alias


########################################################################
# Autenticação via Token do Client
########################################################################

def verify_client_token(
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    token = credentials.credentials
    payload = ClientAuthManager.verify_client_token(token)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: 'sub' não encontrado no token do client.",
        )
    return sub


def get_current_client(
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
        db: Session = Depends(get_session),
) -> Client:
    token = credentials.credentials
    payload = ClientAuthManager.verify_client_token(token)
    client_id = payload.get("sub")

    try:
        client_id = int(client_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token do client inválido: 'sub' não é um inteiro.",
        )

    client = db.query(Client).filter(Client.id == client_id, Client.is_active.is_(True)).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Client não encontrado ou inativo.",
        )
    return client


########################################################################
# Autenticação via Token do Usuário
########################################################################

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
        db: Session = Depends(get_session),
) -> User:
    token = credentials.credentials
    payload = UserAuthManager.verify_access_token(token)

    try:
        user_id = UUID(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: 'sub' não é um UUID válido.",
        )

    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo.",
        )
    return user
