from .candidate import SanctionsCandidate
from .provider_registry import get_global_sanctions_provider


def get_source_candidates(
    source_name: str,
) -> list[SanctionsCandidate]:
    """
    Execute a Sprint 5 sanctions provider and return its
    normalized candidates.

    Raises ValueError when the source is known but its provider
    has not yet been implemented.
    """

    provider = get_global_sanctions_provider(
        source_name
    )

    if provider is None:
        raise ValueError(
            f"No Sprint 5 provider is implemented for source: "
            f"{source_name}"
        )

    return provider.get_candidates()