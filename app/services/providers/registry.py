# ============================================================
# SCREENING PROVIDER REGISTRY
# ============================================================

from app.services.screening_providers import (
    MockScreeningProvider
)
from app.services.providers.ofac.provider import (
    OFACSanctionsProvider
)
from app.services.providers.unsc.provider import (
    UNSCSanctionsProvider
)
from app.services.providers.ofac_non_sdn.provider import (
    OFACNonSDNSanctionsProvider
)
from app.services.providers.uk_sanctions.provider import (
    UKSanctionsProvider
)

# ============================================================
# PROVIDER REGISTRY
# ============================================================

SCREENING_PROVIDER_REGISTRY = {
    "UNSC": UNSCSanctionsProvider,
    "OFAC": OFACSanctionsProvider,
    "OFAC_NON_SDN": OFACNonSDNSanctionsProvider,
    "UK": UKSanctionsProvider,
    "PEP": MockScreeningProvider,
    "ADVERSE_MEDIA": MockScreeningProvider
}


# ============================================================
# GET SCREENING PROVIDER
# ============================================================

def get_screening_provider(
    provider_name: str
):
    provider_class = SCREENING_PROVIDER_REGISTRY.get(
        provider_name
    )
    if provider_class is None:
        raise ValueError(
            f"No screening provider configured for "
            f"{provider_name}"
        )
    return provider_class()