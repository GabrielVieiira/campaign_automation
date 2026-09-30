"""Serviço de autenticação — lógica de negócios para autenticação de usuários.

Este serviço é a fonte única de verdade para as operações de autenticação.
As rotas não devem implementar lógica de autenticação diretamente.

Responsabilidades:
    - Validar as credenciais do usuário (e-mail + senha).
    - Gerar tokens de acesso para usuários autenticados.
    - Fornecer um auxiliar (helper) para recuperar e validar um usuário a partir de um token.

O que este serviço NÃO faz:
    - Fazer hash de senhas no momento do registro (isso pertence a um futuro UserService).
    - Gerenciar sessões (o JWT não tem estado / é stateless).
    - Chamar APIs externas.
"""

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.selectors.user_selector import get_user_by_email
from app.shared.exceptions import AuthenticationError


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Valida e-mail/senha e retorna o Usuário autenticado.

    Args:
        db:       Sessão ativa do banco de dados.
        email:    O e-mail do usuário.
        password: A senha em texto puro fornecida pelo usuário.

    Returns:
        A instância do Usuário autenticado.

    Raises:
        AuthenticationError: Se o e-mail não existir, a senha estiver incorreta,
            a conta estiver inativa ou a conta sofrer exclusão lógica.
    """
    _generic_error = "E-mail ou senha inválidos"  # intencionalmente vago

    user = get_user_by_email(db, email)

    if not user:
        raise AuthenticationError(message=_generic_error)

    if not verify_password(password, user.hashed_password):
        raise AuthenticationError(message=_generic_error)

    if not user.is_active:
        raise AuthenticationError("A conta está desativada")

    return user


def create_token_for_user(user: User) -> str:
    """Cria um token de acesso JWT para um usuário autenticado.

    Embutimos o papel (role) do usuário como uma claim, para que a dependência
    de autenticação possa realizar autorizações sem uma consulta extra ao banco.

    Args:
        user: A instância do Usuário autenticado.

    Returns:
        Uma string com o token de acesso JWT assinado.
    """
    return create_access_token(
        subject=str(user.id),
        extra_claims={
            "email": user.email,
            "role": str(user.role),
        },
    )
