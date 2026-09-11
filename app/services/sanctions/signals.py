from dataclasses import dataclass


@dataclass(frozen=True)
class MatchingSignal:
    """
    One explainable signal used by the sanctions matching engine.
    """

    name: str
    score: float
    weight: float
    matched: bool
    details: str | None = None