from dataclasses import dataclass, field
from typing import Any
from datetime import datetime

from app.services.sanctions.sources import (
    SanctionsSourceDefinition,
    SourceScreeningStatus,
    get_enabled_sources,
)

# ============================================================
# NORMALIZED SANCTIONS CANDIDATE
# ============================================================

@dataclass(frozen=True)
class SanctionsCandidate:
    source_id: str
    source_uid: str
    name: str
    aliases: tuple[str, ...] = ()
    entity_type: str | None = None
    date_of_birth: str | None = None
    nationality: str | None = None
    country: str | None = None
    identifiers: tuple[str, ...] = ()
    raw_data: dict[str, Any] = field(default_factory=dict)

# ============================================================
# SOURCE RESULT
# ============================================================

@dataclass(frozen=True)
class SourceScreeningResult:
    source_id: str
    source_name: str
    status: SourceScreeningStatus
    checked_at: datetime
    message: str | None = None


# ============================================================
# SCREENING PLAN
# ============================================================

@dataclass(frozen=True)
class ScreeningPlan:
    subject_id: str
    subject_type: str
    sources: tuple[SanctionsSourceDefinition, ...]


def build_global_screening_plan(
    subject_id: str,
    subject_type: str,
) -> ScreeningPlan:
    return ScreeningPlan(
        subject_id=subject_id,
        subject_type=subject_type,
        sources=tuple(get_enabled_sources()),
    )


# ============================================================
# COVERAGE SUMMARY
# ============================================================

@dataclass(frozen=True)
class ScreeningCoverageSummary:
    sources_discovered: int
    sources_checked: int
    matches: int
    possible_matches: int
    no_matches: int
    unavailable: int
    errors: int