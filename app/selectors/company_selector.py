"""Company selectors — encapsulate all database queries related to Company."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company


def get_company_by_id(
    db: Session,
    company_id: int,
    *,
    include_deleted: bool = False,
) -> Company | None:
    """Return a Company by primary key, or None if not found.

    Args:
        db:              Active database session.
        company_id:      The company's primary key.
        include_deleted: If True, also search soft-deleted records.

    Returns:
        The Company instance, or None.
    """
    stmt = select(Company).where(Company.id == company_id)
    if not include_deleted:
        stmt = stmt.where(Company.deleted_at.is_(None))
    return db.scalar(stmt)


def get_company_by_slug(
    db: Session,
    slug: str,
    *,
    include_deleted: bool = False,
) -> Company | None:
    """Return a Company by its URL-safe slug, or None.

    Args:
        db:              Active database session.
        slug:            The company slug.
        include_deleted: If True, also search soft-deleted records.

    Returns:
        The Company instance, or None.
    """
    stmt = select(Company).where(Company.slug == slug)
    if not include_deleted:
        stmt = stmt.where(Company.deleted_at.is_(None))
    return db.scalar(stmt)
