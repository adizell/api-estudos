# app/schemas/category_schemas.py

from pydantic import BaseModel, constr, Field
from typing import Optional, List


class CategoryBase(BaseModel):
    """Base schema for all category types."""
    name: constr(min_length=1, max_length=100) = Field(..., description="Category name")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""
    name: Optional[constr(min_length=1, max_length=100)] = Field(None, description="Category name")


class CategoryOutput(CategoryBase):
    """Schema for category output data."""
    id: int
    slug: str
    is_active: bool

    class Config:
        from_attributes = True


class CategoryListOutput(BaseModel):
    """Schema for list of categories."""
    items: List[CategoryOutput]
    total: int
