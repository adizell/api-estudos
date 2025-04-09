from uuid import UUID

from app.core import ResourceNotFoundException
from app.crud.pet import pet as crud_pet
from app.db.models import Pet


# Dentro de um método do serviço:
def get_pet_by_id(self, pet_id: UUID) -> Pet:
    """
    Obtém um pet específico pelo ID.
    """
    pet = crud_pet.get(self.db_session, id=pet_id)
    if not pet:
        raise ResourceNotFoundException(detail="Pet não encontrado", resource_id=pet_id)
    return pet
