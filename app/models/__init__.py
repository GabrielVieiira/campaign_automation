"""app/models package.

Import all models here so that Alembic's `env.py` can discover them
by simply importing this package. This ensures that every model is
included in `Base.metadata` for migration generation.

Order matters: models that are referenced by FKs should be imported first.
"""

from app.models.audit import CampaignChangeLog
from app.models.base import Base, SoftDeleteMixin, TimestampMixin
from app.models.company import Company
from app.models.redtrack_config import RedTrackConfiguration
from app.models.user import User

__all__ = [
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "Company",
    "User",
    "RedTrackConfiguration",
    "CampaignChangeLog",
]
