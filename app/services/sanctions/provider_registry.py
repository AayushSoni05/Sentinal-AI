from .unsc_provider import UNSCGlobalSanctionsProvider


GLOBAL_SANCTIONS_PROVIDER_REGISTRY = {
    "UNSC": UNSCGlobalSanctionsProvider,
}


def get_global_sanctions_provider(
    source_name: str,
):
    """
    Return the Sprint 5 higher-level provider for an official source.

    Returns None when the source is applicable but its higher-level
    provider has not yet been implemented.
    """

    provider = GLOBAL_SANCTIONS_PROVIDER_REGISTRY.get(source_name)

    if provider is None:
        return None

    return provider()