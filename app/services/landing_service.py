"""Camada de Serviços para Landings (Landing Pages e Pre-Landers).

Encapsula a lógica de negócios e orquestra a comunicação com o cliente RedTrack.
"""

from app.integrations.redtrack.client import RedTrackClient


async def get_all_landings(
    redtrack_client: RedTrackClient,
    page: int = 1,
    per: int = 50,
    title: str | None = None,
    type_filter: str | None = None,
) -> dict | list:
    """Busca todas as landings no RedTrack de forma paginada."""
    extra_params = {}
    if title:
        extra_params["title"] = title
    # Se houver filtro de tipo, precisamos buscar TODOS os registros,
    # filtrar em memória no Python para lidar com a inconsistência do RedTrack,
    # e paginar manualmente depois.
    if type_filter:
        data = await redtrack_client.get_landings(
            page=None, per=None, total_stat=True, extra_params=extra_params
        )
    else:
        data = await redtrack_client.get_landings(
            page=page, per=per, total_stat=True, extra_params=extra_params
        )

    # Normaliza o formato de resposta
    if isinstance(data, list):
        items = data
        total = len(data)
    elif isinstance(data, dict):
        items = data.get("items", data.get("data", data.get("landings", [])))
        total = data.get("total", len(items))
    else:
        items, total = [], 0

    # Filtro manual em memória caso solicitado
    if type_filter:
        allowed_types = ["l", "landing"] if type_filter == "lander" else ["p", "prelanding"]
        filtered = [item for item in items if item.get("type") in allowed_types]
        total = len(filtered)
        start = (page - 1) * per
        end = start + per
        items = filtered[start:end]

    return {"total": total, "items": items}
