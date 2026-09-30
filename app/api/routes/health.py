"""Rota de verificação de integridade (health check).

Fornece um endpoint simples de "liveness" para balanceadores de carga e ferramentas de monitoramento.
Nenhuma autenticação é necessária.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificação de integridade (Health check)",
    description="Retorna o status de integridade da aplicação. Nenhuma autenticação é exigida.",
)
def health_check() -> HealthResponse:
    """Retorna o status de integridade da aplicação."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.app_env,
    )
