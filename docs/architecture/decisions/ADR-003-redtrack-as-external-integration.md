# ADR-003: RedTrack como Integração Externa

## Status
Aceito

## Contexto
A plataforma depende fortemente do RedTrack para dados de campanhas. No entanto, um acoplamento forte com a API do RedTrack em toda a aplicação dificultaria os testes, a manutenção, ou a substituição/adição de outros provedores de rastreamento no futuro.

## Decisão
O RedTrack será tratado estritamente como uma **integração externa** dentro do módulo `app/integrations/redtrack`.
Ele deve ter seu próprio Cliente (`RedTrackClient`), hierarquia de exceções (`RedTrackError`, `RedTrackAuthError`) e esquemas.

Nenhuma outra parte da aplicação (Services, Models, rotas da API) tem permissão para fazer chamadas HTTP brutas para o RedTrack. Todos devem usar o `RedTrackClient`.

## Consequências
- **Positivas**: Baixo acoplamento. Podemos facilmente mockar o `RedTrackClient` nos testes. Podemos trocar ou adicionar provedores de rastreamento futuramente criando uma interface genérica sobre os clientes.
- **Negativas**: Exige a manutenção de uma camada de mapeamento entre os esquemas do RedTrack e nossos esquemas internos de Domínio no futuro.
