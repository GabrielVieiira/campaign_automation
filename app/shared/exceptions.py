"""Exceções de domínio base para a aplicação.

Estas exceções representam condições de erro em nível de negócio.
Elas são capturadas na camada de API e traduzidas em respostas HTTP apropriadas.

Hierarquia:
    AppError                   — base para todos os erros da aplicação
    ├── AuthenticationError    — falhas de login / credenciais
    ├── AuthorizationError     — falhas de permissão / papel (role)
    ├── InvalidTokenError      — falhas de validação/decodificação de JWT
    ├── NotFoundError          — recurso não encontrado
    ├── ConflictError          — recurso duplicado
    └── IntegrationError       — falhas de serviços externos
        └── RedTrackError      — erros de integração específicos do RedTrack
"""


class AppError(Exception):
    """Classe base para todos os erros em nível de aplicação."""

    def __init__(self, message: str = "Ocorreu um erro inesperado") -> None:
        super().__init__(message)
        self.message = message


class AuthenticationError(AppError):
    """Levantada quando a autenticação falha (credenciais inválidas)."""

    def __init__(self, message: str = "A autenticação falhou") -> None:
        super().__init__(message)


class AuthorizationError(AppError):
    """Levantada quando um usuário não possui as permissões necessárias."""

    def __init__(self, message: str = "Permissões insuficientes") -> None:
        super().__init__(message)


class InvalidTokenError(AppError):
    """Levantada quando um token JWT é inválido, expirado ou malformado."""

    def __init__(self, message: str = "Token inválido ou expirado") -> None:
        super().__init__(message)


class NotFoundError(AppError):
    """Levantada quando o recurso solicitado não existe."""

    def __init__(self, resource: str = "Recurso", identifier: str | int | None = None) -> None:
        if identifier is not None:
            message = f"{resource} com o identificador '{identifier}' não foi encontrado"
        else:
            message = f"{resource} não foi encontrado"
        super().__init__(message)
        self.resource = resource
        self.identifier = identifier


class ConflictError(AppError):
    """Levantada ao tentar criar um recurso que já existe."""

    def __init__(self, message: str = "O recurso já existe") -> None:
        super().__init__(message)


class IntegrationError(AppError):
    """Levantada quando a chamada a um serviço externo falha."""

    def __init__(self, service: str, message: str) -> None:
        super().__init__(f"[{service}] {message}")
        self.service = service


class RedTrackError(IntegrationError):
    """Levantada quando a API do RedTrack retorna um erro."""

    def __init__(self, message: str) -> None:
        super().__init__("RedTrack", message)
