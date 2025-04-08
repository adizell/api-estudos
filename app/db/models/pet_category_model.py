# app/db/models/pet_category_model.py

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, func, Index
from app.db.base import Base


class PetCategoryBase:
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


# Ambiente (PetCategoryEnvironment)
class PetCategoryEnvironment(Base, PetCategoryBase):
    __tablename__ = "pet_category_environment"
    __table_args__ = (Index("idx_environment_slug", "slug"),)


# Condição (PetCategoryCondition)
class PetCategoryCondition(Base, PetCategoryBase):
    __tablename__ = "pet_category_condition"
    __table_args__ = (Index("idx_condition_slug", "slug"),)


# Finalidade (PetCategoryPurpose)
class PetCategoryPurpose(Base, PetCategoryBase):
    __tablename__ = "pet_category_purpose"
    __table_args__ = (Index("idx_purpose_slug", "slug"),)


# Habitat (PetCategoryHabitat)
class PetCategoryHabitat(Base, PetCategoryBase):
    __tablename__ = "pet_category_habitat"
    __table_args__ = (Index("idx_habitat_slug", "slug"),)


# Origem (PetCategoryOrigin)
class PetCategoryOrigin(Base, PetCategoryBase):
    __tablename__ = "pet_category_origin"
    __table_args__ = (Index("idx_origin_slug", "slug"),)


# Porte (PetCategorySize)
class PetCategorySize(Base, PetCategoryBase):
    __tablename__ = "pet_category_size"
    __table_args__ = (Index("idx_size_slug", "slug"),)


# Fase da vida (PetCategoryAge)
class PetCategoryAge(Base, PetCategoryBase):
    __tablename__ = "pet_category_age"
    __table_args__ = (Index("idx_age_slug", "slug"),)
