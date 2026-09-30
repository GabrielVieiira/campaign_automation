"""Modelos de Usuário e Papel (Role).

Usuários são os atores autenticados do sistema. Cada Usuário pertence a
uma Empresa (Company) e possui um Papel (Role) que rege suas permissões.

As regras de autorização são centralizadas em `app/api/dependencies/auth.py` e
`app/services/auth_service.py`. As verificações de papel (Role) NÃO devem estar
espalhadas pelo código como comparações puras `if user.role == ...`.
"""

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin
from app.shared.enums import Role


class User(SoftDeleteMixin, Base):
    """Representa um usuário autenticado da plataforma.

    Atributos:
        id:              Chave primária autoincrementada.
        email:           Identificador único de login.
        hashed_password: Hash gerado pelo bcrypt. A senha em texto puro NUNCA é armazenada.
        is_active:       Quando Falso (False), o login é rejeitado mesmo com credenciais válidas.
        role:            Papel de autorização (ADMIN | MANAGER).
        company_id:      FK (Chave Estrangeira) para a Empresa (Company) à qual este usuário pertence.

    As FKs de autoria (created_by, updated_by, deleted_by) são herdadas de
    SoftDeleteMixin e referenciam esta mesma tabela (autorreferencial).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    role: Mapped[Role] = mapped_column(String(50), nullable=False, default=Role.MANAGER)

    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Relacionamentos (Relationships)
    # -------------------------------------------------------------------------
    company: Mapped[Company | None] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Company",
        back_populates="users",
        foreign_keys=[company_id],
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"
