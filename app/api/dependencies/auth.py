"""Dependências do FastAPI para autenticação e autorização.

Estas dependências são injetadas nas funções de rota (routes) através do `Depends()`.
Elas são o ponto único de aplicação para autenticação e autorização.

Uso:
    # Exige qualquer usuário autenticado:
    user: User = Depends(get_current_user)

    # Exige um papel (role) específico:
    user: User = Depends(require_role(Role.ADMIN))

Design de autorização:
    As verificações de papel (Role) são centralizadas aqui. NÃO adicione comparações puras
    `if user.role == ...` nos manipuladores de rotas ou serviços. Use estas dependências em vez disso.
"""

import logging
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.selectors.user_selector import get_user_by_id
from app.shared.enums import Role
from app.shared.exceptions import InvalidTokenError

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Valida o token Bearer e retorna o Usuário (User) autenticado.

    Extrai o JWT do cabeçalho de Authorization, o decodifica, e
    busca o Usuário correspondente no banco de dados.

    Args:
        credentials: Credenciais JWT Bearer vindas do cabeçalho Authorization.
        db:          Sessão ativa do banco de dados.

    Returns:
        A instância do Usuário ativo e autenticado.

    Raises:
        HTTPException 401: Se o token estiver ausente, inválido ou expirado.
        HTTPException 401: Se o usuário não existir ou estiver inativo/excluído.
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
    except InvalidTokenError as exc:
        logger.debug("Falha na validação do token: %s", exc.message)
        raise unauthorized from exc

    user_id_str: str | None = payload.get("sub")
    if not user_id_str:
        raise unauthorized

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError) as err:
        raise unauthorized from err

    user = get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise unauthorized

    return user


def require_role(*roles: Role) -> Callable[..., User]:
    """Dependência que verifica se o usuário atual possui um dos papéis exigidos.

    Args:
        *roles: Um ou mais valores de Papel (Role). O usuário deve ter pelo menos um.

    Returns:
        Uma função de dependência do FastAPI.

    Exemplo:
        @router.delete("/users/{id}")
        def delete_user(user = Depends(require_role(Role.ADMIN))):
            ...
    """

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissões insuficientes",
            )
        return current_user

    return _dependency
