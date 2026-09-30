"""Plataforma de Gerenciamento de Campanhas — Ponto de entrada da aplicação FastAPI.

Visão geral da arquitetura:
    Requisição HTTP
        → Camada de API (rotas, esquemas, dependências)
        → Camada de Aplicação (serviços)
        → Camada de Domínio/Dados (seletores, modelos)
        → Camada de Integração (integrações/redtrack)

Veja docs/architecture/overview.md e .agents/AGENTS.md para a documentação completa.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, health
from app.core.config import get_settings
from app.shared.exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
)

settings = get_settings()


def create_app() -> FastAPI:
    """Fábrica (factory) da aplicação.

    Retorna uma instância configurada do FastAPI. Usar uma função de fábrica
    torna o aplicativo mais fácil de testar e evita importações circulares.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "API Backend para a Plataforma de Gerenciamento de Campanhas. "
            "Gerencia campanhas, landing pages, usuários e a integração com RedTrack."
        ),
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
    )

    # -------------------------------------------------------------------------
    # CORS — permissivo no desenvolvimento, restritivo na produção
    # As origens de produção devem ser configuradas via variáveis de ambiente
    # -------------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------------------------------------------------------
    # Manipuladores de exceções de domínio
    # Traduzem exceções de domínio em respostas HTTP na camada mais externa.
    # -------------------------------------------------------------------------

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(
        request: Request, exc: AuthenticationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message},
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_error_handler(
        request: Request, exc: AuthorizationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.message},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message},
        )

    from app.shared.exceptions import RedTrackError

    @app.exception_handler(RedTrackError)
    async def redtrack_error_handler(request: Request, exc: RedTrackError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Ocorreu um erro interno no servidor"},
        )

    # -------------------------------------------------------------------------
    # Roteadores (Routers)
    # -------------------------------------------------------------------------
    from app.api.routes import campaigns, landings

    app.include_router(health.router)
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(campaigns.router, prefix="/api/v1")
    app.include_router(landings.router, prefix="/api/v1")

    return app


app = create_app()
