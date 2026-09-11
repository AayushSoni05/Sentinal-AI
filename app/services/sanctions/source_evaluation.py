from dataclasses import dataclass, field

from .candidate import SanctionsCandidate
from .candidate_evaluation import (
    CandidateEvaluation,
    evaluate_candidate,
)
from .source_result import SourceScreeningResult

@dataclass
class SourceEvaluation:
    """
    Evaluation of all candidates returned by one sanctions source.
    """

    source_name: str
    candidates: list[CandidateEvaluation] = field(default_factory=list)

    @property
    def positive_matches(self) -> list[CandidateEvaluation]:
        return [
            evaluation
            for evaluation in self.candidates
            if evaluation.score.confidence_tier in {"HIGH", "MEDIUM"}
        ]

    @property
    def highest_scoring_match(
        self,
    ) -> CandidateEvaluation | None:
        if not self.candidates:
            return None

        return max(
            self.candidates,
            key=lambda evaluation: evaluation.score.score,
        )


def evaluate_source_candidates(
    *,
    target_name: str,
    candidates: list[SanctionsCandidate],
    target_dob: str | None = None,
    target_country: str | None = None,
    target_identifiers: dict | None = None,
    target_gender: str | None = None,
    target_type: str | None = None,
) -> SourceEvaluation:
    """
    Evaluate every candidate returned by one sanctions source.
    """

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
        for candidate in candidates
    ]

    source_name = (
        candidates[0].source_name
        if candidates
        else "UNKNOWN"
    )

    return SourceEvaluation(
        source_name=source_name,
        candidates=evaluations,
    )

def build_source_screening_result(
    evaluation: SourceEvaluation,
) -> SourceScreeningResult:
    """
    Convert the evaluated candidates from one sanctions source
    into a normalized source-level screening result.
    """

    highest_match = evaluation.highest_scoring_match

    if highest_match is None:
        return SourceScreeningResult(
            source_name=evaluation.source_name,
            candidates_evaluated=len(evaluation.candidates),
            positive_matches=len(evaluation.positive_matches),
            issuing_country="GLOBAL",
        )

    return SourceScreeningResult(
        source_name=evaluation.source_name,
        issuing_country=highest_match.candidate.issuing_country,
        candidates_evaluated=len(evaluation.candidates),
        positive_matches=len(evaluation.positive_matches),
        highest_match=highest_match,
        matched_canonical_name=highest_match.candidate.canonical_name,
        matched_alias_used=highest_match.signals["name_match"][
            "matched_alias_used"
        ],
        raw_match_score=highest_match.score.score,
        match_confidence_tier=highest_match.score.confidence_tier,
        matching_signals=highest_match.score.matching_signals,
        mismatch_signals=highest_match.score.mismatch_signals,
    )