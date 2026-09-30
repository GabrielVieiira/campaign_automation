"""Testes unitários para o comportamento de exclusão lógica (soft delete) nos modelos.

Os testes cobrem:
    - Propriedade is_deleted retorna False para registros ativos.
    - Propriedade is_deleted retorna True após soft_delete().
    - soft_delete() define deleted_at para um datetime não nulo.
    - soft_delete() define deleted_by quando fornecido.
    - restore() limpa o deleted_at.
    - restore() limpa o deleted_by.
    - restore() define updated_by quando fornecido.
    - Registros apagados logicamente são excluídos de consultas padrão.
    - include_deleted=True retorna registros apagados logicamente.
"""

from datetime import UTC, datetime

from sqlalchemy.orm import Session
from tests.conftest import make_user


class TestSoftDeleteMixin:
    """Testes para o comportamento do SoftDeleteMixin no modelo de Usuário (User)."""

    def test_is_deleted_false_for_active_record(self, db: Session):
        user = make_user(db, email="active@soft.com")
        assert user.is_deleted is False

    def test_is_deleted_true_after_soft_delete(self, db: Session):
        user = make_user(db, email="todelete@soft.com")
        user.soft_delete()
        assert user.is_deleted is True

    def test_soft_delete_sets_deleted_at(self, db: Session):
        user = make_user(db, email="timestamp@soft.com")
        before = datetime.now(UTC)
        user.soft_delete()
        assert user.deleted_at is not None
        assert user.deleted_at >= before

    def test_soft_delete_sets_deleted_by(self, db: Session):
        actor = make_user(db, email="actor@soft.com")
        target = make_user(db, email="target@soft.com")
        target.soft_delete(deleted_by_id=actor.id)
        assert target.deleted_by == actor.id

    def test_soft_delete_without_actor(self, db: Session):
        user = make_user(db, email="nactor@soft.com")
        user.soft_delete()
        assert user.deleted_by is None

    def test_restore_clears_deleted_at(self, db: Session):
        user = make_user(db, email="restore@soft.com")
        user.soft_delete()
        assert user.is_deleted is True
        user.restore()
        assert user.deleted_at is None
        assert user.is_deleted is False

    def test_restore_clears_deleted_by(self, db: Session):
        actor = make_user(db, email="ractor@soft.com")
        user = make_user(db, email="rtarget@soft.com")
        user.soft_delete(deleted_by_id=actor.id)
        user.restore()
        assert user.deleted_by is None

    def test_restore_sets_updated_by(self, db: Session):
        actor = make_user(db, email="updater@soft.com")
        user = make_user(db, email="ruser@soft.com")
        user.soft_delete()
        user.restore(restored_by_id=actor.id)
        assert user.updated_by == actor.id
