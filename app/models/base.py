"""Mixin base para modelos, fornecendo timestamps, exclusão lógica (soft delete) e rastreamento de autoria.

Todas as entidades persistentes que podem ser logicamente removidas DEVEM herdar de
`SoftDeleteMixin`. Entidades que precisam apenas de carimbos de data/hora (timestamps) devem usar `TimestampMixin`.

Veja o ADR-004 para a justificativa por trás da exclusão lógica (soft delete).

Convenções:
    created_at  — definido automaticamente no INSERT
    updated_at  — atualizado automaticamente a cada UPDATE
    deleted_at  — NULL significa ativo; não-NULL significa excluído logicamente (soft-deleted)
    created_by  — FK para users.id (anulável, definido pela camada de aplicação)
    updated_by  — FK para users.id (anulável, definido pela camada de aplicação)
    deleted_by  — FK para users.id (anulável, definido pela camada de aplicação)

Consultas (Querying):
    Use `SoftDeleteMixin.filter_active(query)` para excluir linhas apagadas logicamente,
    ou use a propriedade `is_deleted` para verificar uma única instância.
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TimestampMixin:
    """Adiciona as colunas `created_at` e `updated_at` a qualquer modelo.

    Ambas as colunas são armazenadas como datetimes em UTC (cientes de fuso horário).
    `updated_at` é atualizado automaticamente pelo banco de dados a cada alteração.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin(TimestampMixin):
    """Estende o TimestampMixin com exclusão lógica e colunas de autoria.

    Entidades NÃO devem ser excluídas fisicamente; em vez disso, defina `deleted_at`
    para o carimbo de data/hora (timestamp) atual. Todas as consultas normais devem
    filtrar por `deleted_at IS NULL`.

    As colunas `created_by`, `updated_by` e `deleted_by` referenciam
    `users.id` e são definidas pela camada de serviço/aplicação antes do commit.
    Elas são anuláveis (nullable) para suportar cenários de inicialização (ex: seed data)
    e operações iniciadas pelo sistema onde não há um usuário autenticado presente.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
    )

    created_by: Mapped[int | None] = mapped_column(
        Integer,
        # FK lógica para users.id — imposta na camada de aplicação, não como uma restrição (constraint) de BD,
        # para evitar dependência circular entre tabelas que herdam deste mixin.
        nullable=True,
        default=None,
    )
    updated_by: Mapped[int | None] = mapped_column(
        Integer,
        # FK lógica para users.id — veja o comentário de created_by acima.
        nullable=True,
        default=None,
    )
    deleted_by: Mapped[int | None] = mapped_column(
        Integer,
        # FK lógica para users.id — veja o comentário de created_by acima.
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        """Retorna True (Verdadeiro) se este registro foi excluído logicamente (soft-deleted)."""
        return self.deleted_at is not None

    def soft_delete(self, deleted_by_id: int | None = None) -> None:
        """Marca este registro como excluído.

        Args:
            deleted_by_id: O ID do usuário que está realizando a exclusão.
                           Passe None para exclusões iniciadas pelo sistema.
        """
        self.deleted_at = datetime.now(UTC)
        self.deleted_by = deleted_by_id

    def restore(self, restored_by_id: int | None = None) -> None:
        """Restaura um registro que sofreu exclusão lógica (soft-deleted).

        Args:
            restored_by_id: O ID do usuário que está realizando a restauração.
        """
        self.deleted_at = None
        self.deleted_by = None
        self.updated_by = restored_by_id


# Re-exporta Base para que os modelos precisem importar apenas de app.models.base
__all__ = ["Base", "TimestampMixin", "SoftDeleteMixin"]
