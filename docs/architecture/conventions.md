# Convenções de Código

## Versão do Python
- **Python 3.13+**
- Evite `typing.Optional` e `typing.Union`. Use a sintaxe moderna: `str | None`, `int | str`.
- Evite `typing.List` e `typing.Dict`. Use os tipos nativos: `list[str]`, `dict[str, Any]`.

## Tipagem (Type Hinting)
- Todas as funções **devem** ter dicas de tipo (type hints) para os argumentos e os tipos de retorno.
- Usamos o `mypy` para impor uma tipagem estrita (exceto para testes, onde algumas regras são relaxadas).

## Linting & Formatação
- O código é formatado e analisado usando o **Ruff**.
- O comprimento máximo da linha é de 100 caracteres.
- Use aspas duplas `""` para strings.

## Banco de Dados & SQLAlchemy
- Use a sintaxe no estilo SQLAlchemy 2.0 (`Mapped`, `mapped_column`, `session.scalars(select(...))`).
- NADA de `session.query(Model)`. Use `select(Model)`.
- Imponha o Soft-Delete (Exclusão Lógica): Sempre verifique `is_deleted` ou `deleted_at IS NULL`, a menos que você precise explicitamente ignorar isso.

## Tratamento de Exceções
- As rotas da API capturam exceções de domínio (vindas de `app/shared/exceptions.py`) usando os manipuladores globais de exceção configurados em `app/main.py`.
- Os Services levantam exceções de domínio (ex: `AuthenticationError`, `NotFoundError`).
- Os Services **nunca** levantam `HTTPException`.
