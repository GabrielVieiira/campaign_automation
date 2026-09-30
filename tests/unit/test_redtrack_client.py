"""Testes unitários para o RedTrackClient.

Os testes cobrem:
    - A inicialização do cliente valida a api_key.
    - _build_params injeta a api_key automaticamente.
    - get_campaigns lida com respostas bem-sucedidas (lista e dicionário).
    - get_landings lida com respostas bem-sucedidas (lista e dicionário).
    - O tratamento de erros traduz status HTTP para exceções de domínio:
        - 401/403 -> RedTrackAuthError
        - 404 -> RedTrackNotFoundError
        - 429 -> RedTrackRateLimitError
        - 500 -> RedTrackServerError
        - 400 -> RedTrackError (fallback)
"""

import pytest
from app.integrations.redtrack.client import RedTrackClient
from app.integrations.redtrack.exceptions import (
    RedTrackAuthError,
    RedTrackNotFoundError,
    RedTrackRateLimitError,
    RedTrackServerError,
)
from app.shared.exceptions import RedTrackError
from httpx import Response


class MockAsyncClient:
    """Um mock simples para httpx.AsyncClient para simular respostas da API do RedTrack."""
    def __init__(self, response: Response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def get(self, *args, **kwargs):
        return self._response


class TestRedTrackClientInit:
    def test_requires_api_key(self):
        with pytest.raises(ValueError, match="vazia"):
            RedTrackClient(api_key="")

    def test_strips_trailing_slash_from_base_url(self):
        client = RedTrackClient(api_key="key", base_url="https://api.redtrack.io/")
        assert client._base_url == "https://api.redtrack.io"

    def test_build_params_includes_api_key(self):
        client = RedTrackClient(api_key="secret")
        params = client._build_params()
        assert params["api_key"] == "secret"

    def test_build_params_merges_extra_params(self):
        client = RedTrackClient(api_key="secret")
        params = client._build_params({"limit": 10})
        assert params["api_key"] == "secret"
        assert params["limit"] == 10


class TestRedTrackClientGetCampaigns:
    @pytest.mark.asyncio
    async def test_returns_list_when_response_is_list(self, monkeypatch):
        client = RedTrackClient(api_key="key")
        mock_response = Response(200, json=[{"id": 1, "name": "C1"}])
        monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: MockAsyncClient(mock_response))

        result = await client.get_campaigns()
        assert len(result) == 1
        assert result[0]["name"] == "C1"

    @pytest.mark.asyncio
    async def test_returns_data_list_when_response_is_dict(self, monkeypatch):
        """Should return the actual dict if 'data' is not present at top level."""
        client = RedTrackClient(api_key="key")
        mock_response = Response(200, json={"items": [{"id": "2", "name": "C2"}], "total": 1})
        monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: MockAsyncClient(mock_response))

        result = await client.get_campaigns()
        assert isinstance(result, dict)
        assert result["items"][0]["name"] == "C2"


class TestRedTrackClientGetLandings:
    @pytest.mark.asyncio
    async def test_returns_list_when_response_is_list(self, monkeypatch):
        client = RedTrackClient(api_key="key")
        mock_response = Response(200, json=[{"id": 1, "name": "L1"}])
        monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: MockAsyncClient(mock_response))

        result = await client.get_landings()
        assert len(result) == 1
        assert result[0]["name"] == "L1"


class TestRedTrackClientErrorHandling:
    @pytest.mark.asyncio
    async def test_raises_auth_error_on_401(self, monkeypatch):
        client = RedTrackClient(api_key="bad")
        mock_response = Response(401, json={"error": "unauthorized"})
        monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: MockAsyncClient(mock_response))

        with pytest.raises(RedTrackAuthError):
            await client.get_campaigns()

    @pytest.mark.asyncio
    async def test_raises_not_found_on_404(self, monkeypatch):
        client = RedTrackClient(api_key="key")
        mock_response = Response(404)
        monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: MockAsyncClient(mock_response))

        with pytest.raises(RedTrackNotFoundError):
            await client.get_campaigns()

    @pytest.mark.asyncio
    async def test_raises_rate_limit_on_429(self, monkeypatch):
        client = RedTrackClient(api_key="key")
        mock_response = Response(429)
        monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: MockAsyncClient(mock_response))

        with pytest.raises(RedTrackRateLimitError):
            await client.get_campaigns()

    @pytest.mark.asyncio
    async def test_raises_server_error_on_500(self, monkeypatch):
        client = RedTrackClient(api_key="key")
        mock_response = Response(500)
        monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: MockAsyncClient(mock_response))

        with pytest.raises(RedTrackServerError):
            await client.get_campaigns()

    @pytest.mark.asyncio
    async def test_raises_generic_error_on_400(self, monkeypatch):
        client = RedTrackClient(api_key="key")
        mock_response = Response(400)
        monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: MockAsyncClient(mock_response))

        with pytest.raises(RedTrackError, match=r"\[RedTrack\] HTTP 400 recebido do RedTrack:"):
            await client.get_campaigns()
