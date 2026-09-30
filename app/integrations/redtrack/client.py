"""Cliente da API do RedTrack.

Este é o ÚNICO lugar na aplicação que se comunica com a
API do RedTrack. Nenhum outro módulo deve fazer requisições HTTP diretas ao RedTrack.

Autenticação:
    O RedTrack usa autenticação por parâmetro de consulta (query parameter):
        GET https://api.redtrack.io/campaigns?api_key=<chave>

    A api_key é injetada no momento da construção e NUNCA é exposta
    através de logs, exceções ou valores de retorno.

Uso:
    client = RedTrackClient(api_key=settings.redtrack_api_key)
    campaigns = await client.get_campaigns()

Endpoints atuais (confirmados):
    GET /campaigns  — lista de campanhas
    GET /landings   — lista de landings/pre-landers

Futuro:
    Endpoints adicionais serão adicionados quando suas respostas (payloads) forem analisadas.
    Operações de atualização em campanhas NÃO estão implementadas ainda.
"""

import logging

import httpx

from app.integrations.redtrack.exceptions import (
    RedTrackAuthError,
    RedTrackNotFoundError,
    RedTrackRateLimitError,
    RedTrackServerError,
)
from app.integrations.redtrack.schemas import RawCampaign

logger = logging.getLogger(__name__)

# Mascara a api_key em qualquer saída de log acidental
_MASKED = "***"


class RedTrackClient:
    """Cliente HTTP assíncrono para a API do RedTrack.

    Encapsula a autenticação, URL base e tratamento de erros.
    Toda a comunicação com o RedTrack deve passar por esta classe.

    Args:
        api_key:  Chave de API do RedTrack. Obtida de Settings.redtrack_api_key.
                  NUNCA deve ser registrada (logged), retornada em respostas ou armazenada.
        base_url: URL base da API do RedTrack. Por padrão https://api.redtrack.io.
        timeout:  Tempo limite da requisição HTTP em segundos.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.redtrack.io",
        timeout: float = 30.0,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("A api_key do RedTrack não pode estar vazia")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def _build_params(self, extra: dict | None = None) -> dict:
        """Constrói os parâmetros de consulta, sempre incluindo a api_key.

        A api_key é injetada aqui e nunca aparece em outro lugar.
        """
        params: dict = {"api_key": self._api_key}
        if extra:
            params.update(extra)
        return params

    def _handle_response_errors(self, response: httpx.Response) -> None:
        """Levanta uma exceção de domínio para respostas que não são 2xx.

        Args:
            response: O objeto de resposta do HTTPX.

        Raises:
            RedTrackAuthError:       HTTP 401 ou 403
            RedTrackNotFoundError:   HTTP 404
            RedTrackRateLimitError:  HTTP 429
            RedTrackServerError:     HTTP 5xx
            RedTrackError:           Qualquer outro erro não-2xx
        """
        if response.is_success:
            return

        status = response.status_code

        if status in (401, 403):
            raise RedTrackAuthError()
        if status == 404:
            raise RedTrackNotFoundError()
        if status == 429:
            raise RedTrackRateLimitError()
        if status >= 500:
            raise RedTrackServerError(status)

        # Trata outros erros inesperados da família 4xx
        from app.shared.exceptions import RedTrackError

        try:
            body = response.json()
        except Exception:
            body = response.text

        logger.error(f"RedTrack API Error: {status} - {body}")
        raise RedTrackError(f"HTTP {status} recebido do RedTrack: {body}")

    async def get_campaigns(
        self,
        page: int | None = None,
        per: int | None = None,
        total_stat: bool = True,
        extra_params: dict | None = None,
    ) -> dict | list:
        """Busca campanhas na API do RedTrack com paginação opcional.

        Args:
            page: Número da página.
            per: Quantidade de itens por página.
            total_stat: Se True, o RedTrack retorna {"total": X, "items": [...]}.
            extra_params: Parâmetros de consulta adicionais opcionais (ex: title).

        Returns:
            Resposta JSON pura do RedTrack (Lista ou Dicionário).
        """
        url = f"{self._base_url}/campaigns"

        # Constrói os parâmetros
        params = self._build_params(extra_params)
        if page is not None:
            params["page"] = page
        if per is not None:
            params["per"] = per
        if total_stat:
            params["total_stat"] = "true"

        logger.info(f"Buscando campanhas no RedTrack (page={page}, per={per})")

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                url,
                params=params,
                headers={"Accept": "application/json"},
            )

        self._handle_response_errors(response)
        data = response.json()

        # O RedTrack pode retornar uma lista ou um dicionário.
        # Como passamos total_stat=true por padrão, esperamos um dict {"total": X, "items": [...]}
        return data

    async def get_landings(
        self,
        page: int | None = None,
        per: int | None = None,
        total_stat: bool = True,
        extra_params: dict | None = None,
    ) -> dict | list:
        """Busca landings/pre-landers na API do RedTrack com paginação opcional."""
        url = f"{self._base_url}/landings"

        params = self._build_params(extra_params)
        if page is not None:
            params["page"] = page
        if per is not None:
            params["per"] = per
        if total_stat:
            params["total_stat"] = "true"

        logger.info(f"Buscando landings no RedTrack (page={page}, per={per})")

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                url,
                params=params,
                headers={"Accept": "application/json"},
            )

        self._handle_response_errors(response)
        data = response.json()

        return data

    async def get_campaign(self, campaign_id: str) -> dict:
        """Busca uma campanha específica na API do RedTrack pelo seu ID.

        Args:
            campaign_id: O ID da campanha.

        Returns:
            Dicionário com os dados da campanha.
        """
        url = f"{self._base_url}/campaigns/{campaign_id}"
        params = self._build_params()

        logger.info(f"Buscando campanha {campaign_id} no RedTrack")

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                url,
                params=params,
                headers={"Accept": "application/json"},
            )

        self._handle_response_errors(response)
        return response.json()

    async def update_campaign(self, campaign_id: str, campaign_data: dict) -> dict:
        """Atualiza uma campanha inteira via PUT.

        Args:
            campaign_id: O ID da campanha.
            campaign_data: O payload JSON completo modificado.

        Returns:
            Dicionário da resposta da API.
        """
        url = f"{self._base_url}/campaigns/{campaign_id}"
        params = self._build_params()

        logger.info(f"Atualizando campanha {campaign_id} no RedTrack")

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.put(
                url,
                params=params,
                json=campaign_data,
                headers={"Accept": "application/json"},
            )

        self._handle_response_errors(response)
        data = response.json()

        # Assim como a listagem, caso a API retorne um formato aninhado
        if isinstance(data, dict) and "data" in data:
            return data["data"]

        return data

    async def create_campaign(self, payload: dict) -> RawCampaign:
        """Cria uma nova campanha na API do RedTrack.

        Args:
            payload: Dicionário contendo os dados da campanha a ser criada.

        Returns:
            Dicionário com a resposta da API do RedTrack após a criação.
        """
        url = f"{self._base_url}/campaigns"
        params = self._build_params()

        logger.info("Criando nova campanha no RedTrack")

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                url,
                params=params,
                json=payload,
                headers={"Accept": "application/json"},
            )

        self._handle_response_errors(response)
        data = response.json()

        if isinstance(data, dict) and "data" in data:
            return data["data"]

        return data

    async def get_stream(self, stream_id: str) -> dict:
        """Busca um stream específico na API do RedTrack."""
        url = f"{self._base_url}/streams/{stream_id}"
        params = self._build_params()

        logger.info(f"Buscando stream {stream_id} no RedTrack")

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                url,
                params=params,
                headers={"Accept": "application/json"},
            )

        self._handle_response_errors(response)
        data = response.json()

        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data

    async def update_app_stream(self, stream_id: str, stream_data: dict) -> dict:
        """Atualiza um stream via PUT utilizando a API interna do frontend (app.redtrack.io).
        
        A API pública (api.redtrack.io) não suporta atualização de streams customizados 
        dentro de campanhas (retorna 404). O frontend do RedTrack utiliza este endpoint.
        """
        app_url = self._base_url.replace("api.redtrack.io", "app.redtrack.io/api")
        url = f"{app_url}/streams/{stream_id}"
        params = self._build_params()

        logger.info(f"Atualizando stream {stream_id} via app endpoint no RedTrack")

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.put(
                url,
                params=params,
                json=stream_data,
                headers={"Accept": "application/json"},
            )

        self._handle_response_errors(response)
        
        if response.status_code == 204 or not response.text:
            return {}
            
        data = response.json()
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data

    async def update_landing(self, landing_id: str, payload: dict) -> dict:
        """Atualiza uma landing page específica (ex: alterando o título)."""
        url = f"{self._base_url}/landings/{landing_id}"
        params = self._build_params()

        logger.info(f"Atualizando landing {landing_id} no RedTrack")

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.put(
                url,
                params=params,
                json=payload,
                headers={"Accept": "application/json"},
            )

        self._handle_response_errors(response)
        
        if response.status_code == 204 or not response.text:
            return {}

        data = response.json()
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data
