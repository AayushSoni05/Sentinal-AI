from dataclasses import dataclass

from .overrides import apply_hard_risk_overrides
from .verdict import determine_verdict


@dataclass(frozen=True)
class ConsensusResult:
    """
    Final consensus assessment across all evaluated sanctions sources.
    """

    consensus_risk_index: float
    final_verdict: str

    primary_flagged_jurisdiction: str
    total_sources_evaluated: int
    sources_with_positive_matches: int


def build_consensus_result(
    *,
    consensus_risk_index: float,
    source_results: list[dict],
    primary_flagged_jurisdiction: str,
    total_sources_evaluated: int,
    sources_with_positive_matches: int,
) -> ConsensusResult:
    """
    Build the final consensus result from the CRI and source-level results.

    Hard-risk overrides are applied before returning the final verdict.
    """

    base_verdict = determine_verdict(
        consensus_risk_index
    )

    final_score, final_verdict = apply_hard_risk_overrides(
        consensus_risk_index=consensus_risk_index,
        base_verdict=base_verdict,
        source_results=source_results,
    )

    return ConsensusResult(
        consensus_risk_index=final_score,
        final_verdict=final_verdict,
        primary_flagged_jurisdiction=primary_flagged_jurisdiction,
        total_sources_evaluated=total_sources_evaluated,
        sources_with_positive_matches=sources_with_positive_matches,
    )