from dataclasses import dataclass


@dataclass(frozen=True)
class JurisdictionContext:
    """
    Normalized jurisdiction information used to select
    applicable sanctions sources.
    """

    countries: list[str]
    global_sources_included: bool = True


COUNTRY_ALIASES = {
    "US": "UNITED_STATES",
    "USA": "UNITED_STATES",
    "UNITED STATES": "UNITED_STATES",
    "UNITED STATES OF AMERICA": "UNITED_STATES",

    "UK": "UNITED_KINGDOM",
    "GB": "UNITED_KINGDOM",
    "GREAT BRITAIN": "UNITED_KINGDOM",
    "UNITED KINGDOM": "UNITED_KINGDOM",

    "INDIA": "INDIA",
}


def normalize_country(country: str | None) -> str | None:
    if not country:
        return None

    normalized = country.strip().upper()

    return COUNTRY_ALIASES.get(
        normalized,
        normalized.replace(" ", "_"),
    )

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