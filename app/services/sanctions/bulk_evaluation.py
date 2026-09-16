from app.services.sanctions.candidate import SanctionsCandidate
from app.services.sanctions.candidate_evaluation import (
    CandidateEvaluation,
    evaluate_candidate,
)


def evaluate_candidates(
    *,
    target_name: str,
    candidates: list[SanctionsCandidate],
    target_dob: str | None = None,
    target_country: str | None = None,
    target_identifiers: dict | None = None,
    target_gender: str | None = None,
    target_type: str | None = None,
) -> list[CandidateEvaluation]:
    """
    Evaluate each sanctions candidate exactly once.
    """

    evaluations: list[CandidateEvaluation] = []

    for candidate in candidates:
        evaluation = evaluate_candidate(
            target_name=target_name,
            candidate=candidate,
            target_dob=target_dob,
            target_country=target_country,
            target_identifiers=target_identifiers,
            target_gender=target_gender,
            target_type=target_type,
        )

        evaluations.append(evaluation)

    return evaluations