# app/routes/client_jwt_routes.py
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.routes.deps import get_db_session
from app.security.token_store import TokenStore
from app.security.auth_client_manager import ClientAuthManager
from app.db.models.client_model import Client

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/create-jwt", tags=["Create-jwt"], include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")


@router.get("/client", response_class=HTMLResponse)
async def client_login_form(request: Request):
    """
    Exibe o formulário HTML para o login do client (gera token).
    """
    return templates.TemplateResponse("create_client_jwt.html", {"request": request})


@router.post("/client", response_class=HTMLResponse)
async def client_login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db_session: Session = Depends(get_db_session),
):
    """
    Verifica as credenciais do client e gera um token JWT.

    Args:
        request: Objeto de requisição FastAPI
        username: Client ID do cliente
        password: Senha do cliente
        db_session: Sessão do banco de dados

    Returns:
        HTMLResponse: Resposta com template renderizado
    """
    try:
        # Valida a senha contra os hashes armazenados
        if not TokenStore.validate(password, ClientAuthManager.crypt_context):
            logger.warning(f"Tentativa de login com senha inválida para client: {username}")
            return templates.TemplateResponse("create_client_jwt.html", {
                "request": request,
                "error": "Senha incorreta. Token não gerado."
            })

        # Busca o client no banco para obter o ID (sub no token)
        client = db_session.query(Client).filter(Client.client_id == username).first()
        if not client:
            logger.warning(f"Tentativa de login com client inexistente: {username}")
            return templates.TemplateResponse("create_client_jwt.html", {
                "request": request,
                "error": "Client não encontrado."
            })

        # Verifica se o client está ativo
        if not client.is_active:
            logger.warning(f"Tentativa de login com client inativo: {username}")
            return templates.TemplateResponse("create_client_jwt.html", {
                "request": request,
                "error": "Client está inativo. Acesso negado."
            })

        # Gera token com o ID do client (convertendo para string para garantir compatibilidade)
        token = ClientAuthManager.create_client_token(subject=str(client.id))
        logger.info(f"Token JWT gerado com sucesso para client: {username}")

        return templates.TemplateResponse("create_client_jwt.html", {
            "request": request,
            "client_id": username,
            "success": True,
            "token": token
        })

    except SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados ao autenticar client: {e}")
        return templates.TemplateResponse("create_client_jwt.html", {
            "request": request,
            "error": "Erro ao consultar banco de dados. Tente novamente."
        })
    except Exception as e:
        logger.error(f"Erro inesperado ao autenticar client: {e}")
        return templates.TemplateResponse("create_client_jwt.html", {
            "request": request,
            "error": "Erro interno do servidor. Tente novamente mais tarde."
        })