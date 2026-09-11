# ============================================================
# EU CONSOLIDATED FINANCIAL SANCTIONS LIST MATCHER
# ============================================================

from difflib import SequenceMatcher

from app.services.providers.eu_sanctions.normalizer import (
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


def assess_match_strength(
    name_score: float
):
    if name_score >= 0.95:
        return "STRONG"

    if name_score >= 0.85:
        return "MODERATE"

    if name_score >= 0.68:
        return "WEAK"

    return "NONE"


def assess_evidence_strength(
    name_score: float
):
    if name_score >= 0.95:
        return "HIGH"

    if name_score >= 0.85:
        return "MEDIUM"

    if name_score >= 0.68:
        return "LOW"

    return "NONE"


def determine_sanctions_status(
    name_score: float
):
    review_threshold = get_review_threshold()

    score_percent = (
        name_score * 100.0
    )

    if score_percent >= 85.0:
        return "MATCH"

    if score_percent >= review_threshold:
        return "POSSIBLE_MATCH"

    return "NO_MATCH"


def match_subject_against_eu(
    subject_name: str,
    eu_records: list[dict]
):
    normalized_subject = normalize_name(
        subject_name
    )

    if not normalized_subject:
        return {
            "result": "NO_MATCH",
            "match_confidence": 0.0,
            "matched_record": None,
            "match_strength": "NONE",
            "evidence_strength": "NONE"
        }

    best_match = None
    best_score = 0.0

    for record in eu_records:

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

    if matched_record is None:
        return {
            "result": "NO_MATCH",
            "match_confidence": round(
                best_score * 100.0,
                2
            ),
            "matched_record": None,
            "match_strength": "NONE",
            "evidence_strength": "NONE"
        }

    return {
        "result": determine_sanctions_status(
            best_score
        ),
        "match_confidence": round(
            best_score * 100.0,
            2
        ),
        "matched_record": matched_record,
        "match_strength": assess_match_strength(
            best_score
        ),
        "evidence_strength": assess_evidence_strength(
            best_score
        )
    }