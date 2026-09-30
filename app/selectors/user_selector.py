"""Seletores de usuário — encapsulam todas as consultas de banco de dados relacionadas ao Usuário (User).

Os seletores são o único lugar onde as consultas para uma dada entidade são escritas.
Nenhuma outra camada (rotas, serviços, integrações) deve consultar o Usuário diretamente.

Regras:
    - Seletores recebem uma Sessão do SQLAlchemy como o primeiro argumento.
    - Seletores retornam instâncias do modelo de domínio (objetos ORM) ou None.
    - Seletores NÃO executam commit ou rollback de transações.
    - Seletores filtram registros apagados logicamente (soft-deleted) por padrão.
    - Passe `include_deleted=True` para acessar explicitamente registros excluídos logicamente.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_id(
    db: Session,
    user_id: int,
    *,
    include_deleted: bool = False,
) -> User | None:
    """Retorna um Usuário pela chave primária, ou None se não encontrado.

    Args:
        db:              Sessão ativa do banco de dados.
        user_id:         A chave primária do usuário.
        include_deleted: Se True, também busca registros com exclusão lógica.

    Returns:
        A instância do Usuário, ou None.
    """
    stmt = select(User).where(User.id == user_id)
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    return db.scalar(stmt)


def get_user_by_email(
    db: Session,
    email: str,
    *,
    include_deleted: bool = False,
) -> User | None:
    """Retorna um Usuário pelo endereço de e-mail (insensível a maiúsculas), ou None.

    Args:
        db:              Sessão ativa do banco de dados.
        email:           O endereço de e-mail a ser pesquisado.
        include_deleted: Se True, também busca registros com exclusão lógica.

    Returns:
        A instância do Usuário, ou None.
    """
    stmt = select(User).where(User.email == email.lower().strip())
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    return db.scalar(stmt)


def get_active_users_by_company(
    db: Session,
    company_id: int,
) -> list[User]:
    """Retorna todos os usuários ativos (não-excluídos, is_active=True) de uma Empresa.

    Args:
        db:         Sessão ativa do banco de dados.
        company_id: A chave primária da empresa.

    Returns:
        Lista de instâncias de Usuários ativos. Pode ser vazia.
    """
    stmt = (
        select(User)
        .where(User.company_id == company_id)
        .where(User.deleted_at.is_(None))
        .where(User.is_active.is_(True))
        .order_by(User.email)
    )
    return list(db.scalars(stmt).all())
