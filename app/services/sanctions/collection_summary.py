from .screening_collection import ScreeningCollection


def build_collection_summary(
    collection: ScreeningCollection,
) -> dict:
    """
    Build a compact summary of the multi-source screening collection.
    """

    return {
        "total_sources_evaluated": collection.total_sources_evaluated,
        "sources_with_positive_matches": (
            collection.sources_with_positive_matches
        ),
        "source_results": [
            {
                "source_name": result.source_name,
                "issuing_country": result.issuing_country,
                "raw_match_score": result.raw_match_score,
                "match_confidence_tier": result.match_confidence_tier,
                "matched_canonical_name": result.matched_canonical_name,
                "matched_alias_used": result.matched_alias_used,
                "matching_signals": result.matching_signals,
                "mismatch_signals": result.mismatch_signals,
            }
            for result in collection.results
        ],
    }