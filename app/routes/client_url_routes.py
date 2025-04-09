# app/routes/client_url_routes.py

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.db.models import Client
from app.api.deps import get_db_session
from app.services.client_management_services import ClientManagementServices
from app.security.token_store import TokenStore
from app.security.auth_client_manager import ClientAuthManager

create_url_router = APIRouter(prefix="/create-url", tags=["Create-URL"], include_in_schema=False)
update_url_router = APIRouter(prefix="/update-url", tags=["Update-URL"], include_in_schema=False)

templates = Jinja2Templates(directory="app/templates")


@create_url_router.get("/client", response_class=HTMLResponse)
async def create_client_form(request: Request):
    """
    Exibe o formulário HTML para criar um novo client.
    """
    return templates.TemplateResponse("create_client_url.html", {"request": request})


@create_url_router.post("/client", response_class=HTMLResponse)
async def create_client(
        request: Request,
        password: str = Form(...),
        db_session: Session = Depends(get_db_session),
):
    """
    Cria um novo client após validar a senha administrativa.

    Args:
        request: Objeto de requisição FastAPI
        password: Senha administrativa para autorizar a criação
        db_session: Sessão do banco de dados

    Returns:
        HTMLResponse: Resposta com template renderizado
    """
    # Verifica se a senha é válida
    if not TokenStore.validate(password, ClientAuthManager.crypt_context):
        return templates.TemplateResponse("create_client_url.html", {
            "request": request,
            "error": "Senha incorreta. Acesso negado.",
        })

    try:
        uc = ClientManagementServices(db_session)
        credentials = uc.create_client()

        return templates.TemplateResponse("create_client_url.html", {
            "request": request,
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "success": True
        })
    except Exception as e:
        return templates.TemplateResponse("create_client_url.html", {
            "request": request,
            "error": f"Erro ao criar client: {str(e)}",
        })


@update_url_router.get("/client", response_class=HTMLResponse)
async def update_client_form(request: Request):
    """
    Exibe o formulário HTML para atualizar a chave secreta do client.
    """
    return templates.TemplateResponse("update_client_url.html", {"request": request})


@update_url_router.post("/client", response_class=HTMLResponse)
async def update_client_secret(
        request: Request,
        client_id: str = Form(...),
        password: str = Form(...),
        db_session: Session = Depends(get_db_session),
):
    """
    Atualiza a chave secreta de um client após validação da senha administrativa.

    Args:
        request: Objeto de requisição FastAPI
        client_id: ID do client a ser atualizado
        password: Senha administrativa para autorizar a atualização
        db_session: Sessão do banco de dados

    Returns:
        HTMLResponse: Resposta com template renderizado
    """
    # Verifica se a senha é válida
    if not TokenStore.validate(password, ClientAuthManager.crypt_context):
        return templates.TemplateResponse("update_client_url.html", {
            "request": request,
            "error": "Senha incorreta. Atualização não permitida.",
        })

    try:
        # Busca o client para verificar se existe
        client = db_session.query(Client).filter(Client.client_id == client_id).first()
        if not client:
            return templates.TemplateResponse("update_client_url.html", {
                "request": request,
                "error": "Client não encontrado.",
            })

        # Atualiza o secret do client
        uc = ClientManagementServices(db_session)
        result = uc.update_client_secret(client_id=client_id)

        # Gerar token JWT com o ID do client
        token = ClientAuthManager.create_client_token(subject=str(client.id))

        return templates.TemplateResponse("update_client_url.html", {
            "request": request,
            "client_id": client_id,
            "client_secret": result.get("new_client_secret"),
            "token": token,
            "success": True
        })

    except Exception as e:
        return templates.TemplateResponse("update_client_url.html", {
            "request": request,
            "error": f"Erro ao atualizar client: {str(e)}",
        })
