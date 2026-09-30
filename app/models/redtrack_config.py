"""Modelo de configuração do RedTrack.

No MVP, uma única chave de API do RedTrack é lida da variável de ambiente
`REDTRACK_API_KEY`. Este modelo existe para preparar a arquitetura para
cenários multi-tenant (múltiplos inquilinos), onde cada Empresa (Company) terá suas próprias
credenciais do RedTrack.

Contrato de segurança:
    - A `api_key` NÃO é armazenada neste modelo no MVP.
    - Ela é lida exclusivamente do ambiente via `Settings.redtrack_api_key`.
    - Em uma versão futura, a api_key será armazenada criptografada em repouso
      (ex: usando um KMS ou criptografia em nível de aplicação).
    - A api_key NUNCA deve aparecer nas respostas da API, logs ou código-fonte.

Veja o ADR-003 para a justificativa de tratar o RedTrack como uma integração externa.
"""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin


class RedTrackConfiguration(SoftDeleteMixin, Base):
    """Armazena metadados sobre a integração RedTrack de uma Empresa (Company).

    No MVP:
        - Um registro por aplicação (única empresa, única conta).
        - A chave de API (api_key) verdadeira NÃO é armazenada aqui; ela vive no ambiente.

    Futuro:
        - Um registro por Empresa.
        - A api_key será armazenada criptografada (uma coluna será adicionada então).
        - Múltiplas contas por Empresa poderão ser suportadas.

    Atributos:
        id:         Chave primária autoincrementada.
        company_id: FK para a Empresa que possui esta configuração.
        label:      Rótulo legível (ex: "Conta Principal", "Marca A").
        base_url:   URL base da API do RedTrack. Por padrão, https://api.redtrack.io.
                    Permite apontar para diferentes instâncias do RedTrack, se necessário.
        is_active:  Se esta configuração está atualmente em uso.

    NÃO é armazenado aqui (intencionalmente):
        api_key:   Veja o contrato de segurança acima.
    """

    __tablename__ = "redtrack_configurations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Default",
    )

    base_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="https://api.redtrack.io",
    )

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # -------------------------------------------------------------------------
    # Relacionamentos (Relationships)
    # -------------------------------------------------------------------------
    company: Mapped[Company | None] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Company",
        back_populates="redtrack_configurations",
    )

    def __repr__(self) -> str:
        return f"<RedTrackConfiguration id={self.id} label={self.label!r} company_id={self.company_id}>"
