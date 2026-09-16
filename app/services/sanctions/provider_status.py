from dataclasses import dataclass

from .provider_registry import get_global_sanctions_provider


@dataclass(frozen=True)
class ProviderCapability:
    """
    Describes whether a sanctions source currently has a
    Sentinel AI Sprint 5 provider implementation.
    """

    source_name: str
    issuing_country: str
    implemented: bool
    provider: type | None = None


def get_provider_capability(
    source_name: str,
    issuing_country: str,
) -> ProviderCapability:
    """
    Resolve whether Sentinel AI has a Sprint 5 global sanctions
    provider implementation for an official source.
    """

    provider_instance = get_global_sanctions_provider(
        source_name
    )

    return ProviderCapability(
        source_name=source_name,
        issuing_country=issuing_country,
        implemented=provider_instance is not None,
        provider=(
            type(provider_instance)
            if provider_instance is not None
            else None
        ),
    )