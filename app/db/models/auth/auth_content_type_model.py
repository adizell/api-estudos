# app/db/models/auth_content_type_model.py

from sqlalchemy import Column, BigInteger, String, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class AuthContentType(Base):
    __tablename__ = "auth_content_type"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    app_label = Column(String(100), nullable=False, index=True, doc="Nome da aplicação ou domínio (ex: pet, specie)")
    model = Column(String(100), nullable=False, index=True, doc="Ação ou entidade (ex: create, list, update)")

    # Relação reversa com AuthPermission
    permissions = relationship("AuthPermission", back_populates="content_type", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_content_type_app_model", "app_label", "model"),
    )

    def __repr__(self):
        return f"<AuthContentType(app_label='{self.app_label}', model='{self.model}')>"
