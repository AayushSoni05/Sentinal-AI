from dataclasses import dataclass

from .candidate import SanctionsCandidate
from .deterministic_match import calculate_candidate_match
from .source_scoring import SourceScore, calculate_source_score


@dataclass
class CandidateEvaluation:
    """
    Complete deterministic evaluation of one sanctions candidate.
    """

    candidate: SanctionsCandidate
    signals: dict
    score: SourceScore


def evaluate_candidate(
    *,
    target_name: str,
    candidate: SanctionsCandidate,
    target_dob: str | None = None,
    target_country: str | None = None,
    target_identifiers: dict | None = None,
    target_gender: str | None = None,
    target_type: str | None = None,
) -> CandidateEvaluation:
    """
    Evaluate one normalized sanctions candidate using the common
    deterministic matching and source-scoring engine.
    """

    signals = calculate_candidate_match(
        target_name=target_name,
        candidate=candidate,
        target_dob=target_dob,
        target_country=target_country,
        target_identifiers=target_identifiers,
        target_gender=target_gender,
        target_type=target_type,
    )

    score = calculate_source_score(signals)

    return CandidateEvaluation(
        candidate=candidate,
        signals=signals,
        score=score,
    )