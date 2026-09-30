"""Testes unitários para app/selectors/user_selector.py.

Os testes cobrem:
    - get_user_by_id retorna o usuário quando encontrado.
    - get_user_by_id retorna None para um ID desconhecido.
    - get_user_by_id exclui usuários com soft delete por padrão.
    - get_user_by_id inclui usuários com soft delete quando include_deleted=True.
    - get_user_by_email retorna o usuário quando encontrado.
    - get_user_by_email retorna None para e-mail desconhecido.
    - get_user_by_email exclui usuários com soft delete por padrão.
    - get_active_users_by_company retorna apenas os usuários ativos da empresa.
"""

from app.selectors.user_selector import (
    get_active_users_by_company,
    get_user_by_email,
    get_user_by_id,
)
from sqlalchemy.orm import Session
from tests.conftest import make_user


class TestGetUserById:
    def test_returns_user_when_found(self, db: Session):
        user = make_user(db, email="byid@example.com")
        found = get_user_by_id(db, user.id)
        assert found is not None
        assert found.id == user.id

    def test_returns_none_for_unknown_id(self, db: Session):
        assert get_user_by_id(db, 99999) is None

    def test_excludes_soft_deleted_by_default(self, db: Session):
        user = make_user(db, email="softdeleted@example.com")
        user.soft_delete()
        db.flush()
        assert get_user_by_id(db, user.id) is None

    def test_includes_soft_deleted_when_requested(self, db: Session):
        user = make_user(db, email="softdeleted2@example.com")
        user.soft_delete()
        db.flush()
        found = get_user_by_id(db, user.id, include_deleted=True)
        assert found is not None
        assert found.is_deleted is True


class TestGetUserByEmail:
    def test_returns_user_when_found(self, db: Session):
        make_user(db, email="byemail@example.com")
        found = get_user_by_email(db, "byemail@example.com")
        assert found is not None
        assert found.email == "byemail@example.com"

    def test_returns_none_for_unknown_email(self, db: Session):
        assert get_user_by_email(db, "nobody@example.com") is None

    def test_excludes_soft_deleted_by_default(self, db: Session):
        user = make_user(db, email="sdbyemail@example.com")
        user.soft_delete()
        db.flush()
        assert get_user_by_email(db, "sdbyemail@example.com") is None

    def test_normalizes_email_whitespace(self, db: Session):
        make_user(db, email="spaced@example.com")
        found = get_user_by_email(db, "  spaced@example.com  ")
        assert found is not None


class TestGetActiveUsersByCompany:
    def test_returns_active_users(self, db: Session):
        make_user(db, email="c1active@example.com", company_id=1)
        make_user(db, email="c1active2@example.com", company_id=1)
        users = get_active_users_by_company(db, 1)
        emails = {u.email for u in users}
        assert "c1active@example.com" in emails
        assert "c1active2@example.com" in emails

    def test_excludes_inactive_users(self, db: Session):
        make_user(db, email="c2inactive@example.com", company_id=2, is_active=False)
        users = get_active_users_by_company(db, 2)
        assert all(u.is_active for u in users)

    def test_excludes_soft_deleted_users(self, db: Session):
        user = make_user(db, email="c3deleted@example.com", company_id=3)
        user.soft_delete()
        db.flush()
        users = get_active_users_by_company(db, 3)
        assert not any(u.email == "c3deleted@example.com" for u in users)

    def test_returns_empty_list_for_unknown_company(self, db: Session):
        assert get_active_users_by_company(db, 99999) == []
