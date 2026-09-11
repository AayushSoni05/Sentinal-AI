def apply_hard_risk_overrides(
    *,
    consensus_risk_index: float,
    base_verdict: str,
    source_results: list[dict],
) -> tuple[float, str]:
    """
    Apply definitive sanctions evidence overrides.

    A source result containing an exact identifier match is treated
    as high-risk evidence.
    """

    for result in source_results:
        hard_match_signals = (
            result.get("score", {})
            .get("signal_details", {})
            .get("hard_match_signals", {})
        )

        if hard_match_signals.get("exact_identifier_match"):
            return max(consensus_risk_index, 85.0), "FLAGGED_HIGH_RISK"

    return consensus_risk_index, base_verdict