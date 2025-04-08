# app/db/models/pet_model.py

from sqlalchemy import (
    Column,
    BigInteger,
    String,
    ForeignKey,
    DateTime,
    func,
    Enum,
    Boolean,
    Index,
    CheckConstraint,
    UUID,
)

from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid


class Pet(Base):
    __tablename__ = "pets"

    SEX_OPTIONS = ["M", "F"]

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    sex = Column(Enum(*SEX_OPTIONS, name="sex_enum"), nullable=False)
    castrated = Column(Boolean, default=False)
    public = Column(Boolean, default=False)
    pro = Column(Boolean, default=False)
    date_birth = Column(DateTime, nullable=False, default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relacionamento com Species
    specie_id = Column("specie_id", ForeignKey("species.id"), nullable=False)
    specie = relationship("Specie", back_populates="pets")

    # Referência ao dono do Pet (o usuário que criou)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="pets")

    # Relacionamentos com categorias
    category_environment_id = Column(BigInteger, ForeignKey("pet_category_environment.id"), nullable=True)
    category_condition_id = Column(BigInteger, ForeignKey("pet_category_condition.id"), nullable=True)
    category_purpose_id = Column(BigInteger, ForeignKey("pet_category_purpose.id"), nullable=True)
    category_habitat_id = Column(BigInteger, ForeignKey("pet_category_habitat.id"), nullable=True)
    category_origin_id = Column(BigInteger, ForeignKey("pet_category_origin.id"), nullable=True)
    category_size_id = Column(BigInteger, ForeignKey("pet_category_size.id"), nullable=True)
    category_age_id = Column(BigInteger, ForeignKey("pet_category_age.id"), nullable=True)

    category_environment = relationship("PetCategoryEnvironment")
    category_condition = relationship("PetCategoryCondition")
    category_purpose = relationship("PetCategoryPurpose")
    category_habitat = relationship("PetCategoryHabitat")
    category_origin = relationship("PetCategoryOrigin")
    category_size = relationship("PetCategorySize")
    category_age = relationship("PetCategoryAge")

    # Índices
    index_specie_id = Index("idx_specie_id", specie_id)
    index_slug = Index("idx_slug", slug)

    __table_args__ = (
        CheckConstraint(
            "date_birth <= CURRENT_TIMESTAMP", name="check_date_birth_past"
        ),
        index_slug,
    )
