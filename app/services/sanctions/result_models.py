from dataclasses import dataclass, field


@dataclass
class NormalizedSanctionsMatch:
    """
    Common normalized result produced by the sanctions matching engine
    for one source and one screened target.
    """

    source_name: str
    issuing_country: str

    source_uid: str | None
    matched_canonical_name: str
    matched_alias_used: str | None

    raw_match_score: float
    match_confidence_tier: str

    matching_signals: list[str] = field(default_factory=list)
    mismatch_signals: list[str] = field(default_factory=list)

    evidence: dict = field(default_factory=dict)