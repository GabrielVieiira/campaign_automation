"""Esquemas (Schemas) da API para Campanhas.

Estes são os modelos de saída que o nosso Front-end irá receber,
já limpos, formatados e sem o peso de campos não utilizados da API externa.
"""

from pydantic import BaseModel


class CampaignSubItem(BaseModel):
    """Representa um Pre-Lander, Lander ou Oferta dentro de uma campanha."""

    id: str
    name: str | None = None
    weight: int | None = None


class StreamInner(BaseModel):
    """Objeto interno do fluxo que contém os itens da campanha."""

    prelandings: list[CampaignSubItem] = []
    landings: list[CampaignSubItem] = []
    offers: list[CampaignSubItem] = []

    model_config = {"extra": "ignore"}


class CampaignStream(BaseModel):
    """Representa a configuração de fluxo (stream) de uma campanha (wrapper)."""

    id: str
    stream: StreamInner | None = None

    model_config = {"extra": "ignore"}


class CampaignResponse(BaseModel):
    """Modelo de exibição de uma única campanha, enxuto (sem os milhares de filtros)."""

    id: str
    title: str | None = None
    status: int | None = None
    domain_url: str | None = None
    trackback_url: str | None = None
    streams: list[CampaignStream] = []

    model_config = {"extra": "ignore"}


class CampaignPaginatedResponse(BaseModel):
    """Modelo de resposta paginada contendo o total de itens (se requisitado)."""

    total: int
    items: list[CampaignResponse]


class CampaignStreamItemInput(BaseModel):
    """Representa um item (lander/prelander) sendo injetado numa campanha."""

    id: str
    weight: int | None = None
    name: str | None = None
    filters: dict | None = None


class BulkUpdateCampaignsRequest(BaseModel):
    """Payload de entrada para atualizar campanhas em lote (Bulk Update)."""

    campaign_ids: list[str]
    stream_id: str | None = None
    prelandings: list[CampaignStreamItemInput] | None = None
    landings: list[CampaignStreamItemInput] | None = None


class UpdateCampaignLandersRequest(BaseModel):
    """Payload de entrada para atualizar as landers de uma única campanha."""

    stream_id: str | None = None
    prelandings: list[CampaignStreamItemInput] | None = None
    landings: list[CampaignStreamItemInput] | None = None


class BulkUpdateErrorDetail(BaseModel):
    """Detalhes de erro em uma atualização em lote."""

    campaign_id: str
    reason: str


class BulkUpdateCampaignsResponse(BaseModel):
    """Relatório final de uma operação de atualização em lote."""

    success_count: int
    failed_count: int
    ignored_count: int
    errors: list[BulkUpdateErrorDetail]
