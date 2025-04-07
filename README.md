# :dog: RGA PET :paw_prints:
### Root Project
```python
├── app/
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── connection.py
│   │   ├── seed_permissions.py
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── auth/
│   │       │   ├── __init__.py
│   │       │   ├── auth_content_type_model.py
│   │       │   ├── auth_group_model.py
│   │       │   ├── auth_group_permissions_model.py
│   │       │   └── auth_permission_model.py
│   │       ├── client_model.py
│   │       ├── pet_model.py
│   │       ├── partner_model.py
│   │       ├── specie_model.py
│   │       └── user/
│   │           ├── __init__.py
│   │           ├── user_model.py
│   │           ├── user_access_group_model.py
│   │           └── user_access_permission_model.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── client_jwt_routes.py
│   │   ├── client_url_routes.py
│   │   ├── deps.py
│   │   ├── pagination_pet.py
│   │   ├── pagination_specie.py
│   │   ├── pet_routes.py
│   │   ├── specie_routes.py
│   │   └── user_routes.py
│   ├── security/
│   │   ├── __init__.py
│   │   ├── client_auth_manager.py
│   │   ├── permission_checker.py
│   │   └── user_auth_manager.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── client_management_schema.py
│   │   ├── client_schema.py
│   │   ├── pet_schemas.py
│   │   ├── specie_schemas.py
│   │   └── user_schema.py
│   ├── use_cases/
│   │   ├── __init__.py
│   │   ├── client_management_usecases.py
│   │   ├── client_use_cases.py
│   │   ├── pet_use_cases.py
│   │   ├── specie_use_cases.py
│   │   └── user_use_cases.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── pagination.py
│   ├── templates/
│   │   ├── create_client_jwt.html
│   │   ├── create_client_url.html
│   │   └── update_client_url.html
│   ├── test/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── routes/
│   │   │   ├── test_pet_routes.py
│   │   │   └── test_specie_routes.py
│   │   ├── schemas/
│   │   │   ├── test_pet_schema.py
│   │   │   └── test_specie_schema.py
│   │   └── use_cases/
│   │       ├── test_pet_use_cases.py
│   │       └── test_specie_use_cases.py
│   ├── __init__.py
│   └── main.py
├── migrations/
│   ├── versions/
│   ├── env.py
│   ├── README.md
│   └── script.py.mako
├── venv/
├── .env
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── poetry.lock
├── pyproject.toml
└── README.md
```
