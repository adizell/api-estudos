# app/routes/category.py

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, Type

from app.api.deps import get_session, get_current_user
from app.security.permissions import require_permission

from app.services.category_service import CategoryService
from app.core.config import settings
from app.schemas.category_schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryOutput,
    CategoryListOutput,
)
from app.db.models.pet_category_model import (
    PetCategoryEnvironment,
    PetCategoryCondition,
    PetCategoryPurpose,
    PetCategoryHabitat,
    PetCategoryOrigin,
    PetCategorySize,
    PetCategoryAge,
)

router = APIRouter()  # Esta linha é essencial!

# Define the main router for all category routes
category_router = APIRouter(dependencies=[Depends(get_current_user)])


# Config for all category types
CATEGORY_CONFIG = [
    {
        "name": "Environment",
        "route_prefix": "/environment",
        "model": PetCategoryEnvironment,
        "permission_prefix": "category_environment",
        "tag": "Category Environment"
    },
    {
        "name": "Condition",
        "route_prefix": "/condition",
        "model": PetCategoryCondition,
        "permission_prefix": "category_condition",
        "tag": "Category Condition"
    },
    {
        "name": "Purpose",
        "route_prefix": "/purpose",
        "model": PetCategoryPurpose,
        "permission_prefix": "category_purpose",
        "tag": "Category Purpose"
    },
    {
        "name": "Habitat",
        "route_prefix": "/habitat",
        "model": PetCategoryHabitat,
        "permission_prefix": "category_habitat",
        "tag": "Category Habitat"
    },
    {
        "name": "Origin",
        "route_prefix": "/origin",
        "model": PetCategoryOrigin,
        "permission_prefix": "category_origin",
        "tag": "Category Origin"
    },
    {
        "name": "Size",
        "route_prefix": "/size",
        "model": PetCategorySize,
        "permission_prefix": "category_size",
        "tag": "Category Size"
    },
    {
        "name": "Age",
        "route_prefix": "/age",
        "model": PetCategoryAge,
        "permission_prefix": "category_age",
        "tag": "Category Age"
    }
]


# Function to add CRUD routes for a specific category type
def register_category_routes(
        router: APIRouter,
        route_prefix: str,
        model_class: Type,
        permission_prefix: str,
        category_name: str,
        tag: str
):
    """
    Register CRUD routes for a specific category type.

    Args:
        router: FastAPI router to add routes to
        route_prefix: URL prefix for the routes (e.g., "/environment")
        model_class: SQLAlchemy model class for the category
        permission_prefix: Permission prefix for the category
        category_name: Human-readable name for the category
        tag: OpenAPI tag for the routes
    """

    @router.post(
        f"{route_prefix}",
        include_in_schema=settings.SCHEMA_VISIBILITY,
        response_model=CategoryOutput,
        status_code=status.HTTP_201_CREATED,
        summary=f"Create {category_name} Category",
        description=f"Create a new {category_name.lower()} category. Requires authentication with 'add_{permission_prefix}' permission.",
        tags=[tag]
    )
    def create_category(
            category: CategoryCreate,
            db: Session = Depends(get_session),
            _: bool = Depends(require_permission(f"add_{permission_prefix}")),
    ):
        uc = CategoryService(db, model_class)
        return uc.create_category(category)

    @router.get(
        f"{route_prefix}",
        response_model=CategoryListOutput,
        summary=f"List {category_name} Categories",
        description=f"List all {category_name.lower()} categories. Requires authentication with 'list_{permission_prefix}' permission.",
        tags=[tag]
    )
    def list_categories(
            skip: int = Query(0, ge=0, description="Number of items to skip"),
            limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
            is_active: Optional[bool] = Query(None, description="Filter by active status"),
            db: Session = Depends(get_session),
            _: bool = Depends(require_permission(f"list_{permission_prefix}")),
    ):
        uc = CategoryService(db, model_class)
        return uc.list_categories(skip, limit, is_active)

    @router.get(
        f"{route_prefix}/{{category_id}}",
        response_model=CategoryOutput,
        summary=f"Get {category_name} Category",
        description=f"Get a specific {category_name.lower()} category by ID. Requires authentication with 'view_{permission_prefix}' permission.",
        tags=[tag]
    )
    def get_category(
            category_id: int,
            db: Session = Depends(get_session),
            _: bool = Depends(require_permission(f"view_{permission_prefix}")),
    ):
        uc = CategoryService(db, model_class)
        return uc._get_by_id(category_id)

    @router.put(
        f"{route_prefix}/{{category_id}}",
        include_in_schema=settings.SCHEMA_VISIBILITY,
        response_model=CategoryOutput,
        summary=f"Update {category_name} Category",
        description=f"Update a specific {category_name.lower()} category. Requires authentication with 'update_{permission_prefix}' permission.",
        tags=[tag]
    )
    def update_category(
            category_id: int,
            category: CategoryUpdate,
            db: Session = Depends(get_session),
            _: bool = Depends(require_permission(f"update_{permission_prefix}")),
    ):
        uc = CategoryService(db, model_class)
        return uc.update_category(category_id, category)

    @router.delete(
        f"{route_prefix}/{{category_id}}",
        include_in_schema=settings.SCHEMA_VISIBILITY,
        status_code=status.HTTP_200_OK,
        summary=f"Delete {category_name} Category",
        description=f"Delete a specific {category_name.lower()} category. Requires authentication with 'delete_{permission_prefix}' permission.",
        tags=[tag]
    )
    def delete_category(
            category_id: int,
            db: Session = Depends(get_session),
            _: bool = Depends(require_permission(f"delete_{permission_prefix}")),
    ):
        uc = CategoryService(db, model_class)
        return uc.delete_category(category_id)

    @router.patch(
        f"{route_prefix}/{{category_id}}/status",
        include_in_schema=settings.SCHEMA_VISIBILITY,
        response_model=CategoryOutput,
        summary=f"Toggle {category_name} Category Status",
        description=f"Toggle the active status of a {category_name.lower()} category. Requires authentication with 'update_{permission_prefix}' permission.",
        tags=[tag]
    )
    def toggle_category_status(
            category_id: int,
            active: bool = Query(..., description="New active status"),
            db: Session = Depends(get_session),
            _: bool = Depends(require_permission(f"update_{permission_prefix}")),
    ):
        uc = CategoryService(db, model_class)
        return uc.toggle_status(category_id, active)


# Register CRUD routes for each category type
for config in CATEGORY_CONFIG:
    register_category_routes(
        router=category_router,
        route_prefix=config["route_prefix"],
        model_class=config["model"],
        permission_prefix=config["permission_prefix"],
        category_name=config["name"],
        tag=config["tag"]
    )
