"""Exceções da integração com o RedTrack.

Estas exceções estendem a hierarquia base IntegrationError definida em
`app/shared/exceptions.py` com condições de erro específicas do RedTrack.
"""

from app.shared.exceptions import RedTrackError


class RedTrackAuthError(RedTrackError):
    """Levantada quando a API do RedTrack rejeita a chave de API (HTTP 401/403)."""

    def __init__(self) -> None:
        super().__init__("Falha na autenticação — verifique a REDTRACK_API_KEY")


class RedTrackRateLimitError(RedTrackError):
    """Levantada quando o limite de taxa (rate limit) da API do RedTrack é excedido (HTTP 429)."""

    def __init__(self) -> None:
        super().__init__("Limite de taxa excedido — tente novamente após um intervalo")


class RedTrackNotFoundError(RedTrackError):
    """Levantada quando um recurso solicitado do RedTrack não existe (HTTP 404)."""

    def __init__(self, resource: str = "Recurso") -> None:
        super().__init__(f"{resource} não encontrado no RedTrack")


class RedTrackServerError(RedTrackError):
    """Levantada quando o RedTrack retorna um erro de servidor 5xx."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"Erro no servidor do RedTrack (HTTP {status_code})")
