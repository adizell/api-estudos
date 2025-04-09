# app/api/v1/router.py

from fastapi import APIRouter
from app.api.v1.endpoints import (
    pet,
    specie,
    category,
    user,
    client_auth,
    active_species,
    pagination
)

api_router = APIRouter()

# Incluir os routers dos endpoints
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(pet.router, prefix="/pet", tags=["Pet"])
api_router.include_router(specie.router, prefix="/specie", tags=["Specie"])
api_router.include_router(category.category_router, prefix="/categories", tags=["Category"])

# Incluir os novos routers migrados
api_router.include_router(active_species.router, prefix="/active-species", tags=["Active Species"])
api_router.include_router(pagination.pet_pagination_router)
api_router.include_router(pagination.specie_pagination_router)

# Incluir routers dos clients (JWT e URL)
api_router.include_router(client_auth.jwt_router)
api_router.include_router(client_auth.create_url_router)
api_router.include_router(client_auth.update_url_router)
