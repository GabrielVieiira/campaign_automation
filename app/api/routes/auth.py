"""Rotas de autenticação.

Fornece endpoints para:
    - POST /auth/login  — autentica e recebe um token JWT
    - GET  /auth/me     — recupera o perfil do usuário atualmente autenticado

As rotas delegam toda a lógica de negócios para `auth_service`.
Nenhuma lógica de autenticação vive aqui.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.api.schemas.auth import LoginRequest, TokenResponse
from app.api.schemas.users import UserResponse
from app.models.user import User
from app.services.auth_service import authenticate_user, create_token_for_user
from app.shared.exceptions import AuthenticationError

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    description="Valida as credenciais de e-mail e senha. Retorna um token de acesso JWT em caso de sucesso.",
    status_code=status.HTTP_200_OK,
)
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Autentica um usuário e retorna um token de acesso.

    Args:
        body: Credenciais de login (e-mail + senha).
        db:   Sessão do banco de dados (injetada).

    Returns:
        O token de acesso JWT e o tipo de token.

    Raises:
        HTTPException 401: Se as credenciais forem inválidas.
    """
    try:
        user = authenticate_user(db, email=body.email, password=body.password)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    token = create_token_for_user(user)
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obter usuário atual",
    description="Retorna o perfil do usuário autenticado no momento.",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Retorna o perfil do usuário autenticado.

    Args:
        current_user: Injetado pela dependência `get_current_user`.

    Returns:
        O perfil público do usuário atual.
    """
    return UserResponse.model_validate(current_user)
