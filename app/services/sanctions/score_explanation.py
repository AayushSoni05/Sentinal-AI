from .source_scoring import SourceScore


def build_score_explanation(
    score: SourceScore,
    signals: dict | None = None,
) -> dict:
    """
    Build a structured explanation for a source-specific score.
    """

    signals = signals or {}

    return {
        "score": score.score,
        "confidence_tier": score.confidence_tier,
        "matching_signals": score.matching_signals,
        "mismatch_signals": score.mismatch_signals,
        "signal_details": {
            "name_signals": signals.get("name_signals", {}),
            "attribute_signals": signals.get("attribute_signals", {}),
            "hard_match_signals": signals.get("hard_match_signals", {}),
        },
        "explanation": {
            "positive_signal_count": len(score.matching_signals),
            "mismatch_signal_count": len(score.mismatch_signals),
        },
    }