from datetime import datetime, timezone

from .consensus import ConsensusResult
from .screening_collection import ScreeningCollection
from .explainability import build_explainability_report


def build_consensus_output(
    *,
    target_name: str,
    target_type: str,
    consensus: ConsensusResult,
    collection: ScreeningCollection,
) -> dict:
    """
    Build the Sprint 5 consensus output structure.
    """

    return {
        "query_metadata": {
            "target_name": target_name,
            "target_type": target_type,
            "screening_timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        },
        "consensus_summary": {
            "consensus_risk_index": consensus.consensus_risk_index,
            "final_verdict": consensus.final_verdict,
            "primary_flagged_jurisdiction": (
                consensus.primary_flagged_jurisdiction
            ),
            "total_sources_evaluated": (
                consensus.total_sources_evaluated
            ),
            "sources_with_positive_matches": (
                consensus.sources_with_positive_matches
            ),
        },
        "source_breakdown": [
            {
                "source_name": result.source_name,
                "issuing_country": result.issuing_country,
                "raw_match_score": result.raw_match_score,
                "matched_canonical_name": (
                    result.matched_canonical_name
                ),
                "matched_alias_used": (
                    result.matched_alias_used
                ),
                "match_confidence_tier": (
                    result.match_confidence_tier
                ),
                "matching_signals": result.matching_signals,
                "mismatch_signals": result.mismatch_signals,
            }
            for result in collection.results
        ],
        "explainability_report": build_explainability_report(
            target_name=target_name,
            consensus_risk_index=consensus.consensus_risk_index,
            final_verdict=consensus.final_verdict,
            source_results=[
                {
                    "source_name": result.source_name,
                    "issuing_country": result.issuing_country,
                    "raw_match_score": result.raw_match_score,
                    "match_confidence_tier": result.match_confidence_tier,
                    "matched_canonical_name": result.matched_canonical_name,
                    "matched_alias_used": result.matched_alias_used,
                }
                for result in collection.results
            ],
        ),
    }