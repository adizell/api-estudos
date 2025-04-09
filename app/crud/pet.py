from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID

from app.crud.base import CRUDBase
from app.db.models.pet_model import Pet
from app.schemas.pet_schemas import PetCreate, PetUpdate


class CRUDPet(CRUDBase[Pet, PetCreate, PetUpdate]):
    """
    CRUD para operações com pets, estendendo o CRUD base.
    """

    def get_by_slug(self, db: Session, slug: str) -> Optional[Pet]:
        """
        Obtém um pet pelo slug.
        """
        return db.query(Pet).filter(Pet.slug == slug).first()

    def get_user_pets(
            self, db: Session, owner_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Pet]:
        """
        Obtém pets de um usuário específico.
        """
        return (
            db.query(Pet)
            .filter(Pet.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_owner(
            self, db: Session, *, obj_in: PetCreate, owner_id: UUID
    ) -> Pet:
        """
        Cria um pet associado a um dono.
        """
        obj_in_data = obj_in.dict()
        db_obj = Pet(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


pet = CRUDPet(Pet)  # Instância para uso direto (singleton)
