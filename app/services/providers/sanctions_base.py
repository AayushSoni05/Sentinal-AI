# ============================================================
# SANCTIONS SOURCE PROVIDER CONTRACT
# ============================================================

from typing import Protocol


class SanctionsSource(Protocol):

    def screen(
        self,
        name: str,
        subject_type: str,
        subject_id: str,
        relationship_role: str,
        subject_country: str | None = None,
        subject_identifiers: dict | None = None
    ):
        """
        Screen one subject against one sanctions source.

        Every sanctions source must return a normalized
        provider result containing source-specific provenance.
        """
        ...