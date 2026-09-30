"""Rotas da API para Landings.

Este módulo expõe os endpoints para buscar landings e pre-landers no RedTrack.
"""

from fastapi import APIRouter, Depends, Query

from app.api.schemas.landings import LandingPaginatedResponse
from app.core.config import get_settings
from app.integrations.redtrack.client import RedTrackClient
from app.services import landing_service

router = APIRouter(prefix="/landings", tags=["Landings"])


async def get_redtrack_client() -> RedTrackClient:
    settings = get_settings()
    return RedTrackClient(api_key=settings.redtrack_api_key)


@router.get("", response_model=LandingPaginatedResponse)
async def list_landings(
    page: int = Query(1, ge=1, description="Número da página"),
    per: int = Query(50, ge=1, le=1000, description="Itens por página"),
    title: str | None = Query(None, description="Filtrar por nome"),
    type: str | None = Query(None, description="Filtrar por tipo ('lander' ou 'prelander')"),
    client: RedTrackClient = Depends(get_redtrack_client),
):
    """Retorna todas as landings do RedTrack de forma paginada e limpa."""
    return await landing_service.get_all_landings(
        redtrack_client=client, page=page, per=per, title=title, type_filter=type
    )
