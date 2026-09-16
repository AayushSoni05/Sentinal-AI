from dataclasses import dataclass, field

from .candidate import SanctionsCandidate
from .candidate_evaluation import CandidateEvaluation, evaluate_candidate
from .provider_execution import execute_source_provider


@dataclass
class SourceCandidateScreening:
    """
    Result of screening one target against every candidate
    returned by one sanctions source.
    """

    source_name: str
    implemented: bool

    candidates_evaluated: int = 0
    evaluations: list[CandidateEvaluation] = field(
        default_factory=list
    )

    error: str | None = None

    @property
    def confirmed_matches(self) -> list[CandidateEvaluation]:
        return [
            evaluation
            for evaluation in self.evaluations
            if evaluation.score.confidence_tier == "HIGH"
        ]

    @property
    def review_candidates(self) -> list[CandidateEvaluation]:
        return [
            evaluation
            for evaluation in self.evaluations
            if evaluation.score.confidence_tier == "MEDIUM"
        ]


def screen_target_against_source(
    *,
    target_name: str,
    source_name: str,
    target_dob: str | None = None,
    target_country: str | None = None,
    target_identifiers: dict | None = None,
    target_gender: str | None = None,
    target_type: str | None = None,
) -> SourceCandidateScreening:
    """
    Execute one source provider and evaluate every returned candidate
    through the common Sprint 5 matching engine.
    """

    execution = execute_source_provider(
        source_name
    )

    if not execution.implemented:
        return SourceCandidateScreening(
            source_name=source_name,
            implemented=False,
            error=execution.error,
        )

    if execution.error:
        return SourceCandidateScreening(
            source_name=source_name,
            implemented=True,
            error=execution.error,
        )

    evaluations = [
        evaluate_candidate(
            target_name=target_name,
            candidate=candidate,
            target_dob=target_dob,
            target_country=target_country,
            target_identifiers=target_identifiers,
            target_gender=target_gender,
            target_type=target_type,
        )
        for candidate in execution.candidates
    ]

    return SourceCandidateScreening(
        source_name=source_name,
        implemented=True,
        candidates_evaluated=len(
            execution.candidates
        ),
        evaluations=evaluations,
    )