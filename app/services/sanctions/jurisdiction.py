from dataclasses import dataclass


@dataclass(frozen=True)
class JurisdictionContext:
    """
    Normalized jurisdiction information used to select
    applicable sanctions sources.
    """

    countries: list[str]
    global_sources_included: bool = True


def normalize_country(country: str | None) -> str | None:
    if not country:
        return None

    return country.strip().upper()


def build_jurisdiction_context(
    countries: list[str | None],
) -> JurisdictionContext:
    normalized = {
        normalize_country(country)
        for country in countries
    }

    normalized.discard(None)

    return JurisdictionContext(
        countries=sorted(normalized),
        global_sources_included=True,
    )