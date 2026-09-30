"""Engine do banco de dados, fábrica de sessões (session factory) e base declarativa.

Este módulo configura o SQLAlchemy para trabalhar tanto com SQLite (desenvolvimento)
quanto com PostgreSQL (produção) sem exigir alterações na camada de domínio.

A mudança entre bancos de dados é feita exclusivamente por meio da variável de
ambiente DATABASE_URL. Veja o ADR-005 para entender a lógica.
"""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


def _build_engine() -> Engine:
    """Constrói a engine do SQLAlchemy a partir das configurações atuais.

    O SQLite requer `check_same_thread=False` para funcionar com o modelo de
    threads do FastAPI. Este parâmetro (connect_arg) é ignorado pelo PostgreSQL.

    Para o PostgreSQL, a configuração do pool é ajustada para uso em produção.
    """
    settings = get_settings()
    url = settings.database_url

    connect_args: dict = {}

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        engine = create_engine(
            url,
            connect_args=connect_args,
            echo=settings.is_development,
        )
        # Ativa o modo WAL e a imposição de chaves estrangeiras (foreign keys) para o SQLite
        _register_sqlite_pragmas(engine)
        return engine

    # PostgreSQL / outro RDBMS — configurações de pool orientadas à produção
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,
    )


def _register_sqlite_pragmas(engine: Engine) -> None:
    """Registra os PRAGMAs específicos do SQLite em cada nova conexão."""

    @event.listens_for(engine, "connect")
    def set_sqlite_pragmas(dbapi_connection, connection_record) -> None:  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


# ---------------------------------------------------------------------------
# Base declarativa (Declarative base)
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Classe base para todos os modelos ORM do SQLAlchemy."""

    pass


# ---------------------------------------------------------------------------
# Engine e fábrica de sessões (Session factory)
# ---------------------------------------------------------------------------
# Estes são singletons em nível de módulo. Testes podem sobrescrever usando monkeypatch
# em `app.core.database.engine` e `app.core.database.SessionLocal`.

engine = _build_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Dependência do FastAPI
# ---------------------------------------------------------------------------


def get_db() -> Generator[Session]:
    """Fornece uma sessão do banco de dados (yield) e garante seu fechamento após a requisição.

    Uso no FastAPI:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
