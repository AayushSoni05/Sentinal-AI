from dataclasses import dataclass, field


@dataclass
class SanctionsCandidate:
    """
    Normalized candidate record produced from any sanctions source.
    """

    source_name: str
    source_uid: str | None

    canonical_name: str
    aliases: list[str] = field(default_factory=list)

    issuing_country: str = "GLOBAL"
    countries: list[str] = field(default_factory=list)

    dates_of_birth: list[str] = field(default_factory=list)

    entity_type: str | None = None
    gender: str | None = None

    identifiers: dict = field(default_factory=dict)

    raw_data: dict = field(default_factory=dict)