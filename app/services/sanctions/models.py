from dataclasses import dataclass, field


@dataclass
class ScreeningTarget:
    """
    The normalized entity being screened.
    """

    name: str
    target_type: str  # Individual | Entity

    date_of_birth: str | None = None
    country: str | None = None
    identifiers: dict = field(default_factory=dict)

    subject_id: str | None = None
    relationship_role: str = "Customer"