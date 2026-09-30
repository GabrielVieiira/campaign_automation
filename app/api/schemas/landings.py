"""Esquemas (Schemas) da API para Landings e Pre-landings.

Estes são os modelos de saída que o nosso Front-end irá receber para listar as opções de Landings e Pre-Landings na plataforma.
"""

from pydantic import BaseModel, field_validator


class LandingResponse(BaseModel):
    """Modelo de exibição de uma única landing page / pre-landing."""

    id: str
    name: str | None = None
    title: str | None = (
        None  # O JSON mostra 'title' em vez de 'name', vamos garantir que suporte ambos
    )
    url: str | None = None
    type: str | None = None

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v: str | None) -> str | None:
        if v in ("l", "landing"):
            return "lander"
        if v in ("p", "prelanding"):
            return "prelander"
        return v

    model_config = {"extra": "ignore"}


class LandingPaginatedResponse(BaseModel):
    """Modelo de resposta paginada contendo o total de landings."""

    total: int
    items: list[LandingResponse]
