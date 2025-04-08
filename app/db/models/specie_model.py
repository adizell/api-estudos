# app/db/models/specie_model.py

from sqlalchemy import Column, BigInteger, String, DateTime, func, Index, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Specie(Base):
    __tablename__ = "species"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relação com Pet
    pets = relationship("Pet", back_populates="specie")

    # Índices
    idx_slug = Index("idx_specie_slug", slug)
    idx_is_active = Index("idx_specie_is_active", is_active)

    __table_args__ = (idx_slug, idx_is_active)
