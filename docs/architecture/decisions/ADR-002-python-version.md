# ADR-002: Versão do Python

## Status
Aceito

## Contexto
O projeto exige uma versão moderna, rápida e segura do Python, com suporte total às otimizações de desempenho e dicas de tipo (type hints) modernas.

## Decisão
Usaremos o **Python 3.13** (ou mais recente, adaptando para 3.14 se necessário, dependendo do ambiente).
Aproveitaremos seus recursos avançados de tipagem (como `|` para Unions, `str | None`) e melhorias nativas de desempenho.

## Consequências
- **Positivas**: Acesso aos recursos mais recentes da linguagem, melhor desempenho, sintaxe moderna de dicas de tipo sem necessidade de importar o módulo `typing` quando possível.
- **Negativas**: Alguns pacotes de terceiros mais antigos podem não ser totalmente compatíveis (ex: o `passlib` com o `bcrypt`, que exigiu soluções alternativas como o uso direto do `bcrypt`).
