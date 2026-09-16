from .source_result import SourceScreeningResult
from .source_screening import SourceCandidateScreening


def build_source_screening_result(
    screening: SourceCandidateScreening,
) -> SourceScreeningResult:
    """
    Convert generic source screening output into
    the existing SourceScreeningResult model.
    """

    if not screening.implemented or screening.error:
        return SourceScreeningResult(
            source_name=screening.source_name,
            candidates_evaluated=screening.candidates_evaluated,
            positive_matches=len(screening.confirmed_matches),
        )

    highest_match = None

    all_matches = screening.confirmed_matches + screening.review_candidates

    if all_matches:
        highest_match = max(
            all_matches,
            key=lambda evaluation: evaluation.score.score,
        )

    return SourceScreeningResult(
        source_name=screening.source_name,
        candidates_evaluated=screening.candidates_evaluated,
        positive_matches=len(screening.confirmed_matches),
        highest_match=highest_match,
        matched_canonical_name=(
            highest_match.candidate.canonical_name
            if highest_match
            else None
        ),
        matched_alias_used=(
            highest_match.signals["name_match"]["matched_alias_used"]
            if highest_match
            else None
        ),
        raw_match_score=(
            highest_match.score.score
            if highest_match
            else 0.0
        ),
        match_confidence_tier=(
            highest_match.score.confidence_tier
            if highest_match
            else "LOW"
        ),
    )