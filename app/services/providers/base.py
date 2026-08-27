# ============================================================
# EXTERNAL SCREENING PROVIDER BASE
# ============================================================

from typing import Protocol


class ExternalScreeningProvider(Protocol):

    def screen(
        self,
        name: str,
        screening_type: str,
        subject_type: str,
        subject_id: str,
        relationship_role: str,
        subject_country: str | None = None,
        subject_identifiers: dict | None = None
    ):
        ...