from dataclasses import dataclass, field

from .candidate import SanctionsCandidate
from .provider_registry import get_global_sanctions_provider


@dataclass
class ProviderExecutionResult:
    """
    Result of attempting to execute one sanctions source.
    """

    source_name: str
    implemented: bool
    candidates: list[SanctionsCandidate] = field(
        default_factory=list
    )
    error: str | None = None


def execute_source_provider(
    source_name: str,
) -> ProviderExecutionResult:
    """
    Execute a Sprint 5 provider when available.

    An unavailable provider is represented as a structured result
    instead of being silently omitted.
    """

    provider = get_global_sanctions_provider(
        source_name
    )

    if provider is None:
        return ProviderExecutionResult(
            source_name=source_name,
            implemented=False,
            error=(
                f"No Sprint 5 provider is implemented for source: "
                f"{source_name}"
            ),
        )

    try:
        candidates = provider.get_candidates()

        return ProviderExecutionResult(
            source_name=source_name,
            implemented=True,
            candidates=candidates,
        )

    except Exception as exc:
        return ProviderExecutionResult(
            source_name=source_name,
            implemented=True,
            error=str(exc),
        )