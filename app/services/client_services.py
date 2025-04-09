# app/services/client_services.py

from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.client_model import Client
from app.security.auth_client_manager import ClientAuthManager


class ClientServices:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def client_login(self, client_id: str, client_secret: str, expires_in: int = None) -> str:
        client_db = self.db_session.query(Client).filter_by(client_id=client_id).first()
        if client_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Client credentials invalid"
            )
        if not ClientAuthManager.verify_password(client_secret, client_db.client_secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Client credentials invalid"
            )
        if not client_db.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client is inactive"
            )
        expires_delta = timedelta(days=expires_in) if expires_in is not None else None
        token = ClientAuthManager.create_client_token(
            subject=str(client_db.id),
            expires_delta=expires_delta
        )
        return token
