# app/models/auth/auth_group_model.py


from sqlalchemy import Column, BigInteger, String, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class AuthGroup(Base):
    __tablename__ = "auth_group"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(150), unique=True, nullable=False, index=True)

    # Relação com permissões
    permissions = relationship(
        "AuthPermission",
        secondary="auth_group_permissions",
        back_populates="groups",
        lazy="joined"  # Otimiza queries carregando dados em join
    )

    def __repr__(self):
        return f"<AuthGroup(name={self.name})>"

    def has_permission(self, codename: str) -> bool:
        """
        Verifica se o grupo possui uma permissão específica pelo codename.
        """
        return any(perm.codename == codename for perm in self.permissions)
