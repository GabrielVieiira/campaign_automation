# ADR-001: Arquitetura em Camadas

## Status
Aceito

## Contexto
A aplicação precisa ser fácil de manter, escalável e simples de testar.
Uma arquitetura tradicional do tipo "Rotas -> Banco de Dados" (estilo Django) frequentemente resulta em lógica de negócios espalhada pelas views, tornando difícil testar de forma isolada e reaproveitar código.

## Decisão
Adotaremos uma arquitetura em camadas inspirada na Clean Architecture, adaptada para o FastAPI.
As camadas são estritamente separadas:
- **Camada de API (`app/api`)**: Lida com requisições HTTP, validação de entrada (Schemas) e respostas. NÃO contém lógica de negócios.
- **Camada de Aplicação (`app/services`)**: Orquestra a lógica de negócios e os casos de uso.
- **Camada de Dados (`app/models`, `app/selectors`)**: Gerencia a persistência de dados e as consultas. Os Seletores encapsulam todas as consultas do SQLAlchemy.
- **Camada de Integração (`app/integrations`)**: Lida com a comunicação com APIs externas (como o RedTrack).

## Consequências
- **Positivas**: Alta testabilidade, clara separação de responsabilidades, facilidade para mockar dependências externas ou consultas ao banco de dados.
- **Negativas**: Leve sobrecarga ao criar múltiplos arquivos para uma única funcionalidade (esquema, rota, serviço, seletor).

## Alternativas consideradas
- **Fat Routes (Rotas Obesas)**: Colocar toda a lógica nas rotas do FastAPI. Rejeitado porque se torna insustentável à medida que a aplicação cresce.
