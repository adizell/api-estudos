# app/main.py
import logging
import os
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.api.v1.endpoints.category import category_router
from app.routes.species_active_routes import router as species_active_router
from app.core.middleware import (
    ExceptionMiddleware,
    RequestLoggingMiddleware,
    CSRFProtectionMiddleware,
    RateLimitingMiddleware,
    SecurityHeadersMiddleware
)

from app.api.v1.router import api_router as api_v1_router

# Configuração de logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Criar a instância do FastAPI
app = FastAPI(
    title="RGA API",
    description="Registro Geral Animal",
    version="1.0.0"
)

# Importar routers após criar a instância do app
from app.api.v1.endpoints.specie import router as specie_routes
from app.api.v1.endpoints.pet import router as pet_routes
from app.api.v1.endpoints.user import router as user_routes
from app.routes.client_jwt_routes import router as client_jwt_router
from app.routes.client_url_routes import create_url_router, update_url_router
from app.routes.pagination_specie import router as pag_species_routes
from app.routes.pagination_pet import router as pag_pets_routes

# Estabelecer o caminho absoluto para os arquivos estáticos
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Criar diretórios se não existirem
os.makedirs(os.path.join(static_dir, "img"), exist_ok=True)

# Montar o diretório de arquivos estáticos - APÓS criar a instância do app
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Adicionar middlewares
app.add_middleware(SecurityHeadersMiddleware)  # Deve ser o primeiro para garantir que os cabeçalhos sejam aplicados
app.add_middleware(CSRFProtectionMiddleware)  # Deixar este em segundo, ou seja, após SecurityHeadersMiddleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitingMiddleware)  # Adicione RateLimitingMiddleware antes do ExceptionMiddleware
app.add_middleware(ExceptionMiddleware)


# Rota específica para o favicon na raiz
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/img/favicon.ico")


# Rota para redirecionamento para documentação Redoc
@app.get("/redoc", include_in_schema=False)
async def redoc():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="Documentação da API",
    )


# Rota raiz que redireciona para a documentação Swagger
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return get_swagger_ui_html(openapi_url=app.openapi_url, title=app.title)

# Incluir o novo router v1
app.include_router(api_v1_router, prefix="/api/v1")

# Incluir todos os routers
app.include_router(client_jwt_router)
app.include_router(create_url_router)
app.include_router(update_url_router)
app.include_router(user_routes)
app.include_router(specie_routes)
app.include_router(pet_routes)
app.include_router(pag_species_routes)
app.include_router(pag_pets_routes)
app.include_router(species_active_router)
###################################
app.include_router(category_router)

# Adicionar middlewares
app.add_middleware(ExceptionMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitingMiddleware)  # Novo middleware de rate limiting


# Personalização do schema OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Removendo os schemas indesejados da documentação
    openapi_schema["components"]["schemas"].pop("HTTPValidationError", None)
    openapi_schema["components"]["schemas"].pop("ValidationError", None)

    # Remover (ou limpar) os responses 422 que referenciam os schemas removidos
    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            if "responses" in operation and "422" in operation["responses"]:
                # Removendo completamente o response 422
                del operation["responses"]["422"]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
