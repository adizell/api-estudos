# app/db/models/auth/auth_permission_model.py

from sqlalchemy import Column, BigInteger, String, ForeignKey, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base


class AuthPermission(Base):
    __tablename__ = "auth_permission"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    codename: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    content_type_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("auth_content_type.id"), nullable=False)

    # Relações
    content_type = relationship("AuthContentType", back_populates="permissions", lazy="joined")
    groups = relationship("AuthGroup", secondary="auth_group_permissions", back_populates="permissions")

    def __repr__(self):
        return f"<AuthPermission(codename={self.codename})>"
