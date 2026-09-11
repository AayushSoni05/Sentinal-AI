from .source_models import SanctionsSourceDefinition


SANCTIONS_SOURCE_CATALOG = [
    SanctionsSourceDefinition(
        source_name="UNSC",
        issuing_country="GLOBAL",
        global_scope=True,
        provider_name="UNSC",
        provider_implemented=True,
    ),
    SanctionsSourceDefinition(
        source_name="OFAC",
        issuing_country="UNITED_STATES",
        provider_name="OFAC",
        provider_implemented=True,
    ),
    SanctionsSourceDefinition(
        source_name="OFAC_NON_SDN",
        issuing_country="UNITED_STATES",
        provider_name="OFAC_NON_SDN",
        provider_implemented=True,
    ),
    SanctionsSourceDefinition(
        source_name="UK",
        issuing_country="UNITED_KINGDOM",
        provider_name="UK",
        provider_implemented=True,
    ),
    SanctionsSourceDefinition(
        source_name="EU",
        issuing_country="EU",
        provider_name="EU",
        provider_implemented=True,
    ),
    SanctionsSourceDefinition(
        source_name="INDIA_UAPA",
        issuing_country="INDIA",
        provider_name="INDIA_UAPA",
        provider_implemented=True,
    ),
]


def get_enabled_sanctions_sources() -> list[SanctionsSourceDefinition]:
    return [
        source
        for source in SANCTIONS_SOURCE_CATALOG
        if source.enabled
    ]