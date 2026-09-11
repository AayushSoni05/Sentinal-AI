from .source_result import SourceScreeningResult
from .score_explanation import build_score_explanation


def build_source_result_explanation(
    result: SourceScreeningResult,
) -> dict:
    """
    Build the explainability payload for one sanctions source.
    """

    if result.highest_match is None:
        return {
            "source_name": result.source_name,
            "issuing_country": result.issuing_country,
            "candidates_evaluated": result.candidates_evaluated,
            "positive_matches": result.positive_matches,
            "matched_canonical_name": None,
            "matched_alias_used": None,
            "score": {
                "score": 0.0,
                "confidence_tier": "LOW",
                "matching_signals": [],
                "mismatch_signals": [],
                "signal_details": {},
            },
        }

    return {
        "source_name": result.source_name,
        "issuing_country": result.issuing_country,
        "candidates_evaluated": result.candidates_evaluated,
        "positive_matches": result.positive_matches,
        "matched_canonical_name": result.matched_canonical_name,
        "matched_alias_used": result.matched_alias_used,
        "score": build_score_explanation(
            result.highest_match.score,
            result.highest_match.signals,
        ),
    }