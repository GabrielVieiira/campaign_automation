# Domínio de Campanhas (Campaigns Domain)

## Visão Geral

As Campanhas (Campaigns) são a entidade principal gerenciada pela plataforma.
No MVP, as campanhas são buscadas diretamente do RedTrack e NÃO são armazenadas localmente.

## Estado Atual (MVP — Apenas Fundação)

**Nenhum endpoint de campanha foi implementado ainda.**

A base está pronta para implementação futura:
- O modelo `CampaignChangeLog` existe para trilha de auditoria
- O cliente do RedTrack possui o stub `get_campaigns()` pronto para uso

## ⚠️ Nota Importante sobre Payloads da API

A estrutura do payload da API do RedTrack para campanhas NÃO foi totalmente analisada.
**Não invente nomes de campos nem suponha a estrutura da resposta.**

Antes de implementar as funcionalidades de campanha:
1. Analise a resposta real de `GET /campaigns`
2. Defina o esquema `RawCampaign` em `app/integrations/redtrack/schemas.py`
3. Implemente o service e as rotas de campanha

## Funcionalidades Planejadas (Próximas Iterações)

1. `GET /campaigns` — listar todas as campanhas do RedTrack
2. `GET /campaigns/{id}` — obter uma única campanha
3. `POST /campaigns/bulk-update` — atualizar a landing page/pre-landing page em múltiplas campanhas
4. Log de auditoria via `CampaignChangeLog`

## Fluxo Conceitual (Futuro)

```
POST /api/v1/campaigns/bulk-update
    │
    ├── CampaignBulkUpdateRequest (esquema)
    │   ├── campaign_ids: list[str]
    │   ├── lander_id: str | None
    │   └── pre_lander_id: str | None
    │
    ├── CampaignService.bulk_update_landers(...)
    │   ├── validar se os campaign_ids estão acessíveis
    │   ├── chamar RedTrackClient para buscar o estado atual (payload_before)
    │   ├── chamar RedTrackClient para aplicar a atualização
    │   ├── salvar log no CampaignChangeLog
    │   └── retornar resultado
    │
    └── CampaignBulkUpdateResponse
```

## Relacionamento: Campanhas ↔ Landing Pages

O relacionamento exato entre campanhas e landers/pre-landers no RedTrack
deve ser determinado a partir da análise do payload da API.

Veja `app/integrations/redtrack/schemas.py` para o estado de espaço reservado atual (placeholder).
