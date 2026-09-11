from dataclasses import dataclass


@dataclass(frozen=True)
class SourceScore:
    """
    Weighted score for one target against one sanctions candidate.
    """

    score: float
    confidence_tier: str
    matching_signals: list[str]
    mismatch_signals: list[str]


NAME_WEIGHT = 0.50
PHONETIC_WEIGHT = 0.10
BIRTH_YEAR_WEIGHT = 0.15
COUNTRY_WEIGHT = 0.15
IDENTIFIER_WEIGHT = 0.15

GENDER_MISMATCH_PENALTY = 0.20
DOB_MISMATCH_PENALTY = 0.30
ENTITY_TYPE_MISMATCH_PENALTY = 0.30
HARD_IDENTIFIER_MATCH_SCORE = 1.0


def calculate_source_score(signals: dict) -> SourceScore:
    """
    Convert deterministic signals into a normalized source-specific score.

    Name similarity is the base score.
    Additional agreement signals contribute positive weights.
    Explicit mismatches apply penalties.
    """

    name_signals = signals["name_signals"]
    attribute_signals = signals["attribute_signals"]
    mismatch_signals = signals["mismatch_signals"]
    hard_match_signals = signals.get("hard_match_signals", {})
    if hard_match_signals.get("exact_identifier_match"):
        return SourceScore(
            score=HARD_IDENTIFIER_MATCH_SCORE,
            confidence_tier="HIGH",
            matching_signals=["EXACT_IDENTIFIER_MATCH"],
            mismatch_signals=[],
        )

    score = name_signals["name_combined"] * NAME_WEIGHT

    matching_signals: list[str] = []
    mismatch_signal_names: list[str] = []

    if name_signals["jaro_winkler"] >= 0.85:
        matching_signals.append("JARO_WINKLER_STRONG")

    if name_signals["levenshtein"] >= 0.85:
        matching_signals.append("LEVENSHTEIN_STRONG")

    if name_signals["phonetic_agreement"]:
        score += PHONETIC_WEIGHT
        matching_signals.append("PHONETIC_AGREEMENT")

    if attribute_signals["birth_year_agreement"]:
        score += BIRTH_YEAR_WEIGHT
        matching_signals.append("BIRTH_YEAR_AGREEMENT")

    if attribute_signals["country_agreement"]:
        score += COUNTRY_WEIGHT
        matching_signals.append("COUNTRY_AGREEMENT")

    if attribute_signals["identifier_agreement"]:
        score += IDENTIFIER_WEIGHT
        matching_signals.append("IDENTIFIER_AGREEMENT")

    if mismatch_signals["gender_mismatch"]:
        score -= GENDER_MISMATCH_PENALTY
        mismatch_signal_names.append("GENDER_MISMATCH")

    if mismatch_signals["date_of_birth_mismatch"]:
        score -= DOB_MISMATCH_PENALTY
        mismatch_signal_names.append("DATE_OF_BIRTH_MISMATCH")

    if mismatch_signals["entity_type_mismatch"]:
        score -= ENTITY_TYPE_MISMATCH_PENALTY
        mismatch_signal_names.append("ENTITY_TYPE_MISMATCH")

    score = max(0.0, min(1.0, score))

    if score >= 0.85:
        confidence_tier = "HIGH"
    elif score >= 0.65:
        confidence_tier = "MEDIUM"
    else:
        confidence_tier = "LOW"

    return SourceScore(
        score=round(score, 6),
        confidence_tier=confidence_tier,
        matching_signals=matching_signals,
        mismatch_signals=mismatch_signal_names,
    )