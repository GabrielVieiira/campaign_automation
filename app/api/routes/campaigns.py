"""Rotas da API para Campanhas.

Este módulo expõe os endpoints para gerenciar campanhas no RedTrack.
"""

from typing import Any

from fastapi import APIRouter, Depends, Query

from app.api.schemas.campaigns import (
    BulkUpdateCampaignsRequest,
    BulkUpdateCampaignsResponse,
    CampaignPaginatedResponse,
    CampaignResponse,
    UpdateCampaignLandersRequest,
)
from app.core.config import get_settings
from app.integrations.redtrack.client import RedTrackClient
from app.services import campaign_service

router = APIRouter(prefix="/campaigns", tags=["Campanhas"])


async def get_redtrack_client() -> RedTrackClient:
    settings = get_settings()
    return RedTrackClient(api_key=settings.redtrack_api_key)


@router.put("/bulk-update", response_model=BulkUpdateCampaignsResponse)
async def bulk_update_campaigns(
    payload: BulkUpdateCampaignsRequest,
    client: RedTrackClient = Depends(get_redtrack_client),
):
    """Atualiza as landers/pre-landers de múltiplas campanhas de uma vez.

    Busca o modelo bruto do RedTrack para cada campanha, modifica os fluxos (streams)
    injetando os novos pesos/landers enviados no payload, e salva as alterações
    via PUT completo. Em caso de erro numa campanha, registra no relatório e continua.
    """
    return await campaign_service.bulk_update_campaign_landers(client, payload)


@router.put("/{campaign_id}/landers", response_model=dict)
async def update_campaign_landers(
    campaign_id: str,
    payload: UpdateCampaignLandersRequest,
    client: RedTrackClient = Depends(get_redtrack_client),
):
    """Atualiza as landers/pre-landers de uma única campanha."""
    # Transforma os objetos Pydantic em dicts puros preservando apenas o que o front enviou
    prelandings_dump = (
        [item.model_dump(exclude_unset=True) for item in payload.prelandings] if payload.prelandings else None
    )
    landings_dump = (
        [item.model_dump(exclude_unset=True) for item in payload.landings] if payload.landings else None
    )

    return await campaign_service.update_campaign_landers(
        redtrack_client=client,
        campaign_id=campaign_id,
        prelandings=prelandings_dump,
        landings=landings_dump,
        stream_id=payload.stream_id,
    )


@router.get("", response_model=CampaignPaginatedResponse)
async def list_campaigns(
    page: int = Query(1, ge=1, description="Número da página"),
    per: int = Query(50, ge=1, le=1000, description="Itens por página"),
    title: str | None = Query(None, description="Filtrar por nome"),
    client: RedTrackClient = Depends(get_redtrack_client),
):
    """Retorna todas as campanhas do RedTrack de forma paginada e limpa."""
    return await campaign_service.get_all_campaigns(
        redtrack_client=client, page=page, per=per, title=title
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    client: RedTrackClient = Depends(get_redtrack_client),
):
    """Retorna uma campanha específica do RedTrack pelo ID."""
    return await campaign_service.get_campaign(client, campaign_id)


@router.post("", response_model=dict[str, Any])
async def create_campaign(
    payload: dict[str, Any],
    client: RedTrackClient = Depends(get_redtrack_client),
):
    """Cria uma nova campanha no RedTrack.

    (Placeholder) No momento, o esquema do payload é livre, aguardando análise
    do formato da API do RedTrack.
    """
    return await campaign_service.create_campaign(client, payload)
