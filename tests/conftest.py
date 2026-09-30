"""Configuração do Pytest e fixtures compartilhadas.

Este conftest.py fornece:
    - Um banco de dados SQLite em memória para execuções de teste isoladas
    - Um TestClient do FastAPI com o banco de dados de teste injetado
    - Fixtures do tipo factory para criar usuários de teste

Os testes devem usar as fixtures deste arquivo em vez do banco de dados real.
O banco de dados real nunca é tocado durante a execução dos testes.
"""

from collections.abc import Generator

import pytest
from app.core.database import get_db
from app.core.security import hash_password
from app.main import app
from app.models import Base, User
from app.shared.enums import Role
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# Banco de dados em memória para testes
# ---------------------------------------------------------------------------
# StaticPool garante que a mesma conexão SQLite em memória seja reutilizada
# durante toda a sessão de testes, evitando erros de "tabela não encontrada" entre fixtures.

TEST_DATABASE_URL = "sqlite:///:memory:"

_test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSessionLocal = sessionmaker(bind=_test_engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Cria todas as tabelas uma única vez para toda a sessão de testes."""
    Base.metadata.create_all(bind=_test_engine)
    yield
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture()
def db() -> Generator[Session]:
    """Fornece uma sessão de banco de dados isolada para um único teste.

    Cada teste é executado dentro de uma transação que sofre rollback no final,
    garantindo o isolamento do teste sem recriar o esquema (schema).
    """
    connection = _test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db: Session) -> Generator[TestClient]:
    """Fornece um TestClient do FastAPI com o banco de dados de teste injetado.

    Sobrescreve a dependência `get_db` para que todos os manipuladores de rotas usem
    a sessão de teste isolada em vez do banco de dados real.
    """

    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Fábricas de Usuários (User factories)
# ---------------------------------------------------------------------------


def make_user(
    db: Session,
    *,
    email: str = "user@example.com",
    password: str = "password123",
    role: Role = Role.MANAGER,
    is_active: bool = True,
    company_id: int | None = None,
) -> User:
    """Cria e persiste um Usuário para fins de teste.

    Args:
        db:         Sessão do banco de dados de teste.
        email:      Endereço de e-mail do usuário.
        password:   Senha em texto puro (será feito o hash).
        role:       Papel (role) do usuário.
        is_active:  Se a conta do usuário está ativa.
        company_id: Associação opcional à empresa.

    Returns:
        A instância persistida do Usuário.
    """
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=role,
        is_active=is_active,
        company_id=company_id,
    )
    db.add(user)
    db.flush()  # atribui ID sem fazer commit
    return user


@pytest.fixture()
def admin_user(db: Session) -> User:
    """Um usuário ADMIN persistido para uso em testes."""
    return make_user(db, email="admin@example.com", role=Role.ADMIN)


@pytest.fixture()
def manager_user(db: Session) -> User:
    """Um usuário MANAGER persistido para uso em testes."""
    return make_user(db, email="manager@example.com", role=Role.MANAGER)
