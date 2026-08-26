# ============================================================
# SCREENING PROVIDERS
# ============================================================

from typing import Protocol
from app.services.providers.base import (
    ExternalScreeningProvider
)

# ============================================================
# SCREENING PROVIDER INTERFACE
# ============================================================

class ScreeningProvider(Protocol):

    def screen(
        self,
        name: str,
        screening_type: str
    ):
        ...


# ============================================================
# MOCK SCREENING PROVIDER
# ============================================================

class MockScreeningProvider(
    ExternalScreeningProvider
):

    def screen(
    self,
    name: str,
    screening_type: str,
    subject_type: str,
    subject_id: str,
    relationship_role: str
):
        return {
            "provider": "MOCK_PROVIDER",
            "screening_type": screening_type,
            "result": "CLEAR",
            "matched_name": None,
            "match_confidence": None,
            "evidence": f"Mock screening for {name}",
            "subject_type": subject_type,
            "subject_id": subject_id,
            "relationship_role": relationship_role
        }