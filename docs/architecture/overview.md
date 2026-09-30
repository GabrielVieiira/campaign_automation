# Visão Geral da Arquitetura

O backend da Plataforma de Gerenciamento de Campanhas é construído com Python 3.13+ e FastAPI. Ele segue estritamente uma Arquitetura em Camadas (Layered Architecture) projetada para facilitar testes, promover a clara separação de responsabilidades e permitir extensibilidade futura.

## Princípios Básicos
1. **Separação de Responsabilidades**: As rotas da API não contêm lógica de negócios. A lógica de negócios não sabe nada sobre requisições HTTP. Os modelos não sabem sobre APIs externas.
2. **Injeção de Dependências**: Dependências (como sessões de banco de dados, usuário atual, clientes) são injetadas nas rotas usando o sistema de injeção de dependência do FastAPI, tornando-as fáceis de mockar nos testes.
3. **Soft Deletes (Exclusão Lógica)**: Os dados raramente são excluídos permanentemente; usamos carimbos de data/hora `deleted_at` para auditoria e recuperação.
4. **Integrações Resilientes**: APIs externas (como a do RedTrack) são encapsuladas em clientes dedicados que traduzem erros HTTP em exceções específicas do domínio.

## Arquitetura de Alto Nível
```mermaid
graph TD
    Client[Web Frontend / Cliente] -->|Requisição HTTP| API[Camada de API (Rotas FastAPI)]
    API -->|Dados Validados| Services[Camada de Aplicação (Services)]
    Services -->|Consultas| Selectors[Camada de Dados (Selectors)]
    Services -->|Escritas| DB[(Banco de Dados)]
    Selectors -->|Leituras| DB
    Services -->|Ações Externas| Integrations[Camada de Integração (Clientes)]
    Integrations -->|HTTP| ExternalAPI[APIs Externas (ex: RedTrack)]
```

## Camadas
Veja [Detalhes das Camadas](layers.md) para uma explicação aprofundada das camadas (`app/api`, `app/services`, `app/selectors`, `app/integrations`, `app/models`).
