# app/db/models/partner_model.py

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Partner(Base):
    """
    Modelo que representa um parceiro (partner) vinculado a um client.

    Atributos:
        id (BigInteger): Identificador único do partner.
        name (String): Nome do partner.
        client_id (BigInteger): Chave estrangeira para o client associado.
        is_active (Boolean): Indica se o partner está ativo.
        created_at (DateTime): Data de criação.
        updated_at (DateTime): Data de atualização.
    """
    __tablename__ = "partners"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    client_id = Column(BigInteger, ForeignKey("clients.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    # Relacionamento com o client
    client = relationship("Client", back_populates="partners")
    
    # Relacionamento com os usuários vinculados a esse partner
    # users = relationship("User", back_populates="partner")

    def __repr__(self) -> str:
        return f"<Partner(name={self.name})>"
