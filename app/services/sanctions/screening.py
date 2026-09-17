from dataclasses import dataclass, field
from typing import Any
import re
import unicodedata

from app.services.sanctions.sources import (
    SanctionsSourceDefinition,
    SourceScreeningStatus,
    get_enabled_sources,
)
from datetime import datetime, timezone
import jellyfish

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

def normalize_name(name: str) -> str:
    """
    Normalize a name into a consistent comparison form.
    """
    if not name:
        return ""

    normalized = unicodedata.normalize("NFKD", name)

    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    normalized = normalized.casefold()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()

def normalize_aliases(aliases: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        normalized
        for alias in aliases
        if (normalized := normalize_name(alias))
    )

def get_normalized_names(candidate: SanctionsCandidate) -> tuple[str, ...]:
    names = [normalize_name(candidate.name)]
    names.extend(normalize_aliases(candidate.aliases))

    return tuple(
        name
        for name in names
        if name
    )

def name_matches(
    subject_name: str,
    candidate: SanctionsCandidate,
) -> bool:
    normalized_subject = normalize_name(subject_name)

    if not normalized_subject:
        return False

    return normalized_subject in get_normalized_names(candidate)

def name_similarity(
    subject_name: str,
    candidate: SanctionsCandidate,
) -> float:
    normalized_subject = normalize_name(subject_name)

    if not normalized_subject:
        return 0.0

    candidate_names = get_normalized_names(candidate)

    if not candidate_names:
        return 0.0

    return max(
        jellyfish.jaro_winkler_similarity(
            normalized_subject,
            candidate_name,
        )
        for candidate_name in candidate_names
    )

def is_name_similarity_match(
    similarity: float,
    threshold: float = 0.85,
) -> bool:
    return similarity >= threshold

def levenshtein_similarity(
    subject_name: str,
    candidate: SanctionsCandidate,
) -> float:
    normalized_subject = normalize_name(subject_name)

    if not normalized_subject:
        return 0.0

    candidate_names = get_normalized_names(candidate)

    if not candidate_names:
        return 0.0

    def similarity(candidate_name: str) -> float:
        distance = jellyfish.levenshtein_distance(
            normalized_subject,
            candidate_name,
        )

        max_length = max(
            len(normalized_subject),
            len(candidate_name),
        )

        if max_length == 0:
            return 1.0

        return 1.0 - (distance / max_length)

    return max(
        similarity(candidate_name)
        for candidate_name in candidate_names
    )

def phonetic_match(
    subject_name: str,
    candidate: SanctionsCandidate,
) -> bool:
    normalized_subject = normalize_name(subject_name)

    if not normalized_subject:
        return False

    candidate_names = get_normalized_names(candidate)

    if not candidate_names:
        return False

    subject_soundex = jellyfish.soundex(normalized_subject)

    return any(
        jellyfish.soundex(candidate_name) == subject_soundex
        for candidate_name in candidate_names
    )

@dataclass(frozen=True)
class NameMatchEvidence:
    exact_match: bool
    jaro_winkler_score: float
    levenshtein_score: float
    phonetic_match: bool

def build_name_match_evidence(
    subject_name: str,
    candidate: SanctionsCandidate,
) -> NameMatchEvidence:
    jaro_score = name_similarity(
        subject_name,
        candidate,
    )

    return NameMatchEvidence(
        exact_match=name_matches(
            subject_name,
            candidate,
        ),
        jaro_winkler_score=jaro_score,
        levenshtein_score=levenshtein_similarity(
            subject_name,
            candidate,
        ),
        phonetic_match=phonetic_match(
            subject_name,
            candidate,
        ),
    )
# ============================================================
# SOURCE RESULT
# ============================================================

# ============================================================
# SOURCE RETRIEVAL RESULT
# ============================================================

@dataclass(frozen=True)
class SourceRetrievalResult:
    source_id: str
    source_name: str
    available: bool
    checked_at: datetime
    candidate_count: int = 0
    message: str | None = None

@dataclass(frozen=True)
class SourceScreeningResult:
    source_id: str
    source_name: str
    status: SourceScreeningStatus
    checked_at: datetime
    screening_completed: bool = False
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

def execute_global_source_retrieval(
    subject_id: str,
    subject_type: str,
) -> tuple[ScreeningPlan, list[SourceRetrievalResult]]:
    from app.services.sanctions.connectors import get_connector

    plan = build_global_screening_plan(
        subject_id=subject_id,
        subject_type=subject_type,
    )

    results: list[SourceRetrievalResult] = []

    from datetime import datetime, timezone

    for source in plan.sources:
        connector = get_connector(source.connector_type)

        if connector is None:
            results.append(
                SourceRetrievalResult(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    available=False,
                    checked_at=datetime.now(timezone.utc),
                    message=(
                        f"No connector registered for "
                        f"connector type: {source.connector_type}"
                    ),
                )
            )
            continue

        if source.implementation_status != "IMPLEMENTED":
            results.append(
                SourceRetrievalResult(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    available=False,
                    checked_at=datetime.now(timezone.utc),
                    message=(
                        "Source discovered but connector/parser "
                        "implementation is not complete."
                    ),
                )
            )
            continue

        try:
            result = connector.retrieve(source)
            results.append(result)

        except Exception as exc:
            results.append(
                SourceRetrievalResult(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    available=False,
                    checked_at=datetime.now(timezone.utc),
                    message=str(exc),
                )
            )

    return plan, results

def load_global_source_candidates(
    subject_id: str,
    subject_type: str,
) -> tuple[
    ScreeningPlan,
    dict[str, list[SanctionsCandidate]],
    list[SourceRetrievalResult],
]:
    from app.services.sanctions.connectors import get_connector

    plan = build_global_screening_plan(
        subject_id=subject_id,
        subject_type=subject_type,
    )

    candidate_sets: dict[str, list[SanctionsCandidate]] = {}
    retrieval_results: list[SourceRetrievalResult] = []

    for source in plan.sources:
        connector = get_connector(source.connector_type)

        if connector is None:
            retrieval_results.append(
                SourceRetrievalResult(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    available=False,
                    checked_at=datetime.now(timezone.utc),
                    message=(
                        f"No connector registered for "
                        f"connector type: {source.connector_type}"
                    ),
                )
            )
            continue

        if source.implementation_status != "IMPLEMENTED":
            retrieval_results.append(
                SourceRetrievalResult(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    available=False,
                    checked_at=datetime.now(timezone.utc),
                    message=(
                        "Source discovered but connector/parser "
                        "implementation is not complete."
                    ),
                )
            )
            continue

        try:
            retrieval = connector.retrieve(source)

            if not retrieval.available:
                retrieval_results.append(retrieval)
                continue

            candidates = connector.load_candidates(source)

            candidate_sets[source.source_id] = candidates

            retrieval_results.append(
                SourceRetrievalResult(
                    source_id=retrieval.source_id,
                    source_name=retrieval.source_name,
                    available=True,
                    checked_at=retrieval.checked_at,
                    candidate_count=len(candidates),
                    message=retrieval.message,
                )
            )

        except Exception as exc:
            retrieval_results.append(
                SourceRetrievalResult(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    available=False,
                    checked_at=datetime.now(timezone.utc),
                    candidate_count=0,
                    message=str(exc),
                )
            )
    return plan, candidate_sets, retrieval_results