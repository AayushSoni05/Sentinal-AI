from .alias_matching import find_best_name_match
from .attribute_signals import (
    birth_year_agreement,
    country_agreement,
    identifier_agreement,
)
from .mismatch_signals import (
    date_of_birth_mismatch,
    entity_type_mismatch,
    gender_mismatch,
)
from .identifier_matching import exact_identifier_match
from .candidate import SanctionsCandidate

def calculate_deterministic_signals(
    *,
    target_name: str,
    candidate_name: str,
    candidate_aliases: list[str] | None = None,
    target_dob: str | None = None,
    candidate_dobs: list[str] | None = None,
    target_country: str | None = None,
    candidate_countries: list[str] | None = None,
    target_identifiers: dict | None = None,
    candidate_identifiers: dict | None = None,
    target_gender: str | None = None,
    candidate_gender: str | None = None,
    target_type: str | None = None,
    candidate_type: str | None = None,
) -> dict:
    """
    Calculate all deterministic matching and mismatch signals
    for one target/candidate pair.

    Name matching includes the canonical candidate name and
    all available aliases.
    """

    candidate_dobs = candidate_dobs or []
    candidate_countries = candidate_countries or []
    target_identifiers = target_identifiers or {}
    candidate_identifiers = candidate_identifiers or {}
    candidate_aliases = candidate_aliases or []

    best_name_match = find_best_name_match(
        target_name=target_name,
        canonical_name=candidate_name,
        aliases=candidate_aliases,
    )

    return {
        "name_match": {
            "matched_name": best_name_match["matched_name"],
            "matched_alias_used": best_name_match["matched_alias_used"],
        },
        "name_signals": {
            "jaro_winkler": best_name_match["jaro_winkler"],
            "levenshtein": best_name_match["levenshtein"],
            "name_combined": best_name_match["name_combined"],
            "phonetic_agreement": best_name_match["phonetic_agreement"],
        },
        "attribute_signals": {
            "birth_year_agreement": birth_year_agreement(
                target_dob,
                candidate_dobs,
            ),
            "country_agreement": country_agreement(
                target_country,
                candidate_countries,
            ),
            "identifier_agreement": identifier_agreement(
                target_identifiers,
                candidate_identifiers,
            ),
        },
        "mismatch_signals": {
            "gender_mismatch": gender_mismatch(
                target_gender,
                candidate_gender,
            ),
            "date_of_birth_mismatch": date_of_birth_mismatch(
                target_dob,
                candidate_dobs,
            ),
            "entity_type_mismatch": entity_type_mismatch(
                target_type,
                candidate_type,
            ),
        },
        "hard_match_signals": {
            "exact_identifier_match": exact_identifier_match(
                target_identifiers,
                candidate_identifiers,
            ),
        },
    }

def calculate_candidate_match(
    *,
    target_name: str,
    candidate: SanctionsCandidate,
    target_dob: str | None = None,
    target_country: str | None = None,
    target_identifiers: dict | None = None,
    target_gender: str | None = None,
    target_type: str | None = None,
) -> dict:
    """
    Calculate deterministic matching signals for a normalized
    sanctions candidate.
    """

    return calculate_deterministic_signals(
        target_name=target_name,
        candidate_name=candidate.canonical_name,
        candidate_aliases=candidate.aliases,
        target_dob=target_dob,
        candidate_dobs=candidate.dates_of_birth,
        target_country=target_country,
        candidate_countries=candidate.countries,
        target_identifiers=target_identifiers,
        candidate_identifiers=candidate.identifiers,
        target_gender=target_gender,
        candidate_gender=candidate.gender,
        target_type=target_type,
        candidate_type=candidate.entity_type,
    )