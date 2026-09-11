from dataclasses import dataclass


@dataclass(frozen=True)
class VerdictThresholds:
    """
    Thresholds used to translate CRI into a final sanctions verdict.
    """

    high_risk: float
    review: float


DEFAULT_VERDICT_THRESHOLDS = VerdictThresholds(
    high_risk=85.0,
    review=65.0,
)


def determine_verdict(
    consensus_risk_index: float,
    thresholds: VerdictThresholds = DEFAULT_VERDICT_THRESHOLDS,
) -> str:
    """
    Map the CRI to the required Sprint 5 final verdict.
    """

    if consensus_risk_index >= thresholds.high_risk:
        return "FLAGGED_HIGH_RISK"

    if consensus_risk_index >= thresholds.review:
        return "POTENTIAL_MATCH_REVIEW"

    return "CLEAR"