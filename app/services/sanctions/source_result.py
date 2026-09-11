from dataclasses import dataclass, field

from .candidate_evaluation import CandidateEvaluation


@dataclass
class SourceScreeningResult:
    """
    Final deterministic screening result for one sanctions source.
    """

    source_name: str
    candidates_evaluated: int
    positive_matches: int

    issuing_country: str = "GLOBAL"

    highest_match: CandidateEvaluation | None = None

    matched_canonical_name: str | None = None
    matched_alias_used: str | None = None

    raw_match_score: float = 0.0
    match_confidence_tier: str = "LOW"

    matching_signals: list[str] = field(default_factory=list)
    mismatch_signals: list[str] = field(default_factory=list)