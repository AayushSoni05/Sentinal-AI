# ============================================================
# OFAC CONSOLIDATED NON-SDN MATCHER
# ============================================================

from difflib import SequenceMatcher

from app.services.providers.ofac_non_sdn.normalizer import (
    normalize_name
)

from app.services.providers.unsc.config import (
    get_review_threshold
)


def calculate_name_similarity(
    subject_name: str,
    sanctions_name: str
):
    subject = normalize_name(
        subject_name
    )

    candidate = normalize_name(
        sanctions_name
    )

    if not subject or not candidate:
        return 0.0

    return SequenceMatcher(
        None,
        subject,
        candidate
    ).ratio()


def country_matches(
    subject_country: str | None,
    record: dict
):
    if not subject_country:
        return None

    subject = (
        subject_country
        .strip()
        .upper()
    )

    countries = set()

    for address in record.get(
        "addresses",
        []
    ):
        country = address.get(
            "country"
        )

        if country:
            countries.add(
                country.strip().upper()
            )

    if not countries:
        return None

    return subject in countries


def identifier_matches(
    subject_identifiers: dict | None,
    record: dict
):
    if not subject_identifiers:
        return None

    subject_id_type = subject_identifiers.get(
        "id_type"
    )

    subject_id_number = subject_identifiers.get(
        "id_number"
    )

    if not subject_id_type or not subject_id_number:
        return None

    subject_id_number = (
        str(subject_id_number)
        .strip()
        .upper()
    )

    for identifier in record.get(
        "identifiers",
        []
    ):
        record_id_type = identifier.get(
            "id_type"
        )

        record_id_number = identifier.get(
            "id_number"
        )

        if not record_id_type or not record_id_number:
            continue

        if (
            record_id_type.strip().upper()
            == subject_id_type.strip().upper()
            and
            record_id_number.strip().upper()
            == subject_id_number
        ):
            return True

    return False


def assess_match_strength(
    name_score: float,
    country_match: bool | None
):
    if name_score >= 0.95:

        if country_match is True:
            return "STRONG"

        if country_match is False:
            return "MODERATE"

        return "STRONG"

    if name_score >= 0.85:

        if country_match is True:
            return "STRONG"

        return "MODERATE"

    return "WEAK"


def assess_corroborating_evidence(
    name_score: float,
    country_match: bool | None,
    identifier_match: bool | None
):
    if (
        name_score >= 0.95
        and identifier_match is True
    ):
        return "CONFIRMED"

    if (
        name_score >= 0.95
        and country_match is True
    ):
        return "STRONG"

    if (
        name_score >= 0.85
        and identifier_match is True
    ):
        return "STRONG"

    if (
        name_score >= 0.85
        and country_match is True
    ):
        return "MODERATE"

    return "WEAK"


def determine_sanctions_status(
    evidence_strength: str,
    name_score: float,
    identifier_match: bool | None
):
    review_threshold = get_review_threshold()

    if identifier_match is True:
        return "MATCH"

    score_percent = name_score * 100.0

    if score_percent >= 100.0:
        return "MATCH"

    if score_percent >= 85.0:
        return "MATCH"

    if score_percent >= review_threshold:
        return "POSSIBLE_MATCH"

    return "NO_MATCH"


def match_subject_against_non_sdn(
    subject_name: str,
    non_sdn_records: list[dict],
    subject_country: str | None = None,
    subject_identifiers: dict | None = None
):
    normalized_subject = normalize_name(
        subject_name
    )

    if not normalized_subject:
        return {
            "result": "NO_MATCH",
            "match_confidence": 0.0,
            "matched_record": None,
            "country_match": None,
            "match_strength": "WEAK",
            "identifier_match": None,
            "evidence_strength": "WEAK"
        }

    best_match = None
    best_score = 0.0

    for record in non_sdn_records:

        candidate_names = [
            record.get(
                "normalized_name",
                ""
            )
        ]

        candidate_names.extend(
            record.get(
                "normalized_aliases",
                []
            )
        )

        for candidate_name in candidate_names:

            score = calculate_name_similarity(
                normalized_subject,
                candidate_name
            )

            if score > best_score:
                best_score = score
                best_match = record

    review_threshold = get_review_threshold()

    matched_record = (
        best_match
        if best_score * 100.0 >= review_threshold
        else None
    )

    matched_country = (
        country_matches(
            subject_country,
            matched_record
        )
        if matched_record
        else None
    )

    identifier_match = (
        identifier_matches(
            subject_identifiers,
            matched_record
        )
        if matched_record
        else None
    )

    match_strength = assess_match_strength(
        name_score=best_score,
        country_match=matched_country
    )

    evidence_strength = (
        assess_corroborating_evidence(
            name_score=best_score,
            country_match=matched_country,
            identifier_match=identifier_match
        )
    )

    result = determine_sanctions_status(
        evidence_strength=evidence_strength,
        name_score=best_score,
        identifier_match=identifier_match
    )

    return {
        "result": result,
        "match_confidence": round(
            best_score * 100.0,
            2
        ),
        "matched_record": matched_record,
        "country_match": matched_country,
        "match_strength": match_strength,
        "identifier_match": identifier_match,
        "evidence_strength": evidence_strength
    }