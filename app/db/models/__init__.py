# app/db/models/__init__.py

# Importa modelos principais
from ..base import Base
from .client_model import Client
from .partner_model import Partner
from .specie_model import Specie
from .pet_model import Pet

# Importa modelos do usuário (subpasta user)
from .user.user_model import User
from .user.user_access_group_model import user_access_groups
from .user.user_access_permission_model import user_access_permission

# Importa modelos de autorização (subpasta auth)
from .auth.auth_group_model import AuthGroup
from .auth.auth_permission_model import AuthPermission
from .auth.auth_content_type_model import AuthContentType
from .auth.auth_group_permissions_model import auth_group_permissions

# Importar as categorias do pet
from .pet_category_model import (
    PetCategoryEnvironment,
    PetCategoryCondition,
    PetCategoryPurpose,
    PetCategoryHabitat,
    PetCategoryOrigin,
    PetCategorySize,
    PetCategoryAge,
)
