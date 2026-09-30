"""Camada de Serviços para Campanhas (Campaigns).

Encapsula a lógica de negócios e orquestra a comunicação com o cliente RedTrack.
"""

from app.api.schemas.campaigns import BulkUpdateCampaignsRequest
from app.integrations.redtrack.client import RedTrackClient
from app.integrations.redtrack.schemas import RawCampaign
from app.shared.exceptions import ConflictError


async def get_all_campaigns(
    redtrack_client: RedTrackClient, page: int = 1, per: int = 50, title: str | None = None
) -> dict | list:
    """Busca todas as campanhas no RedTrack de forma paginada."""
    extra_params = {}
    if title:
        extra_params["title"] = title

    data = await redtrack_client.get_campaigns(
        page=page, per=per, total_stat=True, extra_params=extra_params
    )

    # Normaliza a resposta do RedTrack para evitar que o Pydantic quebre (Erro 500)
    # A API do RedTrack pode ser instável no formato dependendo da versão
    if isinstance(data, list):
        return {"total": len(data), "items": data}

    if isinstance(data, dict):
        items = data.get("items", data.get("data", data.get("campaigns", [])))
        total = data.get("total", len(items))
        return {"total": total, "items": items}

    return {"total": 0, "items": []}


async def get_campaign(redtrack_client: RedTrackClient, campaign_id: str) -> dict:
    """Busca uma campanha específica no RedTrack pelo seu ID."""
    return await redtrack_client.get_campaign(campaign_id)


async def update_campaign_landers(
    redtrack_client: RedTrackClient,
    campaign_id: str,
    prelandings: list[dict] | None,
    landings: list[dict] | None,
    stream_id: str | None = None,
) -> dict:
    """Atualiza as landers/pre-landers de uma campanha.
    
    Como a API pública do RedTrack falha silenciosamente ao tentar atualizar streams
    dentro do payload da campanha, esta função utiliza o endpoint interno do app
    para atualizar o funil, e o endpoint global de landings para atualizar os nomes.
    """
    # 1. GET completo na Campanha para obter o stream_inner
    raw_campaign = await redtrack_client.get_campaign(campaign_id)
    if "data" in raw_campaign and isinstance(raw_campaign["data"], dict):
        raw_campaign = raw_campaign["data"]

    streams = raw_campaign.get("streams", [])

    if not streams:
        raise ConflictError("Campanha não possui nenhum funil (stream).")

    # Encontra o stream correto
    stream_obj = None
    if stream_id:
        for s in streams:
            if s.get("id") == stream_id or (s.get("stream") and s["stream"].get("id") == stream_id):
                stream_obj = s
                break
        if not stream_obj:
            raise ConflictError(f"Stream {stream_id} não encontrado na campanha.")
    else:
        # Verifica regra do MVP para fallback
        if len(streams) > 1:
            raise ConflictError("Campanha possui múltiplos funis e nenhum stream_id foi fornecido.")
        stream_obj = streams[0]

    # O RedTrack aninha os dados do funil dentro de "stream"
    target_stream = stream_obj.get("stream", stream_obj)
    target_stream_id = target_stream.get("id")

    # 2. Mescla os novos dados (pesos, filtros) preservando os não informados, mas SOBRESCREVE a lista
    def _merge_stream_items(existing_items: list[dict], new_items: list[dict]) -> list[dict]:
        existing_map = {item.get("id"): item for item in existing_items}
        
        final_items = []
        for new_item in new_items:
            item_id = new_item.get("id")
            if not item_id:
                continue
                
            if item_id in existing_map:
                # Copia a antiga para preservar os campos que não vieram
                merged_item = existing_map[item_id].copy()
                
                # Atualiza peso
                if new_item.get("weight") is not None:
                    merged_item["weight"] = new_item["weight"]
                
                # Atualiza filtros apenas se a chave filters vier preenchida com algo
                if new_item.get("filters"):
                    merged_item["filters"] = new_item["filters"]
                
                # Se houver 'name', preservamos localmente (apesar de sabermos que é atualizado globalmente no passo 4)
                if new_item.get("name") and str(new_item["name"]).strip():
                    merged_item["name"] = new_item["name"]
                    
                final_items.append(merged_item)
            else:
                # É uma nova landing sendo injetada no funil, inicializamos defaults se faltar
                new_item_copy = new_item.copy()
                if new_item_copy.get("weight") is None:
                    new_item_copy["weight"] = 100
                if new_item_copy.get("filters") is None:
                    new_item_copy["filters"] = {}
                final_items.append(new_item_copy)
                
        return final_items

    if prelandings is not None:
        target_stream["prelandings"] = _merge_stream_items(target_stream.get("prelandings", []), prelandings)

    if landings is not None:
        target_stream["landings"] = _merge_stream_items(target_stream.get("landings", []), landings)

    # 3. Atualiza o funil (Stream) para refletir os novos pesos e filtros
    # O RedTrack aceita apenas no endpoint interno /app.redtrack.io/api
    await redtrack_client.update_app_stream(target_stream_id, target_stream)

    # 3. O endpoint de stream NÃO atualiza o nome global das landings.
    # Precisamos iterar sobre as listas e fazer um PUT /landings/{id} se houver 'name'
    async def _update_names(items: list[dict] | None):
        if not items:
            return
        for item in items:
            name = item.get("name")
            if name and isinstance(name, str) and name.strip():
                # No RedTrack, a propriedade global da landing se chama 'title'
                await redtrack_client.update_landing(item["id"], {"title": name})

    await _update_names(prelandings)
    await _update_names(landings)

    # Retorna o stream atualizado (ou um status de sucesso)
    return target_stream


async def bulk_update_campaign_landers(
    redtrack_client: RedTrackClient, payload: BulkUpdateCampaignsRequest
) -> dict:
    """Atualiza as landers/pre-landers de múltiplas campanhas em lote."""
    success_count = 0
    failed_count = 0
    ignored_count = 0
    errors = []

    prelandings_dump = (
        [item.model_dump(exclude_unset=True) for item in payload.prelandings] if payload.prelandings else None
    )
    landings_dump = (
        [item.model_dump(exclude_unset=True) for item in payload.landings] if payload.landings else None
    )

    for campaign_id in payload.campaign_ids:
        try:
            await update_campaign_landers(
                redtrack_client, 
                campaign_id, 
                prelandings_dump, 
                landings_dump,
                stream_id=payload.stream_id
            )
            success_count += 1
        except ConflictError as e:
            ignored_count += 1
            errors.append({"campaign_id": campaign_id, "reason": e.message})
        except Exception as e:
            failed_count += 1
            errors.append({"campaign_id": campaign_id, "reason": str(e)})

    return {
        "success_count": success_count,
        "failed_count": failed_count,
        "ignored_count": ignored_count,
        "errors": errors,
    }


async def create_campaign(redtrack_client: RedTrackClient, payload: dict) -> RawCampaign:
    """Cria uma nova campanha no RedTrack.

    Por enquanto, é apenas um stub (esqueleto) que aceita qualquer dicionário,
    até definirmos o esquema real do payload.
    """
    return await redtrack_client.create_campaign(payload)
