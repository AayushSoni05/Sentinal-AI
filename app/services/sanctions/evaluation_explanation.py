from .candidate_evaluation import CandidateEvaluation
from .score_explanation import build_score_explanation


def build_candidate_explanation(
    evaluation: CandidateEvaluation,
) -> dict:
    """
    Build a complete explainability payload for one evaluated
    sanctions candidate.
    """

    candidate = evaluation.candidate

    return {
        "source_name": candidate.source_name,
        "source_uid": candidate.source_uid,
        "matched_canonical_name": candidate.canonical_name,
        "matched_name": evaluation.signals["name_match"]["matched_name"],
        "matched_alias_used": evaluation.signals["name_match"][
            "matched_alias_used"
        ],
        "score": build_score_explanation(
            evaluation.score,
            evaluation.signals,
        ),
    }