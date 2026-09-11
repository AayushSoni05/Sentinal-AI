from typing import Protocol


class SanctionsCandidate(Protocol):
    """
    Standard candidate record returned by any sanctions source.
    """

    source_name: str
    source_uid: str
    canonical_name: str
    aliases: list[str]
    issuing_country: str | None
    countries: list[str]
    dates_of_birth: list[str]
    entity_type: str | None
    identifiers: dict


class SanctionsMatch(Protocol):
    """
    Standard normalized screening result produced by the
    common sanctions matching engine.
    """

    source_name: str
    source_uid: str
    matched_canonical_name: str
    matched_alias_used: str | None

    raw_match_score: float
    match_confidence_tier: str

    matching_signals: list[str]
    mismatch_signals: list[str]