# Domínio de Usuários (Users Domain)

## Visão Geral

Este domínio gerencia as contas de usuário e seu ciclo de vida dentro da plataforma.

## Contexto Delimitado (Bounded Context)

- Criação, desativação e exclusão lógica (soft deletion) de usuários
- Atribuição de papéis (ADMIN, MANAGER)
- Associação com uma Empresa (Company)

## Estado Atual (MVP)

No MVP, os usuários são criados manualmente (ex: por meio de um script seed ou inserção direta no banco de dados).
Uma API completa de gerenciamento de usuários será implementada em uma iteração subsequente.

## Arquivos Principais

| Arquivo | Responsabilidade |
|------|---------------|
| `app/models/user.py` | Modelo SQLAlchemy para Usuário (User) |
| `app/selectors/user_selector.py` | Consultas no BD (Queries) para Usuário |
| `app/shared/enums.py` | Enum de Papéis (Role) (ADMIN, MANAGER) |

## Papéis (Roles)

| Papel | Permissões |
|------|-------------|
| ADMIN | Gerenciar usuários, acessar configurações, configurar integrações |
| MANAGER | Consultar campanhas, executar operações de gerenciamento permitidas |

## Soft Delete (Exclusão Lógica)

Usuários são excluídos logicamente definindo a coluna `deleted_at`. Usuários apagados logicamente não podem fazer login.
Veja `app/models/base.py` e o ADR-004.

## Trabalhos Futuros

- `POST /users` — criar usuário (somente ADMIN)
- `PATCH /users/{id}` — atualizar usuário
- `DELETE /users/{id}` — exclusão lógica de usuário
- Fluxo de redefinição de senha
- Convite de usuário via e-mail
