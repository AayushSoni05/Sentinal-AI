from .jurisdiction import JurisdictionContext
from .source_catalog import get_enabled_sanctions_sources
from .source_models import SanctionsSourceDefinition
from .source_resolution import SourceResolution
from .contracts import SanctionsResolution


def select_applicable_sources(
    context: JurisdictionContext,
) -> list[SanctionsSourceDefinition]:
    """
    Select all sanctions sources applicable to the supplied jurisdictions.

    Global sources are always included.
    Jurisdiction-specific sources are included when their issuing country
    matches one of the target countries.
    """

    selected_sources: list[SanctionsSourceDefinition] = []

    for source in get_enabled_sanctions_sources():
        if source.global_scope:
            selected_sources.append(source)
            continue

        if source.issuing_country in context.countries:
            selected_sources.append(source)

    return selected_sources


def resolve_applicable_sources(
    context: JurisdictionContext,
) -> list[SourceResolution]:
    """
    Resolve each applicable source while preserving whether Sentinel AI
    currently has an implementation for it.
    """

    sources = select_applicable_sources(context)

    return [
        SourceResolution(
            source=source,
            applicable=True,
            implementation_status=source.implementation_status,
        )
        for source in sources
    ]

def build_sanctions_resolution(
    context: JurisdictionContext,
) -> SanctionsResolution:
    """
    Build the complete sanctions source resolution for a jurisdiction context.
    """

    return SanctionsResolution(
        applicable_sources=resolve_applicable_sources(context)
    )