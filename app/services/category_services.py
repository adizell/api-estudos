# app/services/category_services.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from slugify import slugify
from typing import Type, List, Optional, Dict, Any

from app.db.models.pet_category_model import PetCategoryBase
from app.schemas.category_schemas import CategoryCreate, CategoryUpdate


class CategoryServices:
    """
    Generic class for handling CRUD operations on category models.
    This class can be used with any category model that inherits from PetCategoryBase.
    """

    def __init__(self, db_session: Session, model_class: Type[PetCategoryBase]):
        """
        Initialize with a database session and the category model class.

        Args:
            db_session: SQLAlchemy session
            model_class: The category model class (e.g., PetCategorySize)
        """
        self.db_session = db_session
        self.model_class = model_class

    def _get_by_id(self, category_id: int) -> PetCategoryBase:
        """
        Get a category by its ID.

        Args:
            category_id: The category ID

        Returns:
            The category object

        Raises:
            HTTPException: If the category doesn't exist
        """
        category = self.db_session.query(self.model_class).filter(
            self.model_class.id == category_id
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model_class.__tablename__} with ID {category_id} not found"
            )
        return category

    def create_category(self, data: CategoryCreate) -> PetCategoryBase:
        """
        Create a new category.

        Args:
            data: The category data

        Returns:
            The created category

        Raises:
            HTTPException: If there's an error creating the category
        """
        try:
            # Generate slug from name
            slug = slugify(data.name)

            # Check if category with this name or slug already exists
            existing = self.db_session.query(self.model_class).filter(
                (self.model_class.name == data.name) | (self.model_class.slug == slug)
            ).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A category with name '{data.name}' or slug '{slug}' already exists"
                )

            # Create new category
            new_category = self.model_class(name=data.name, slug=slug)
            self.db_session.add(new_category)
            self.db_session.commit()
            self.db_session.refresh(new_category)

            return new_category

        except IntegrityError as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating category: {str(e)}"
            )
        except HTTPException:
            self.db_session.rollback()
            raise
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error creating category: {str(e)}"
            )

    def list_categories(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> Dict[str, Any]:
        """
        List categories with optional filtering.

        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            is_active: Filter by active status

        Returns:
            Dictionary with items and total count
        """
        query = self.db_session.query(self.model_class)

        # Apply filters
        if is_active is not None:
            query = query.filter(self.model_class.is_active == is_active)

        # Get total count for pagination
        total = query.count()

        # Apply pagination
        items = query.order_by(self.model_class.name).offset(skip).limit(limit).all()

        return {
            "items": items,
            "total": total
        }

    def update_category(self, category_id: int, data: CategoryUpdate) -> PetCategoryBase:
        """
        Update an existing category.

        Args:
            category_id: The category ID
            data: The updated data

        Returns:
            The updated category

        Raises:
            HTTPException: If there's an error updating the category
        """
        try:
            category = self._get_by_id(category_id)

            if data.name is not None:
                # Check if the new name would cause a conflict
                new_slug = slugify(data.name)
                existing = self.db_session.query(self.model_class).filter(
                    (self.model_class.name == data.name) | (self.model_class.slug == new_slug),
                    self.model_class.id != category_id
                ).first()

                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"A category with name '{data.name}' or slug '{new_slug}' already exists"
                    )

                # Update name and slug
                category.name = data.name
                category.slug = new_slug

            self.db_session.commit()
            self.db_session.refresh(category)

            return category

        except IntegrityError as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating category: {str(e)}"
            )
        except HTTPException:
            self.db_session.rollback()
            raise
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error updating category: {str(e)}"
            )

    def delete_category(self, category_id: int) -> Dict[str, str]:
        """
        Delete a category.

        Args:
            category_id: The category ID

        Returns:
            Success message

        Raises:
            HTTPException: If there's an error deleting the category
        """
        try:
            category = self._get_by_id(category_id)

            self.db_session.delete(category)
            self.db_session.commit()

            return {"message": f"Category with ID {category_id} successfully deleted"}

        except IntegrityError as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete this category because it's referenced by other entities: {str(e)}"
            )
        except HTTPException:
            self.db_session.rollback()
            raise
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error deleting category: {str(e)}"
            )

    def toggle_status(self, category_id: int, active: bool) -> PetCategoryBase:
        """
        Toggle the active status of a category.

        Args:
            category_id: The category ID
            active: The new active status

        Returns:
            The updated category

        Raises:
            HTTPException: If there's an error updating the category
        """
        try:
            category = self._get_by_id(category_id)

            category.is_active = active
            self.db_session.commit()
            self.db_session.refresh(category)

            return category

        except HTTPException:
            self.db_session.rollback()
            raise
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error updating category status: {str(e)}"
            )
