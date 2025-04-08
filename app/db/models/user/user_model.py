# app/db/models/user/user_model.py

from sqlalchemy import (
    Column,
    Boolean,
    String,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relação com pets
    pets = relationship("Pet", back_populates="owner")

    # Relação many-to-many com grupos
    groups = relationship("AuthGroup", secondary="user_access_groups", backref="users")

    # Relação many-to-many com permissões individuais
    permissions = relationship(
        "AuthPermission", secondary="user_access_permission", backref="users"
    )

    def __repr__(self) -> str:
        return f"<User(email={self.email})>"
