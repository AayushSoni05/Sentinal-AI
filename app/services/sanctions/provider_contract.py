from typing import Protocol

from .candidate import SanctionsCandidate


class GlobalSanctionsProvider(Protocol):
    """
    Common higher-level contract for every official sanctions source.

    A provider is responsible for obtaining and normalizing official
    source records. The common sanctions engine evaluates the candidates.
    """

    source_name: str
    issuing_country: str

    def get_candidates(
        self,
    ) -> list[SanctionsCandidate]:
        """
        Return normalized candidates from the official source.
        """
        ...