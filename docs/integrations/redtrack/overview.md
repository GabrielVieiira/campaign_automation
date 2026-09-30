# Visão Geral da Integração com o RedTrack

O pacote `app/integrations/redtrack` isola todas as interações com a API externa do RedTrack.

## Estrutura
- `client.py`: Contém o `RedTrackClient` que usa o `httpx.AsyncClient` para fazer as requisições. Ele injeta automaticamente a `api_key` em todas as chamadas.
- `exceptions.py`: Define exceções específicas do RedTrack (`RedTrackAuthError`, `RedTrackRateLimitError`, etc.) que são levantadas pelo cliente com base nos códigos de status HTTP.
- `schemas.py`: (Futuro) Modelos do Pydantic representando os dados retornados pelo RedTrack, usados para análise e validação das respostas externas.

## Como Usar
Os services que precisarem de dados do RedTrack devem instanciar o `RedTrackClient` (ou tê-lo injetado) e chamar os seus métodos. O cliente lida com sessões HTTP, limites de taxa (no futuro) e tradução de erros.

```python
from app.integrations.redtrack.client import RedTrackClient
from app.core.config import get_settings

settings = get_settings()

async def fetch_campaigns():
    async with RedTrackClient(api_key=settings.redtrack_api_key) as client:
        try:
            campaigns = await client.get_campaigns()
            return campaigns
        except RedTrackAuthError:
            # Lidar com API Key inválida
            pass
```

## Segurança
A `api_key` é passada via string de consulta (query string) para o RedTrack (conforme exigido pela API deles). O cliente encapsula isso construindo a query string internamente, garantindo que a chave não seja acidentalmente vazada nos logs ou exposta em outras partes da aplicação.
