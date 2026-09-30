# Domínio de Landing Pages (Landings Domain)

## Visão Geral

As landing pages (landers) e pré-landing pages (pre-landers) são buscadas do RedTrack e usadas para configurar as campanhas.
No MVP, elas NÃO são armazenadas localmente.

## Estado Atual (MVP — Apenas Fundação)

**Nenhum endpoint de landing pages foi implementado ainda.**

O cliente do RedTrack possui o stub `get_landings()` pronto para uso.

## ⚠️ Nota Importante sobre Payloads da API

A estrutura do payload da API do RedTrack para landing pages NÃO foi totalmente analisada.
**Não invente nomes de campos nem suponha a estrutura da resposta.**

Antes de implementar as funcionalidades de landing pages:
1. Analise a resposta real de `GET /landings`
2. Defina o esquema `RawLanding` em `app/integrations/redtrack/schemas.py`
3. Determine como landers diferem de pre-landers no modelo de dados do RedTrack
4. Implemente os endpoints de listagem e seleção

## Funcionalidades Planejadas (Próximas Iterações)

1. `GET /landings` — listar as landing pages disponíveis no RedTrack
2. `GET /landings?type=pre_lander` — filtrar pre-landers (se a API suportar)

## Uso Conceitual

```
# Usuário seleciona um lander e/ou pre-lander
Lander A       → aplicado às → Campanhas [1, 2, 3]
Pre-Lander B   → aplicado às → Campanhas [4, 5]

# Ou ambos simultaneamente:
Lander A + Pre-Lander B → aplicados às → Campanhas [1, 2, 3]
```

O mecanismo de atualização será definido assim que o payload da API do RedTrack
para atualizações de campanhas for compreendido.
