def build_explainability_report(
    *,
    target_name: str,
    consensus_risk_index: float,
    final_verdict: str,
    source_results: list[dict],
) -> str:
    """
    Build a human-readable sanctions screening explanation.
    """

    if not source_results:
        return (
            f"Screening completed for {target_name}. "
            f"No source results were available. "
            f"Consensus Risk Index: {consensus_risk_index:.2f}. "
            f"Final verdict: {final_verdict}."
        )

    positive_sources = [
        result
        for result in source_results
        if result.get("raw_match_score", 0.0) > 0.0
    ]

    lines = [
        f"Screening completed for {target_name}.",
        f"Consensus Risk Index: {consensus_risk_index:.2f}.",
        f"Final verdict: {final_verdict}.",
        (
            f"{len(positive_sources)} of "
            f"{len(source_results)} evaluated source(s) "
            "returned candidate evidence."
        ),
    ]

    for result in source_results:
        source_name = result.get("source_name", "UNKNOWN")
        issuing_country = result.get(
            "issuing_country",
            "UNKNOWN",
        )
        score = result.get("raw_match_score", 0.0)
        tier = result.get(
            "match_confidence_tier",
            "LOW",
        )
        canonical_name = result.get(
            "matched_canonical_name",
        )
        alias_used = result.get(
            "matched_alias_used",
        )

        lines.append(
            f"{source_name} ({issuing_country}) "
            f"returned a score of {score:.2f} "
            f"with {tier} confidence."
        )

        if canonical_name:
            lines.append(
                f"Matched canonical name: {canonical_name}."
            )

        if alias_used:
            lines.append(
                f"Matched alias used: {alias_used}."
            )

    return " ".join(lines)