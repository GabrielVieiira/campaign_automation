"""Database session dependency for FastAPI route injection.

Usage:
    from app.api.dependencies.database import get_db

    @router.get("/example")
    def example(db: Session = Depends(get_db)):
        ...
"""

# Re-export get_db from core so routes import from a consistent API location
from app.core.database import get_db

__all__ = ["get_db"]
