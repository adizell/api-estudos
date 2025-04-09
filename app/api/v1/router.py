# app/api/v1/router.py

from fastapi import APIRouter
from app.api.v1.endpoints import pet, specie, category, user

api_router = APIRouter()

# Incluir os routers dos endpoints
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(pet.router, prefix="/pet", tags=["Pet"])
api_router.include_router(specie.router, prefix="/specie", tags=["Specie"])
api_router.include_router(category.router, prefix="/categories", tags=["Category"])
