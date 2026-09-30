"""Utilitários de segurança: hash de senhas e gerenciamento de tokens JWT.

Usa:
- bcrypt para fazer o hash das senhas
- PyJWT para codificar/decodificar os tokens JWT

Este módulo é a única fonte de verdade para todas as operações criptográficas
dentro da aplicação. Nenhum outro módulo deve importar `jwt` ou `bcrypt` diretamente.
"""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings
from app.shared.exceptions import InvalidTokenError

# ---------------------------------------------------------------------------
# Hash de Senhas (Password hashing)
# ---------------------------------------------------------------------------


def hash_password(plain_password: str) -> str:
    """Retorna um hash bcrypt da senha fornecida em texto simples.

    Args:
        plain_password: A senha crua fornecida pelo usuário.

    Returns:
        Uma string com o hash bcrypt, segura para ser armazenada no banco de dados.
    """
    salt = bcrypt.gensalt()
    pwd_bytes = plain_password.encode("utf-8")
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica uma senha em texto simples comparando com um hash bcrypt armazenado.

    Args:
        plain_password: A senha crua a ser verificada.
        hashed_password: O hash bcrypt armazenado.

    Returns:
        True se a senha corresponder ao hash, False caso contrário.
    """
    pwd_bytes = plain_password.encode("utf-8")
    hash_bytes = hashed_password.encode("utf-8")

    try:
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except ValueError:
        # Ocorre se hash_bytes não estiver em um formato de hash bcrypt válido
        return False


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

_TOKEN_TYPE_ACCESS = "access"  # noqa: S105 — não é uma senha, apenas um rótulo


def create_access_token(
    subject: str,
    extra_claims: dict | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Cria um token de acesso JWT assinado.

    Args:
        subject: O assunto do token (subject), geralmente o ID do usuário em string.
        extra_claims: Reivindicações adicionais para embutir no payload do token.
        expires_delta: Janela de tempo customizada para expiração. Por padrão, usa
            o valor configurado em Settings.jwt_access_token_expire_minutes.

    Returns:
        Uma string com o JWT assinado.
    """
    settings = get_settings()

    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)

    now = datetime.now(UTC)
    payload: dict = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
        "type": _TOKEN_TYPE_ACCESS,
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decodifica e valida um token de acesso JWT.

    Args:
        token: A string JWT a ser decodificada.

    Returns:
        O dicionário (dict) com o payload decodificado.

    Raises:
        InvalidTokenError: Se o token estiver expirado, malformado ou possuir
            uma assinatura inválida.
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as exc:
        raise InvalidTokenError("O token expirou") from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenError("O token é inválido") from exc

    if payload.get("type") != _TOKEN_TYPE_ACCESS:
        raise InvalidTokenError("O tipo de token não é 'access'")

    return payload
