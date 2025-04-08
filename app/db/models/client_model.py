# app/db/models/client_model.py

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Client(Base):
    """
    Modelo que representa um client (aplicação/parceiro) que acessa a API.
    """

    __tablename__ = "clients"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    client_id = Column(String, unique=True, nullable=False)
    client_secret = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Removemos a relação com usuários, pois não há chave estrangeira direta:
    # users = relationship("User", back_populates="client")

    # Definimos a relação com parceiros (partners)
    partners = relationship("Partner", back_populates="client")

    def __repr__(self) -> str:
        return f"<Client(client_id={self.client_id})>"
