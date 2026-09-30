"""Plataforma de Gerenciamento de Campanhas — Configuração central.

Lê todas as configurações de variáveis de ambiente. Use `.env` para desenvolvimento local.
Nunca codifique segredos de forma rígida (hard-code) neste arquivo.
"""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente.

    Todos os campos são lidos do ambiente (ou do arquivo `.env`).
    Campos obrigatórios não têm valor padrão e gerarão uma exceção na inicialização se estiverem ausentes.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Aplicação
    # -------------------------------------------------------------------------
    app_name: str = "Campaign Management Platform"
    app_version: str = "0.1.0"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # -------------------------------------------------------------------------
    # Banco de Dados
    # -------------------------------------------------------------------------
    database_url: str = "sqlite:///./campaign_management.db"

    # -------------------------------------------------------------------------
    # Segurança / JWT
    # -------------------------------------------------------------------------
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # -------------------------------------------------------------------------
    # Integração com RedTrack
    # NOTA: No MVP, é usada uma única chave de API (lida do ambiente).
    #       Futuro: cada Empresa (Company) terá a sua própria RedTrackConfiguration com
    #       as credenciais armazenadas de forma segura (criptografadas em repouso).
    # -------------------------------------------------------------------------
    redtrack_api_key: str
    redtrack_base_url: str = "https://api.redtrack.io"

    # -------------------------------------------------------------------------
    # Propriedades computadas
    # -------------------------------------------------------------------------
    @property
    def is_production(self) -> bool:
        """Verdadeiro (True) quando rodando em ambiente de produção."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Verdadeiro (True) quando rodando em ambiente de desenvolvimento."""
        return self.app_env == "development"

    @field_validator("jwt_secret_key")
    @classmethod
    def jwt_secret_key_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("JWT_SECRET_KEY não pode estar vazio")
        return v


@lru_cache
def get_settings() -> Settings:
    """Retorna as configurações da aplicação em cache.

    O uso do `lru_cache` garante que a classe Settings seja instanciada apenas uma vez por processo.
    Em testes, chame `get_settings.cache_clear()` antes de sobrescrever com
    um `.env` específico de testes ou usar monkeypatching.
    """
    return Settings()
