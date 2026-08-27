# ============================================================
# SCREENING PROVIDER REGISTRY
# ============================================================

from app.services.screening_providers import (
    MockScreeningProvider
)


# ============================================================
# PROVIDER REGISTRY
# ============================================================

SCREENING_PROVIDER_REGISTRY = {
    "SANCTIONS": MockScreeningProvider,
    "PEP": MockScreeningProvider,
    "ADVERSE_MEDIA": MockScreeningProvider
}


# ============================================================
# GET SCREENING PROVIDER
# ============================================================

def get_screening_provider(
    screening_type: str
):
    provider_class = SCREENING_PROVIDER_REGISTRY.get(
        screening_type
    )

    if provider_class is None:
        raise ValueError(
            f"No screening provider configured for "
            f"{screening_type}"
        )

    return provider_class()