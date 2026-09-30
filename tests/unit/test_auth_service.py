"""Testes unitários para app/services/auth_service.py.

Os testes cobrem:
    - authenticate_user retorna o Usuário quando as credenciais são válidas.
    - authenticate_user levanta AuthenticationError para e-mail desconhecido.
    - authenticate_user levanta AuthenticationError para senha incorreta.
    - authenticate_user levanta AuthenticationError para usuário inativo.
    - authenticate_user levanta AuthenticationError para usuário excluído logicamente (soft-deleted).
    - create_token_for_user retorna um token decodificável com as claims corretas.
"""

import pytest
from app.core.security import decode_access_token
from app.services.auth_service import authenticate_user, create_token_for_user
from app.shared.exceptions import AuthenticationError
from sqlalchemy.orm import Session
from tests.conftest import make_user


class TestAuthenticateUser:
    """Testes para authenticate_user."""

    def test_returns_user_with_valid_credentials(self, db: Session):
        make_user(db, email="valid@example.com", password="correct")
        user = authenticate_user(db, email="valid@example.com", password="correct")
        assert user.email == "valid@example.com"

    def test_raises_for_unknown_email(self, db: Session):
        with pytest.raises(AuthenticationError):
            authenticate_user(db, email="ghost@example.com", password="any")

    def test_raises_for_wrong_password(self, db: Session):
        make_user(db, email="user@example.com", password="correct")
        with pytest.raises(AuthenticationError):
            authenticate_user(db, email="user@example.com", password="wrong")

    def test_raises_for_inactive_user(self, db: Session):
        make_user(db, email="inactive@example.com", password="pw", is_active=False)
        with pytest.raises(AuthenticationError, match="desativada"):
            authenticate_user(db, email="inactive@example.com", password="pw")

    def test_raises_for_soft_deleted_user(self, db: Session):
        """Usuários com exclusão lógica (soft-deleted) não devem ser encontrados por get_user_by_email."""
        u = make_user(db, email="deleted@example.com", password="pw")
        u.soft_delete()
        db.flush()
        with pytest.raises(AuthenticationError):
            authenticate_user(db, email="deleted@example.com", password="pw")

    def test_error_message_is_generic_for_unknown_email(self, db: Session):
        """A mensagem de erro não deve revelar se o e-mail existe."""
        with pytest.raises(AuthenticationError) as exc_info:
            authenticate_user(db, email="no@example.com", password="pw")
        assert "inválido" in exc_info.value.message.lower()

    def test_error_message_is_generic_for_wrong_password(self, db: Session):
        """A mensagem de erro não deve revelar que o e-mail está correto."""
        make_user(db, email="real@example.com", password="correct")
        with pytest.raises(AuthenticationError) as exc_info:
            authenticate_user(db, email="real@example.com", password="wrong")
        assert "inválido" in exc_info.value.message.lower()


class TestCreateTokenForUser:
    """Testes para create_token_for_user."""

    def test_returns_string_token(self, db: Session):
        user = make_user(db, email="tokenuser@example.com")
        token = create_token_for_user(user)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_user_id_as_subject(self, db: Session):
        user = make_user(db, email="sub@example.com")
        token = create_token_for_user(user)
        payload = decode_access_token(token)
        assert payload["sub"] == str(user.id)

    def test_token_contains_email_claim(self, db: Session):
        user = make_user(db, email="claim@example.com")
        token = create_token_for_user(user)
        payload = decode_access_token(token)
        assert payload["email"] == "claim@example.com"

    def test_token_contains_role_claim(self, db: Session):
        from app.shared.enums import Role
        user = make_user(db, email="role@example.com", role=Role.ADMIN)
        token = create_token_for_user(user)
        payload = decode_access_token(token)
        assert payload["role"] == "admin"
