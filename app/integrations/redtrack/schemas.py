"""RedTrack API response schemas — PLACEHOLDER.

This module will contain Pydantic models that represent the response
structures returned by the RedTrack API.

IMPORTANT — Current Status:
    These schemas are intentionally incomplete placeholders.
    The RedTrack API payloads for /campaigns and /landings have NOT yet
    been fully analyzed. Do NOT invent field names or structures.

    Once the real API responses are examined, this module will be updated
    with validated Pydantic models representing the actual data shapes.

What we know so far:
    - GET /campaigns   → returns a list of campaign objects (structure TBD)
    - GET /landings    → returns a list of landing objects (structure TBD)
    - Authentication   → api_key passed as query parameter

Next steps (NOT to be implemented until API payloads are confirmed):
    - Define CampaignSchema with real field names
    - Define LandingSchema with real field names
    - Define the relationship between campaigns and landers/pre-landers
    - Define the update payload structure for bulk campaign modifications
"""

from typing import Any

# ---------------------------------------------------------------------------
# Placeholder type aliases — to be replaced with proper Pydantic models
# once the RedTrack API payloads are analyzed.
# ---------------------------------------------------------------------------

# Raw campaign object as returned by GET /campaigns
# Shape TBD — do not assume field names
RawCampaign = dict[str, Any]

# Raw landing/pre-lander object as returned by GET /landings
# Shape TBD — do not assume field names
RawLanding = dict[str, Any]
