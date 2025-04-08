# app/db/seed_permissions.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from decouple import config

from app.db.models.auth.auth_group_model import AuthGroup
from app.db.models.auth.auth_permission_model import AuthPermission
from app.db.models.auth.auth_content_type_model import AuthContentType
from app.db.base import Base

# Configurações do banco
TEST_MODE = config("TEST_MODE", default=False, cast=bool)
DB_URL = config("DB_URL_TEST") if TEST_MODE else config("DB_URL")
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dados base
groups = ["admin", "user"]

# Permissões de usuário/species/pets existentes
content_types = [
    {"app_label": "user", "model": "register_user"},
    {"app_label": "user", "model": "login_user"},
    {"app_label": "specie", "model": "list_species"},
    {"app_label": "specie", "model": "add_specie"},
    {"app_label": "specie", "model": "update_specie"},
    {"app_label": "specie", "model": "delete_specie"},
    {"app_label": "pet", "model": "add_pet"},
    {"app_label": "pet", "model": "list_pets"},
    {"app_label": "pet", "model": "update_pet"},
    {"app_label": "pet", "model": "delete_pet"},

    # Novas permissões para categorias - Environment
    {"app_label": "category", "model": "list_category_environment"},
    {"app_label": "category", "model": "add_category_environment"},
    {"app_label": "category", "model": "update_category_environment"},
    {"app_label": "category", "model": "delete_category_environment"},
    {"app_label": "category", "model": "view_category_environment"},

    # Novas permissões para categorias - Condition
    {"app_label": "category", "model": "list_category_condition"},
    {"app_label": "category", "model": "add_category_condition"},
    {"app_label": "category", "model": "update_category_condition"},
    {"app_label": "category", "model": "delete_category_condition"},
    {"app_label": "category", "model": "view_category_condition"},

    # Novas permissões para categorias - Purpose
    {"app_label": "category", "model": "list_category_purpose"},
    {"app_label": "category", "model": "add_category_purpose"},
    {"app_label": "category", "model": "update_category_purpose"},
    {"app_label": "category", "model": "delete_category_purpose"},
    {"app_label": "category", "model": "view_category_purpose"},

    # Novas permissões para categorias - Habitat
    {"app_label": "category", "model": "list_category_habitat"},
    {"app_label": "category", "model": "add_category_habitat"},
    {"app_label": "category", "model": "update_category_habitat"},
    {"app_label": "category", "model": "delete_category_habitat"},
    {"app_label": "category", "model": "view_category_habitat"},

    # Novas permissões para categorias - Origin
    {"app_label": "category", "model": "list_category_origin"},
    {"app_label": "category", "model": "add_category_origin"},
    {"app_label": "category", "model": "update_category_origin"},
    {"app_label": "category", "model": "delete_category_origin"},
    {"app_label": "category", "model": "view_category_origin"},

    # Novas permissões para categorias - Size
    {"app_label": "category", "model": "list_category_size"},
    {"app_label": "category", "model": "add_category_size"},
    {"app_label": "category", "model": "update_category_size"},
    {"app_label": "category", "model": "delete_category_size"},
    {"app_label": "category", "model": "view_category_size"},

    # Novas permissões para categorias - Age
    {"app_label": "category", "model": "list_category_age"},
    {"app_label": "category", "model": "add_category_age"},
    {"app_label": "category", "model": "update_category_age"},
    {"app_label": "category", "model": "delete_category_age"},
    {"app_label": "category", "model": "view_category_age"},
]

# Distribuição de permissões por grupo
group_permissions = {
    "admin": [
        # Permissões existentes
        "register_user", "login_user", "list_species",
        "add_pet", "list_pets", "update_pet", "delete_pet",

        # Apenas visualização/listagem de categorias (para ambos grupos)
        "list_category_environment", "view_category_environment",
        "list_category_condition", "view_category_condition",
        "list_category_purpose", "view_category_purpose",
        "list_category_habitat", "view_category_habitat",
        "list_category_origin", "view_category_origin",
        "list_category_size", "view_category_size",
        "list_category_age", "view_category_age",

        # Permissões administrativas de categorias (apenas para admin)
        #        "add_category_environment", "update_category_environment", "delete_category_environment",
        #        "add_category_condition", "update_category_condition", "delete_category_condition",
        #        "add_category_purpose", "update_category_purpose", "delete_category_purpose",
        #        "add_category_habitat", "update_category_habitat", "delete_category_habitat",
        #        "add_category_origin", "update_category_origin", "delete_category_origin",
        #        "add_category_size", "update_category_size", "delete_category_size",
        #        "add_category_age", "update_category_age", "delete_category_age",
    ],
    "user": [
        # Permissões existentes
        "register_user", "login_user", "list_species",
        "add_pet", "list_pets", "update_pet", "delete_pet",

        # Apenas visualização/listagem de categorias
        "list_category_environment", "view_category_environment",
        "list_category_condition", "view_category_condition",
        "list_category_purpose", "view_category_purpose",
        "list_category_habitat", "view_category_habitat",
        "list_category_origin", "view_category_origin",
        "list_category_size", "view_category_size",
        "list_category_age", "view_category_age",
    ]
}


def run_seed():
    session = SessionLocal()
    try:
        # Criação de grupos
        group_objs = {}
        for name in groups:
            group = session.query(AuthGroup).filter_by(name=name).first()
            if not group:
                group = AuthGroup(name=name)
                session.add(group)
                print(f"🟢 Grupo '{name}' criado com sucesso.")
            else:
                print(f"🟡 Grupo '{name}' já existe.")
            group_objs[name] = group

        # Criação de content types e permissões
        permission_objs = {}
        for ct in content_types:
            ct_obj = session.query(AuthContentType).filter_by(
                app_label=ct["app_label"], model=ct["model"]
            ).first()
            if not ct_obj:
                ct_obj = AuthContentType(app_label=ct["app_label"], model=ct["model"])
                session.add(ct_obj)
                session.flush()
                print(f"🟢 ContentType '{ct['app_label']}.{ct['model']}' criado.")
            else:
                print(f"🟡 ContentType '{ct['app_label']}.{ct['model']}' já existe.")

            codename = ct["model"]
            perm = session.query(AuthPermission).filter_by(codename=codename).first()
            if not perm:
                perm = AuthPermission(
                    name=f"Can {codename}",
                    codename=codename,
                    content_type_id=ct_obj.id,
                )
                session.add(perm)
                session.flush()
                print(f"🟢 Permissão '{codename}' criada.")
            else:
                print(f"🟡 Permissão '{codename}' já existe.")

            permission_objs[codename] = perm

        # Associação entre permissões e grupos
        for group_name, perms in group_permissions.items():
            group = group_objs[group_name]
            for codename in perms:
                permission = permission_objs.get(codename)
                if permission and permission not in group.permissions:
                    group.permissions.append(permission)
                    print(f"🟢 Permissão '{codename}' adicionada ao grupo '{group_name}'.")
                elif permission:
                    print(f"🟡 Grupo '{group_name}' já possui a permissão '{codename}'.")

        session.commit()
        print("✅ Seed finalizado com sucesso.")
    except Exception as e:
        session.rollback()
        print(f"🔴 Erro ao executar seed: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    run_seed()
