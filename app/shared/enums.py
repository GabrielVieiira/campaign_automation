"""Enumerações compartilhadas usadas em toda a aplicação.

Centralizar as enumerações evita duplicação e garante consistência entre
a camada de domínio e os esquemas da API.
"""

from enum import StrEnum


class Role(StrEnum):
    """Papéis (Roles) de usuário que controlam a autorização dentro da plataforma.

    Os valores são armazenados como strings no banco de dados.

    ADMIN:
        Acesso total. Pode gerenciar usuários, acessar configurações e
        (em futuras versões) configurar integrações.

    MANAGER:
        Acesso operacional. Pode consultar campanhas e landings, e
        executar operações de gerenciamento permitidas.
    """

    ADMIN = "admin"
    MANAGER = "manager"
