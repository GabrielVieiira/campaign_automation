# Customizações do Agente (Agent Customizations)

Este arquivo dita como o Antigravity e outros agentes devem se comportar ao trabalhar neste projeto.

## Regra de Idioma (MUITO IMPORTANTE)
- **Idioma**: TODOS os comentários, docstrings (strings de documentação) no código, arquivos Markdown (`.md`), mensagens de commit e explicações de PRs devem ser escritos EXCLUSIVAMENTE em Português do Brasil (pt-BR).

## Diretrizes de Arquitetura
- **Camadas Estritas**: Impor a separação estrita entre `api`, `services`, `selectors`, `models` e `integrations`.
- **Injeção de Dependências**: As dependências do FastAPI DEVEM ser usadas para passar `Session` e `User` para as rotas. Os Services devem receber `Session` como um argumento normal.
- **Tratamento de Erros**: As rotas da API capturam exceções; os Services levantam exceções de domínio (de `app.shared.exceptions`). NÃO levante `HTTPException` dentro dos Services.
- **Banco de Dados**: Use os paradigmas do SQLAlchemy 2.0 (`Mapped`, `mapped_column`, `select`, `session.scalars`). NUNCA use `session.query`.
- **Soft Deletes (Exclusão Lógica)**: Quase todos os dados são excluídos logicamente (soft delete). Os seletores devem, por padrão, filtrar os dados usando `deleted_at IS NULL`.

## Escolhas de Tecnologia
- **Type Hints (Dicas de Tipo)**: Evite usar `typing.Optional`/`typing.Union`/`typing.List`. Use o pipe `|` e as coleções nativas `list`, `dict`.
- **Autenticação**: Use `bcrypt` para o hash de senhas (diretamente, sem passlib). Use `PyJWT` para os tokens JWT. Não use `python-jose`.
- **Formatação**: Respeite as configurações do Ruff (tamanho máximo da linha: 100, aspas duplas).

## Integração com RedTrack
- Trate o RedTrack como um fornecedor terceirizado. Todas as interações com a API DEVEM passar por `app/integrations/redtrack/client.py`.
- Nunca vaze URLs ou requisitos de `api_key` da API do RedTrack para os Services ou rotas da API.
