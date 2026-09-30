"""Testes unitários para app/core/security.py.

Os testes cobrem:
    - Hash de senhas: hash_password retorna um hash bcrypt, não o texto simples.
    - Verificação de senhas: verify_password retorna True para senhas corretas
      e False para incorretas.
    - Criação de JWT: create_access_token retorna um token assinado válido.
    - Decodificação de JWT: decode_access_token retorna o payload correto.
    - Expiração de JWT: tokens expirados levantam InvalidTokenError.
    - Adulteração de JWT: tokens com assinaturas inválidas levantam InvalidTokenError.
    - Validação do tipo de JWT: tokens sem type='access' são rejeitados.
"""

from datetime import timedelta

import pytest
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.shared.exceptions import InvalidTokenError


class TestPasswordHashing:
    """Testes para geração de hash e verificação de senhas."""

    def test_hash_password_returns_string(self):
        result = hash_password("minhasenha")
        assert isinstance(result, str)

    def test_hash_password_is_not_plain_text(self):
        plain = "minhasenha"
        hashed = hash_password(plain)
        assert hashed != plain

    def test_hash_password_is_bcrypt(self):
        hashed = hash_password("minhasenha")
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    def test_two_hashes_of_same_password_differ(self):
        """O bcrypt usa salts aleatórios — senhas idênticas produzem hashes diferentes."""
        h1 = hash_password("igual")
        h2 = hash_password("igual")
        assert h1 != h2

    def test_verify_password_correct_password(self):
        hashed = hash_password("senhacorreta")
        assert verify_password("senhacorreta", hashed) is True

    def test_verify_password_wrong_password(self):
        hashed = hash_password("senhacorreta")
        assert verify_password("senhaerrada", hashed) is False

    def test_verify_password_empty_password(self):
        hashed = hash_password("senhacorreta")
        assert verify_password("", hashed) is False

    def test_verify_password_case_sensitive(self):
        hashed = hash_password("Senha")
        assert verify_password("senha", hashed) is False
        assert verify_password("Senha", hashed) is True


class TestJWTCreation:
    """Testes para criação de tokens de acesso JWT."""

    def test_create_access_token_returns_string(self):
        token = create_access_token(subject="42")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_has_three_parts(self):
        """Um JWT válido tem três partes codificadas em base64url separadas por pontos."""
        token = create_access_token(subject="42")
        parts = token.split(".")
        assert len(parts) == 3

    def test_create_access_token_with_extra_claims(self):
        token = create_access_token(subject="1", extra_claims={"role": "admin"})
        payload = decode_access_token(token)
        assert payload["role"] == "admin"

    def test_create_access_token_subject_in_payload(self):
        token = create_access_token(subject="99")
        payload = decode_access_token(token)
        assert payload["sub"] == "99"

    def test_create_access_token_type_is_access(self):
        token = create_access_token(subject="1")
        payload = decode_access_token(token)
        assert payload["type"] == "access"


class TestJWTDecoding:
    """Testes para decodificação e validação de JWT."""

    def test_decode_valid_token(self):
        token = create_access_token(subject="1")
        payload = decode_access_token(token)
        assert payload["sub"] == "1"

    def test_decode_expired_token_raises(self):
        token = create_access_token(subject="1", expires_delta=timedelta(seconds=-1))
        with pytest.raises(InvalidTokenError, match="expirou"):
            decode_access_token(token)

    def test_decode_tampered_token_raises(self):
        token = create_access_token(subject="1")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(InvalidTokenError):
            decode_access_token(tampered)

    def test_decode_completely_invalid_token_raises(self):
        with pytest.raises(InvalidTokenError):
            decode_access_token("nao.e.um.token")

    def test_decode_token_with_wrong_type_raises(self):
        """Tokens que não possuem type='access' devem ser rejeitados."""
        from datetime import UTC, datetime

        import jwt
        from app.core.config import get_settings

        settings = get_settings()
        payload = {
            "sub": "1",
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(minutes=30),
            "type": "refresh",  # tipo errado
        }
        bad_token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        with pytest.raises(InvalidTokenError, match="tipo"):
            decode_access_token(bad_token)
