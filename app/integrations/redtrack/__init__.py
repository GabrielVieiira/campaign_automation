"""app/integrations/redtrack package.

This package is the only interface between the application and the
RedTrack API. Nothing outside this package should know how RedTrack
authentication works or what HTTP library is being used.
"""

from app.integrations.redtrack.client import RedTrackClient

__all__ = ["RedTrackClient"]
