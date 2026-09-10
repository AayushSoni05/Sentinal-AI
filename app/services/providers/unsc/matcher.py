from difflib import SequenceMatcher
import re

from app.services.providers.unsc.config import (
    get_review_threshold
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value: str | None) -> str:
    if not value:
        return ""

    value = value.upper()

    # Replace punctuation with spaces.
    value = re.sub(
        r"[^A-Z0-9\s]",
        " ",
        value
    )

    # Collapse multiple spaces.
    value = " ".join(
        value.split()
    )

    return value


def tokenize(value: str | None) -> list[str]:
    normalized = normalize_text(value)

    if not normalized:
        return []

    return normalized.split()


# ============================================================
# BASIC STRING SIMILARITY
# ============================================================

def sequence_similarity(
    value_1: str,
    value_2: str
) -> float:

    if not value_1 or not value_2:
        return 0.0

    return SequenceMatcher(
        None,
        value_1,
        value_2
    ).ratio() * 100.0


# ============================================================
# TOKEN SIMILARITY
# ============================================================

def token_similarity(
    value_1: str,
    value_2: str
) -> float:

    tokens_1 = set(
        tokenize(value_1)
    )

    tokens_2 = set(
        tokenize(value_2)
    )

    if not tokens_1 or not tokens_2:
        return 0.0

    intersection = (
        tokens_1 & tokens_2
    )

    union = (
        tokens_1 | tokens_2
    )

    return (
        len(intersection)
        / len(union)
    ) * 100.0


# ============================================================
# NAME SCORE
# ============================================================

def calculate_name_score(
    subject_name: str,
    candidate_name: str
) -> float:

    subject = normalize_text(
        subject_name
    )

    candidate = normalize_text(
        candidate_name
    )

    if not subject or not candidate:
        return 0.0

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    if subject == candidate:
        return 100.0

    # --------------------------------------------------------
    # Sequence similarity
    # --------------------------------------------------------

    sequence_score = sequence_similarity(
        subject,
        candidate
    )

    return round(
        min(sequence_score, 100.0),
        2
    )

# ============================================================
# FIND BEST NAME MATCH
# ============================================================

def best_name_match(
    subject_name: str,
    record: dict
):

    primary_name = record.get(
        "name"
    )

    aliases = record.get(
        "aliases",
        []
    ) or []

    normalized_subject = normalize_text(
        subject_name
    )

    normalized_primary = normalize_text(
        primary_name
    )

    # --------------------------------------------------------
    # EXACT PRIMARY NAME
    # --------------------------------------------------------

    if (
        normalized_subject
        and normalized_subject
        == normalized_primary
    ):
        return {
            "score": 100.0,
            "match_type": "EXACT_NAME"
        }

    # --------------------------------------------------------
    # EXACT ALIAS
    # --------------------------------------------------------

    for alias in aliases:

        normalized_alias = normalize_text(
            alias
        )

        if (
            normalized_subject
            and normalized_subject
            == normalized_alias
        ):
            return {
                "score": 100.0,
                "match_type": "EXACT_ALIAS"
            }

    # --------------------------------------------------------
    # FUZZY PRIMARY NAME
    # --------------------------------------------------------

    best_score = calculate_name_score(
        normalized_subject,
        normalized_primary
    )

    best_match_type = "FUZZY_NAME"

    # --------------------------------------------------------
    # FUZZY ALIAS
    # --------------------------------------------------------

    for alias in aliases:

        alias_score = calculate_name_score(
            normalized_subject,
            alias
        )

        if alias_score > best_score:
            best_score = alias_score
            best_match_type = "FUZZY_ALIAS"

    return {
        "score": best_score,
        "match_type": best_match_type
    }


# ============================================================
# MATCH SUBJECT AGAINST UNSC
# ============================================================

def match_subject_against_unsc(
    name: str,
    records: list[dict],
    subject_identifiers: dict | None = None
):

    review_threshold = get_review_threshold()

    subject_identifiers = (
        subject_identifiers or {}
    )

    # ========================================================
    # IDENTIFIER NORMALIZATION
    # ========================================================

    normalized_subject_identifiers = {
        str(value).strip().upper()
        for value in subject_identifiers.values()
        if value is not None
        and str(value).strip()
    }

    # ========================================================
    # EXACT IDENTIFIER MATCH
    # ========================================================

    for record in records:

        identifiers = record.get(
            "identifiers",
            []
        ) or []

        for identifier in identifiers:

            if not isinstance(
                identifier,
                dict
            ):
                continue

            identifier_value = (
                identifier.get("number")
                or identifier.get("value")
                or identifier.get("identifier")
            )

            if not identifier_value:
                continue

            normalized_identifier = (
                str(identifier_value)
                .strip()
                .upper()
            )

            if (
                normalized_identifier
                in normalized_subject_identifiers
            ):

                return {
                    "result": "MATCH",
                    "match_confidence": 100.0,
                    "matched_record": None,
                    "country_match": None,
                    "identifier_match": True,
                    "match_strength": "EXACT_IDENTIFIER",
                    "evidence_strength": "HIGH",
                    "match_type": "EXACT_IDENTIFIER",
                    "recommendation": "BLOCK"
                }

    # ========================================================
    # NAME MATCHING
    # ========================================================

    best_record = None
    best_score = 0.0
    best_match_type = None

    for record in records:

        name_match = best_name_match(
            name,
            record
        )

        score = name_match[
            "score"
        ]

        if score > best_score:
            best_score = score
            best_record = record
            best_match_type = name_match[
                "match_type"
            ]

    # ========================================================
    # BELOW REVIEW THRESHOLD
    # ========================================================

    if best_record is None or best_score < review_threshold:

        return {
            "result": "NO_MATCH",

            # Business confidence is zero because
            # there is no business-level match.
            "match_confidence": round(
                best_score,
                2
            ),

            "matched_record": None,

            "country_match": None,

            "identifier_match": False,

            "match_strength": "NONE",

            "evidence_strength": "NONE",

            "match_type": "NO_MATCH",

            "recommendation": "CLEAR",

            # Technical similarity retained for
            # debugging/analysis only.
            "similarity_score": round(
                best_score,
                2
            )
        }

    # ========================================================
    # EXACT / VERY HIGH MATCH
    # ========================================================

    if best_score >= 100.0:

        return {
            "result": "MATCH",
            "match_confidence": 100.0,
            "matched_record": best_record,
            "country_match": None,
            "identifier_match": False,
            "match_strength": "EXACT",
            "evidence_strength": "HIGH",
            "match_type": best_match_type,
            "recommendation": "BLOCK",
            "similarity_score": 100.0
        }

    # ========================================================
    # REVIEW MATCH
    # ========================================================

    if best_score >= review_threshold:

        if best_score >= 95:
            match_strength = "VERY_STRONG"
            evidence_strength = "HIGH"

        elif best_score >= 85:
            match_strength = "STRONG"
            evidence_strength = "MEDIUM"

        else:
            match_strength = "MODERATE"
            evidence_strength = "MEDIUM"

        return {
            "result": "MATCH",
            "match_confidence": round(
                best_score,
                2
            ),
            "matched_record": best_record,
            "country_match": None,
            "identifier_match": False,
            "match_strength": match_strength,
            "evidence_strength": evidence_strength,
            "match_type": best_match_type,
            "recommendation": "REVIEW",
            "similarity_score": round(
                best_score,
                2
            )
        }

    # ========================================================
    # SAFETY FALLBACK
    # ========================================================

    return {
        "result": "NO_MATCH",
        "match_confidence": round(
            best_score,
            2
        ),
        "matched_record": None,
        "country_match": None,
        "identifier_match": False,
        "match_strength": "NONE",
        "evidence_strength": "NONE",
        "match_type": "NO_MATCH",
        "recommendation": "CLEAR",
        "similarity_score": round(
            best_score,
            2
        )
    }