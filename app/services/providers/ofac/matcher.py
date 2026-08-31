# ============================================================
# OFAC ENTITY MATCHER
# ============================================================

from difflib import SequenceMatcher

from app.services.providers.ofac.normalizer import (
    normalize_name
)


def calculate_name_similarity(
    subject_name: str,
    sanctions_name: str
):
    subject = normalize_name(subject_name)
    candidate = normalize_name(sanctions_name)

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

    subject = subject_country.strip().upper()

    countries = set()

    for address in record.get(
        "addresses",
        []
    ):
        country = address.get("country")

        if country:
            countries.add(
                country.strip().upper()
            )

    if not countries:
        return None

    return subject in countries

# ============================================================
# CHECK IDENTIFIER MATCH
# ============================================================

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

# ============================================================
# ASSESS MATCH STRENGTH
# ============================================================

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

# ============================================================
# DETERMINE MATCH RESULT
# ============================================================

def match_subject_against_sdn(
    subject_name: str,
    sdn_records: list[dict],
    possible_match_threshold: float = 0.85,
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

    for record in sdn_records:

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

    # --------------------------------------------------------
    # KEEP A CANDIDATE ONLY IF IT REACHES THE MATCH THRESHOLD
    # --------------------------------------------------------

    if best_score >= possible_match_threshold:
        matched_record = best_match
    else:
        matched_record = None

    # --------------------------------------------------------
    # COUNTRY EVIDENCE
    # --------------------------------------------------------

    matched_country = (
        country_matches(
            subject_country,
            matched_record
        )
        if matched_record
        else None
    )

    # --------------------------------------------------------
    # NAME MATCH STRENGTH
    # --------------------------------------------------------

    match_strength = assess_match_strength(
        name_score=best_score,
        country_match=matched_country
    )

    # --------------------------------------------------------
    # IDENTIFIER EVIDENCE
    # --------------------------------------------------------

    identifier_match = (
        identifier_matches(
            subject_identifiers,
            matched_record
        )
        if matched_record
        else None
    )

    # --------------------------------------------------------
    # CORROBORATING EVIDENCE
    # --------------------------------------------------------

    evidence_strength = assess_corroborating_evidence(
        name_score=best_score,
        country_match=matched_country,
        identifier_match=identifier_match
    )

    # --------------------------------------------------------
    # FINAL SANCTIONS STATUS
    # --------------------------------------------------------

    result = determine_sanctions_status(
        evidence_strength=evidence_strength,
        name_score=best_score,
        identifier_match=identifier_match
    )

    return {
        "result": result,
        "match_confidence": round(
            best_score * 100,
            2
        ),
        "matched_record": matched_record,
        "country_match": matched_country,
        "match_strength": match_strength,
        "identifier_match": identifier_match,
        "evidence_strength": evidence_strength
    }

# ============================================================
# ASSESS CORROBORATING EVIDENCE
# ============================================================

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

# ============================================================
# DETERMINE SANCTIONS SCREENING STATUS
# ============================================================

def determine_sanctions_status(
    evidence_strength: str,
    name_score: float,
    identifier_match: bool | None
):
    if (
        evidence_strength == "CONFIRMED"
        and name_score >= 0.95
        and identifier_match is True
    ):
        return "CONFIRMED_MATCH"

    if evidence_strength in {
        "STRONG",
        "MODERATE"
    }:
        return "POSSIBLE_MATCH"

    return "NO_MATCH"