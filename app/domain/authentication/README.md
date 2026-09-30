# Domínio de Autenticação (Authentication Domain)

## Visão Geral

Este domínio gerencia a autenticação de usuários e o gerenciamento de sessões.

## Contexto Delimitado (Bounded Context)

O domínio de autenticação é responsável por:
- Validar credenciais de usuário (email + senha)
- Emitir tokens de acesso JWT
- Fornecer a dependência `get_current_user` para rotas protegidas
- Centralizar a autorização baseada em papéis (roles) através de `require_role`

## Arquivos Principais

| Arquivo | Responsabilidade |
|------|---------------|
| `app/services/auth_service.py` | Lógica de negócios: autenticar usuário, criar token |
| `app/core/security.py` | Primitivas criptográficas: hash, verificação, codificar/decodificar JWT |
| `app/api/dependencies/auth.py` | Dependências do FastAPI: `get_current_user`, `require_role` |
| `app/api/routes/auth.py` | Endpoints HTTP: `POST /auth/login`, `GET /auth/me` |
| `app/api/schemas/auth.py` | Contratos de requisição/resposta: `LoginRequest`, `TokenResponse` |

## Fluxo de Autenticação

```
POST /api/v1/auth/login
    │
    ├── LoginRequest (validação de esquema)
    │
    ├── auth_service.authenticate_user(db, email, password)
    │   ├── user_selector.get_user_by_email(db, email)
    │   ├── security.verify_password(plain, hashed)
    │   └── retorna User ou levanta AuthenticationError
    │
    ├── auth_service.create_token_for_user(user)
    │   └── security.create_access_token(sub=user.id, role=user.role)
    │
    └── retorna TokenResponse
```

## Fluxo de Rota Protegida

```
GET /api/v1/alguma-rota-protegida
    │
    ├── Bearer <token> extraído pelo HTTPBearer
    │
    ├── dependência get_current_user
    │   ├── security.decode_access_token(token)
    │   ├── user_selector.get_user_by_id(db, user_id)
    │   └── retorna User ou levanta HTTP 401
    │
    └── manipulador (handler) da rota recebe o User
```

## Autorização de Papel (Role)

```python
# Nos manipuladores de rotas (route handlers):
@router.delete("/users/{id}")
def delete_user(user=Depends(require_role(Role.ADMIN))): ...
```

Nunca use simplesmente `if user.role == Role.ADMIN:` dentro dos manipuladores de rota.

## Regras de Segurança

- As senhas recebem hash com bcrypt e nunca são armazenadas ou logadas em texto puro (plain text).
- Os tokens JWT são assinados com `JWT_SECRET_KEY` (a partir do ambiente).
- Os tokens embutem o papel (role) do usuário para evitar uma consulta extra ao DB por requisição.
- A expiração do token é controlada por `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`.

## Trabalhos Futuros

- Endpoint de atualização de token (Refresh token)
- Fluxo de redefinição de senha
- Bloqueio de conta após N tentativas falhas
- Autenticação de dois fatores (MFA)
