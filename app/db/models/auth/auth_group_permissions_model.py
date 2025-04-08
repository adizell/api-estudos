# app/db/models/auth_group_permissions_model.py

from sqlalchemy import Table, Column, BigInteger, ForeignKey, UniqueConstraint
from app.db.base import Base

auth_group_permissions = Table(
    "auth_group_permissions",
    Base.metadata,
    Column("group_id", BigInteger, ForeignKey("auth_group.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", BigInteger, ForeignKey("auth_permission.id", ondelete="CASCADE"), primary_key=True),

    # Garante que não haja duplicações
    UniqueConstraint("group_id", "permission_id", name="uq_group_permission")
)
