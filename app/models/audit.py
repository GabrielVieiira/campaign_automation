"""Modelos de Auditoria — log de alterações de campanha.

Este módulo define a trilha de auditoria para as operações de gerenciamento de campanhas.
A implementação completa do registro de auditoria (preenchimento, consultas, relatórios)
será adicionada em iterações subsequentes, à medida que os recursos de gerenciamento de
campanhas forem construídos.

O que este log irá capturar no futuro:
    - Quem realizou a ação (user_id)
    - Quando ocorreu (executed_at)
    - A qual empresa (company) a operação pertence
    - Qual operação foi realizada (ex: UPDATE_LANDER, UPDATE_PRE_LANDER)
    - Quais campanhas foram afetadas (lista de IDs externos do RedTrack)
    - O estado antes da alteração (snapshot em JSON)
    - O estado após a alteração (snapshot em JSON)
    - Se a operação foi bem-sucedida ou falhou
    - A mensagem de erro em caso de falha

Notas de design:
    - campaign_ids é armazenado como JSON para suportar operações em lote (bulk)
      afetando várias campanhas em um único registro de auditoria.
    - payload_before / payload_after armazenam snapshots (instantâneos) brutos
      da API do RedTrack. Seus esquemas serão definidos quando os payloads da API forem analisados.
    - Esta tabela é do tipo "apenas adição" (append-only); registros nunca devem ser atualizados ou excluídos.
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class OperationStatus(str):
    """Constantes de status para as entradas do log de alterações de campanha.

    Usar uma classe de string pura (não enum) intencionalmente para permitir que
    o conjunto de status seja expandido sem precisar de uma migration no banco de dados.
    """

    PENDING = "pending"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"


class CampaignChangeLog(TimestampMixin, Base):
    """Registro de auditoria imutável para operações de gerenciamento de campanhas.

    Esta tabela é "apenas adição" (append-only). Os registros não devem ser atualizados
    ou excluídos fisicamente. Ela fornece rastreabilidade para todas as modificações de campanha em massa.

    Atributos:
        id:             Chave primária autoincrementada.
        user_id:        FK para o Usuário (User) que iniciou a operação.
        company_id:     FK para o contexto de Empresa (Company) da operação.
        operation:      Rótulo curto para o tipo de operação (ex: "UPDATE_LANDER").
        campaign_ids:   Array JSON contendo os IDs das campanhas afetadas no RedTrack.
        payload_before: Snapshot (instantâneo) JSON do estado antes da operação.
                        O esquema será definido (TBD) após a análise da API do RedTrack.
        payload_after:  Snapshot JSON do estado após a operação.
                        O esquema será definido (TBD) após a análise da API do RedTrack.
        status:         Resultado: pending (pendente) | success (sucesso) | partial (parcial) | failure (falha).
        error_message:  Detalhes do erro se o status for falha ou parcial.
        executed_at:    Quando a operação foi tentada (por padrão, usa o horário atual).
    """

    __tablename__ = "campaign_change_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    company_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    operation: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Array JSON com os IDs das campanhas externas no RedTrack (strings ou ints a serem definidos)
    campaign_ids: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Snapshots (instantâneos) JSON brutos — o esquema será determinado após análise da API do RedTrack
    payload_before: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_after: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=OperationStatus.PENDING,
        index=True,
    )

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # -------------------------------------------------------------------------
    # Relacionamentos (referências apenas leitura; sem exclusão em cascata)
    # -------------------------------------------------------------------------
    user: Mapped[User | None] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User",
        foreign_keys=[user_id],
    )

    def __repr__(self) -> str:
        return (
            f"<CampaignChangeLog id={self.id} operation={self.operation!r} status={self.status!r}>"
        )
