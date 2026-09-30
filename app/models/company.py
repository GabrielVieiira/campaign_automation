"""Modelo de Empresa (Company).

Uma Empresa (Company) representa um inquilino (tenant) no sistema. No MVP, apenas uma única
empresa será usada, mas a arquitetura está preparada para multi-tenancy (múltiplos inquilinos).

Evolução futura:
    - Cada Empresa terá a sua própria RedTrackConfiguration (com chaves de API separadas).
    - Os usuários pertencerão a uma Empresa e verão apenas os dados dentro de sua própria Empresa.
    - O faturamento e o gerenciamento de planos podem ser adicionados no nível da Empresa.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin


class Company(SoftDeleteMixin, Base):
    """Representa uma organização/inquilino (tenant) na plataforma.

    Atributos:
        id:   Chave primária autoincrementada.
        name: Nome legível da empresa. Deve ser único.
        slug: Identificador seguro para URL. Deve ser único.
    """

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    # -------------------------------------------------------------------------
    # Relacionamentos (declarados aqui; retro-povoados nos modelos relacionados)
    # -------------------------------------------------------------------------
    users: Mapped[list[User]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User",
        back_populates="company",
        foreign_keys="User.company_id",
    )
    redtrack_configurations: Mapped[list[RedTrackConfiguration]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "RedTrackConfiguration",
        back_populates="company",
    )

    def __repr__(self) -> str:
        return f"<Company id={self.id} slug={self.slug!r}>"
