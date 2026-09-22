from dataclasses import dataclass, field
from typing import Any
import re
import unicodedata

from app.services.sanctions.sources import (
    SanctionsSourceDefinition,
    SourceScreeningStatus,
    get_source_by_id,
)
from app.services.sanctions.discovery import (
    discover_sanctions_sources,
)
from datetime import datetime, timezone
import jellyfish
import math

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
    gender: str | None = None
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

@dataclass(frozen=True)
class CandidateMatchResult:
    candidate: SanctionsCandidate
    name_evidence: NameMatchEvidence
    identifier_supplied: bool = False
    date_of_birth_supplied: bool = False
    country_supplied: bool = False
    entity_type_supplied: bool = False
    gender_supplied: bool = False
    identifier_match: bool = False
    date_of_birth_match: bool = False
    birth_year_match: bool = False
    country_match: bool = False
    entity_type_match: bool = False
    gender_match: bool = False
    identifier_mismatch: bool = False
    date_of_birth_mismatch: bool = False
    birth_year_mismatch: bool = False
    country_mismatch: bool = False
    entity_type_mismatch: bool = False
    gender_mismatch: bool = False

@dataclass(frozen=True)
class CandidateMatchWeights:
    name: float
    identifier: float
    date_of_birth: float
    birth_year: float = 0.0
    country: float = 0.0
    entity_type: float = 0.0
    gender: float = 0.0

@dataclass(frozen=True)
class NameMatchWeights:
    jaro_winkler: float
    levenshtein: float
    phonetic: float

@dataclass(frozen=True)
class CandidateMatchThresholds:
    match_threshold: float
    possible_match_threshold: float

@dataclass(frozen=True)
class EvaluatedCandidateMatch:
    match_result: CandidateMatchResult
    score_breakdown: CandidateMatchScoreBreakdown
    status: SourceScreeningStatus

@dataclass(frozen=True)
class SourceCandidateEvaluation:
    source_id: str
    source_name: str
    evaluations: tuple[EvaluatedCandidateMatch, ...]
    status: SourceScreeningStatus
    checked_at: datetime

@dataclass(frozen=True)
class GlobalCandidateEvaluation:
    subject_id: str
    subject_type: str
    source_evaluations: tuple[SourceCandidateEvaluation, ...]
    status: SourceScreeningStatus
    coverage: ScreeningCoverageSummary
    checked_at: datetime

@dataclass(frozen=True)
class PositiveSanctionsFinding:
    source_id: str
    source_name: str
    source_uid: str
    candidate_name: str
    issuing_country: str
    status: SourceScreeningStatus
    score: float

def evaluate_candidate_match(
    match_result: CandidateMatchResult,
    weights: CandidateMatchWeights,
    penalties: CandidateMatchPenalties | None = None,
    name_weights: NameMatchWeights | None = None,
    thresholds: CandidateMatchThresholds | None = None,
) -> EvaluatedCandidateMatch:
    if thresholds is None:
        thresholds = CandidateMatchThresholds(
            match_threshold=0.85,
            possible_match_threshold=0.65,
        )

    score_breakdown = build_candidate_match_score_breakdown(
        match_result,
        weights,
        penalties,
        name_weights,
    )

    status = classify_candidate_match(
        score_breakdown.final_score,
        thresholds,
    )

    return EvaluatedCandidateMatch(
        match_result=match_result,
        score_breakdown=score_breakdown,
        status=status,
    )

def evaluate_candidate_matches(
    subject_name: str,
    candidates: list[SanctionsCandidate],
    subject_identifiers: tuple[str, ...] = (),
    subject_date_of_birth: str | None = None,
    subject_countries: tuple[str, ...] = (),
    subject_entity_type: str | None = None,
    subject_gender: str | None = None,
    weights: CandidateMatchWeights | None = None,
    penalties: CandidateMatchPenalties | None = None,
    name_weights: NameMatchWeights | None = None,
    thresholds: CandidateMatchThresholds | None = None,
) -> list[EvaluatedCandidateMatch]:
    if weights is None:
        weights = CandidateMatchWeights(
            name=0.35,
            identifier=0.30,
            date_of_birth=0.10,
            birth_year=0.05,
            country=0.05,
            entity_type=0.05,
            gender=0.10,
        )

    evaluations: list[EvaluatedCandidateMatch] = []

    for candidate in candidates:
        match_result = build_candidate_match_result(
            subject_name,
            candidate,
            subject_identifiers,
            subject_date_of_birth,
            subject_countries,
            subject_entity_type,
            subject_gender,
        )

        if not is_candidate_match(match_result):
            continue

        evaluations.append(
            evaluate_candidate_match(
                match_result,
                weights,
                penalties,
                name_weights,
                thresholds,
            )
        )

    return evaluations

def evaluate_source_candidates(
    source: SanctionsSourceDefinition,
    subject_name: str,
    candidates: list[SanctionsCandidate],
    subject_identifiers: tuple[str, ...] = (),
    subject_date_of_birth: str | None = None,
    subject_countries: tuple[str, ...] = (),
    subject_entity_type: str | None = None,
    subject_gender: str | None = None,
    weights: CandidateMatchWeights | None = None,
    penalties: CandidateMatchPenalties | None = None,
    name_weights: NameMatchWeights | None = None,
    thresholds: CandidateMatchThresholds | None = None,
) -> SourceCandidateEvaluation:
    evaluations = evaluate_candidate_matches(
        subject_name=subject_name,
        candidates=candidates,
        subject_identifiers=subject_identifiers,
        subject_date_of_birth=subject_date_of_birth,
        subject_countries=subject_countries,
        subject_entity_type=subject_entity_type,
        subject_gender=subject_gender,
        weights=weights,
        penalties=penalties,
        name_weights=name_weights,
        thresholds=thresholds,
    )

    if any(
        evaluation.status == SourceScreeningStatus.MATCH
        for evaluation in evaluations
    ):
        status = SourceScreeningStatus.MATCH
    elif any(
        evaluation.status == SourceScreeningStatus.POSSIBLE_MATCH
        for evaluation in evaluations
    ):
        status = SourceScreeningStatus.POSSIBLE_MATCH
    else:
        status = SourceScreeningStatus.NO_MATCH

    return SourceCandidateEvaluation(
        source_id=source.source_id,
        source_name=source.source_name,
        evaluations=tuple(evaluations),
        status=status,
        checked_at=datetime.now(timezone.utc),
    )

def validate_candidate_match_thresholds(
    thresholds: CandidateMatchThresholds,
) -> None:
    if not (
        0.0
        <= thresholds.possible_match_threshold
        <= 1.0
    ):
        raise ValueError(
            "Possible-match threshold must be between 0.0 and 1.0."
        )

    if not (
        0.0
        <= thresholds.match_threshold
        <= 1.0
    ):
        raise ValueError(
            "Match threshold must be between 0.0 and 1.0."
        )

    if (
        thresholds.match_threshold
        < thresholds.possible_match_threshold
    ):
        raise ValueError(
            "Match threshold must be greater than or equal to "
            "the possible-match threshold."
        )

def classify_candidate_match(
    score: float,
    thresholds: CandidateMatchThresholds,
) -> SourceScreeningStatus:
    validate_candidate_match_thresholds(thresholds)

    if not 0.0 <= score <= 1.0:
        raise ValueError(
            "Candidate match score must be between 0.0 and 1.0."
        )

    if score >= thresholds.match_threshold:
        return SourceScreeningStatus.MATCH

    if score >= thresholds.possible_match_threshold:
        return SourceScreeningStatus.POSSIBLE_MATCH

    return SourceScreeningStatus.NO_MATCH

def validate_name_match_weights(
    weights: NameMatchWeights,
) -> None:
    weight_values = (
        weights.jaro_winkler,
        weights.levenshtein,
        weights.phonetic,
    )

    if any(
        weight < 0.0 or weight > 1.0
        for weight in weight_values
    ):
        raise ValueError(
            "Name match weights must be between 0.0 and 1.0."
        )

    if not math.isclose(
        sum(weight_values),
        1.0,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise ValueError(
            "Name match weights must sum to 1.0."
        )

@dataclass(frozen=True)
class CandidateMatchPenalties:
    identifier: float
    date_of_birth: float
    birth_year: float
    country: float
    entity_type: float
    gender: float

@dataclass(frozen=True)
class CandidateMatchScoreBreakdown:
    name_score: float
    jaro_winkler_score: float
    levenshtein_score: float
    phonetic_match: bool
    identifier_score: float
    date_of_birth_score: float
    birth_year_score: float
    country_score: float
    entity_type_score: float
    gender_score: float
    mismatch_penalty: float
    final_score: float

def validate_candidate_match_penalties(
    penalties: CandidateMatchPenalties,
) -> None:
    penalty_values = (
        penalties.identifier,
        penalties.date_of_birth,
        penalties.birth_year,
        penalties.country,
        penalties.entity_type,
        penalties.gender,
    )

    if any(
        penalty < 0.0 or penalty > 1.0
        for penalty in penalty_values
    ):
        raise ValueError(
            "Candidate match penalties must be between 0.0 and 1.0."
        )

def validate_candidate_match_weights(
    weights: CandidateMatchWeights,
) -> None:
    weight_values = (
        weights.name,
        weights.identifier,
        weights.date_of_birth,
        weights.birth_year,
        weights.country,
        weights.entity_type,
        weights.gender,
    )

    if any(
        weight < 0.0 or weight > 1.0
        for weight in weight_values
    ):
        raise ValueError(
            "Candidate match weights must be between 0.0 and 1.0."
        )

    if not any(weight > 0.0 for weight in weight_values):
        raise ValueError(
            "At least one candidate match weight must be greater than 0.0."
        )

    if not math.isclose(
        sum(weight_values),
        1.0,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise ValueError(
            "Candidate match weights must sum to 1.0."
        )

def calculate_name_match_score(
    evidence: NameMatchEvidence,
    weights: NameMatchWeights | None = None,
) -> float:
    if weights is None:
        weights = NameMatchWeights(
            jaro_winkler=0.50,
            levenshtein=0.30,
            phonetic=0.20,
        )

    validate_name_match_weights(weights)

    score = (
        evidence.jaro_winkler_score
        * weights.jaro_winkler
        + evidence.levenshtein_score
        * weights.levenshtein
        + (
            1.0 if evidence.phonetic_match else 0.0
        )
        * weights.phonetic
    )

    if evidence.exact_match:
        score = 1.0

    return max(
        0.0,
        min(1.0, score),
    )

def build_candidate_match_score_breakdown(
    match_result: CandidateMatchResult,
    weights: CandidateMatchWeights,
    penalties: CandidateMatchPenalties | None = None,
    name_weights: NameMatchWeights | None = None,
) -> CandidateMatchScoreBreakdown:
    validate_candidate_match_weights(weights)

    if penalties is None:
        penalties = CandidateMatchPenalties(
            identifier=0.0,
            date_of_birth=0.0,
            birth_year=0.0,
            country=0.0,
            entity_type=0.0,
            gender=0.0,
        )

    validate_candidate_match_penalties(penalties)

    name_score = calculate_name_match_score(
        match_result.name_evidence,
        name_weights,
    )

    jaro_winkler_score = (
        match_result.name_evidence.jaro_winkler_score
    )

    levenshtein_score = (
        match_result.name_evidence.levenshtein_score
    )

    phonetic_match = (
        match_result.name_evidence.phonetic_match
    )

    identifier_score = (
        1.0
        if match_result.identifier_match
        else 0.0
    )

    date_of_birth_score = (
        1.0
        if match_result.date_of_birth_match
        else 0.0
    )

    birth_year_score = (
        1.0
        if match_result.birth_year_match
        else 0.0
    )

    country_score = (
        1.0
        if match_result.country_match
        else 0.0
    )

    entity_type_score = (
        1.0
        if match_result.entity_type_match
        else 0.0
    )

    gender_score = (
        1.0
        if match_result.gender_match
        else 0.0
    )

    # --------------------------------------------------------
    # SUPPLIED ATTRIBUTES ONLY
    # --------------------------------------------------------

    supplied_scores = [
        (name_score, weights.name)
    ]

    if match_result.identifier_supplied:
        supplied_scores.append(
            (identifier_score, weights.identifier)
        )

    if match_result.date_of_birth_supplied:
        supplied_scores.append(
            (date_of_birth_score, weights.date_of_birth)
        )

    if match_result.country_supplied:
        supplied_scores.append(
            (country_score, weights.country)
        )

    if match_result.entity_type_supplied:
        supplied_scores.append(
            (entity_type_score, weights.entity_type)
        )

    if match_result.gender_supplied:
        supplied_scores.append(
            (gender_score, weights.gender)
        )

    weighted_sum = sum(
        score * weight
        for score, weight in supplied_scores
    )

    total_weight = sum(
        weight
        for _, weight in supplied_scores
    )

    score = (
        weighted_sum / total_weight
        if total_weight > 0
        else 0.0
    )

    # --------------------------------------------------------
    # MISMATCH PENALTIES
    # --------------------------------------------------------

    mismatch_penalty = (
        penalties.identifier
        if match_result.identifier_mismatch
        else 0.0
    )

    if (
        match_result.date_of_birth_mismatch
        and not match_result.birth_year_mismatch
    ):
        mismatch_penalty += penalties.date_of_birth

    if match_result.birth_year_mismatch:
        mismatch_penalty += penalties.birth_year

    mismatch_penalty += (
        penalties.country
        if match_result.country_mismatch
        else 0.0
    )

    mismatch_penalty += (
        penalties.entity_type
        if match_result.entity_type_mismatch
        else 0.0
    )

    mismatch_penalty += (
        penalties.gender
        if match_result.gender_mismatch
        else 0.0
    )

    score -= mismatch_penalty

    if match_result.identifier_match:
        score = max(score, 0.85)

    final_score = max(
        0.0,
        min(1.0, score),
    )

    return CandidateMatchScoreBreakdown(
        name_score=name_score,
        jaro_winkler_score=jaro_winkler_score,
        levenshtein_score=levenshtein_score,
        phonetic_match=phonetic_match,
        identifier_score=identifier_score,
        date_of_birth_score=date_of_birth_score,
        birth_year_score=birth_year_score,
        country_score=country_score,
        entity_type_score=entity_type_score,
        gender_score=gender_score,
        mismatch_penalty=mismatch_penalty,
        final_score=final_score,
    )

def build_candidate_match_result(
    subject_name: str,
    candidate: SanctionsCandidate,
    subject_identifiers: tuple[str, ...] = (),
    subject_date_of_birth: str | None = None,
    subject_countries: tuple[str, ...] = (),
    subject_entity_type: str | None = None,
    subject_gender: str | None = None,
) -> CandidateMatchResult:
    evidence = build_name_match_evidence(
        subject_name,
        candidate,
    )

    identifier_evidence = identifier_match(
        subject_identifiers,
        candidate,
    )

    identifier_mismatch_evidence = identifier_mismatch(
        subject_identifiers,
        candidate,
    )

    date_of_birth_evidence = date_of_birth_match(
        subject_date_of_birth,
        candidate,
    )

    birth_year_evidence = birth_year_match(
        subject_date_of_birth,
        candidate,
    )

    birth_year_mismatch_evidence = birth_year_mismatch(
        subject_date_of_birth,
        candidate,
    )

    country_evidence = country_match(
        subject_countries,
        candidate,
    )

    country_value_available = any(
        value and value.strip()
        for value in (
            candidate.country,
            candidate.nationality,
        )
    )

    entity_type_evidence = entity_type_match(
        subject_entity_type,
        candidate,
    )

    gender_evidence = gender_match(
        subject_gender,
        candidate,
    )

    return CandidateMatchResult(
        candidate=candidate,
        name_evidence=evidence,
        identifier_supplied=bool(subject_identifiers),
        date_of_birth_supplied=bool(
            subject_date_of_birth
            and subject_date_of_birth.strip()
        ),
        country_supplied=bool(subject_countries),
        entity_type_supplied=bool(
            subject_entity_type
            and subject_entity_type.strip()
        ),
        gender_supplied=bool(
            subject_gender
            and subject_gender.strip()
        ),
        identifier_match=identifier_evidence,
        date_of_birth_match=date_of_birth_evidence,
        birth_year_match=birth_year_evidence,
        birth_year_mismatch=birth_year_mismatch_evidence,
        country_match=country_evidence,
        entity_type_match=entity_type_evidence,
        gender_match=gender_evidence,
        identifier_mismatch=identifier_mismatch_evidence,
        date_of_birth_mismatch=explicit_value_mismatch(
            subject_date_of_birth,
            candidate.date_of_birth,
        ),
        country_mismatch=(
            bool(subject_countries)
            and country_value_available
            and not country_evidence
        ),
        entity_type_mismatch=explicit_value_mismatch(
            subject_entity_type,
            candidate.entity_type,
        ),
        gender_mismatch=explicit_value_mismatch(
            subject_gender,
            candidate.gender,
        ),
    )

def is_candidate_name_match(
    match_result: CandidateMatchResult,
    threshold: float = 0.85,
) -> bool:
    evidence = match_result.name_evidence

    if evidence.exact_match:
        return True

    return evidence.jaro_winkler_score >= threshold

def identifier_match(
    subject_identifiers: tuple[str, ...],
    candidate: SanctionsCandidate,
) -> bool:
    if not subject_identifiers:
        return False

    candidate_identifiers = {
        identifier.strip().casefold()
        for identifier in candidate.identifiers
        if identifier and identifier.strip()
    }

    if not candidate_identifiers:
        return False

    return any(
        identifier.strip().casefold() in candidate_identifiers
        for identifier in subject_identifiers
        if identifier and identifier.strip()
    )

def identifier_mismatch(
    subject_identifiers: tuple[str, ...],
    candidate: SanctionsCandidate,
) -> bool:
    if not subject_identifiers:
        return False

    candidate_identifiers = {
        identifier.strip().casefold()
        for identifier in candidate.identifiers
        if identifier and identifier.strip()
    }

    if not candidate_identifiers:
        return False

    normalized_subject_identifiers = {
        identifier.strip().casefold()
        for identifier in subject_identifiers
        if identifier and identifier.strip()
    }

    if not normalized_subject_identifiers:
        return False

    return normalized_subject_identifiers.isdisjoint(
        candidate_identifiers
    )

def is_candidate_match(
    match_result: CandidateMatchResult,
    name_threshold: float = 0.85,
) -> bool:
    if match_result.identifier_match:
        return True

    return is_candidate_name_match(
        match_result,
        threshold=name_threshold,
    )

def date_of_birth_match(
    subject_date_of_birth: str | None,
    candidate: SanctionsCandidate,
) -> bool:
    if not subject_date_of_birth or not candidate.date_of_birth:
        return False

    return (
        subject_date_of_birth.strip().casefold()
        == candidate.date_of_birth.strip().casefold()
    )

def birth_year_match(
    subject_date_of_birth: str | None,
    candidate: SanctionsCandidate,
) -> bool:
    if not subject_date_of_birth or not candidate.date_of_birth:
        return False

    subject_year = subject_date_of_birth.strip()[:4]
    candidate_year = candidate.date_of_birth.strip()[:4]

    if not (
        subject_year.isdigit()
        and candidate_year.isdigit()
    ):
        return False

    return subject_year == candidate_year

def birth_year_mismatch(
    subject_date_of_birth: str | None,
    candidate: SanctionsCandidate,
) -> bool:
    if not subject_date_of_birth or not candidate.date_of_birth:
        return False

    subject_year = subject_date_of_birth.strip()[:4]
    candidate_year = candidate.date_of_birth.strip()[:4]

    if not (
        subject_year.isdigit()
        and candidate_year.isdigit()
    ):
        return False

    return subject_year != candidate_year

def country_match(
    subject_countries: tuple[str, ...],
    candidate: SanctionsCandidate,
) -> bool:
    if not subject_countries:
        return False

    candidate_countries = {
        value.strip().casefold()
        for value in (
            candidate.country,
            candidate.nationality,
        )
        if value and value.strip()
    }

    if not candidate_countries:
        return False

    return any(
        country.strip().casefold() in candidate_countries
        for country in subject_countries
        if country and country.strip()
    )

def entity_type_match(
    subject_entity_type: str | None,
    candidate: SanctionsCandidate,
) -> bool:
    if not subject_entity_type or not candidate.entity_type:
        return False

    return (
        subject_entity_type.strip().casefold()
        == candidate.entity_type.strip().casefold()
    )

def gender_match(
    subject_gender: str | None,
    candidate: SanctionsCandidate,
) -> bool:
    if not subject_gender or not candidate.gender:
        return False

    return (
        subject_gender.strip().casefold()
        == candidate.gender.strip().casefold()
    )

def explicit_value_mismatch(
    subject_value: str | None,
    candidate_value: str | None,
) -> bool:
    if not subject_value or not candidate_value:
        return False

    return (
        subject_value.strip().casefold()
        != candidate_value.strip().casefold()
    )

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

def calculate_candidate_match_score(
    match_result: CandidateMatchResult,
    weights: CandidateMatchWeights,
    penalties: CandidateMatchPenalties | None = None,
    name_weights: NameMatchWeights | None = None,
) -> float:
    breakdown = build_candidate_match_score_breakdown(
        match_result,
        weights,
        penalties,
        name_weights,
    )

    return breakdown.final_score

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
        sources=tuple(discover_sanctions_sources()),
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

def build_screening_coverage_summary(
    sources_discovered: int,
    source_results: list[SourceScreeningResult],
) -> ScreeningCoverageSummary:
    matches = sum(
        1
        for result in source_results
        if result.status == SourceScreeningStatus.MATCH
    )

    possible_matches = sum(
        1
        for result in source_results
        if result.status == SourceScreeningStatus.POSSIBLE_MATCH
    )

    no_matches = sum(
        1
        for result in source_results
        if result.status == SourceScreeningStatus.NO_MATCH
    )

    unavailable = sum(
        1
        for result in source_results
        if result.status == SourceScreeningStatus.UNAVAILABLE
    )

    errors = sum(
        1
        for result in source_results
        if result.status == SourceScreeningStatus.ERROR
    )

    sources_checked = sum(
        1
        for result in source_results
        if result.status
        in {
            SourceScreeningStatus.MATCH,
            SourceScreeningStatus.POSSIBLE_MATCH,
            SourceScreeningStatus.NO_MATCH,
        }
    )

    return ScreeningCoverageSummary(
        sources_discovered=sources_discovered,
        sources_checked=sources_checked,
        matches=matches,
        possible_matches=possible_matches,
        no_matches=no_matches,
        unavailable=unavailable,
        errors=errors,
    )

def evaluate_global_candidates(
    subject_id: str,
    subject_type: str,
    subject_name: str,
    subject_identifiers: tuple[str, ...] = (),
    subject_date_of_birth: str | None = None,
    subject_countries: tuple[str, ...] = (),
    subject_entity_type: str | None = None,
    subject_gender: str | None = None,
    weights: CandidateMatchWeights | None = None,
    penalties: CandidateMatchPenalties | None = None,
    name_weights: NameMatchWeights | None = None,
    thresholds: CandidateMatchThresholds | None = None,
) -> GlobalCandidateEvaluation:
    plan, candidate_map, retrieval_results = load_global_source_candidates(
        subject_id=subject_id,
        subject_type=subject_type,
    )

    source_evaluations: list[SourceCandidateEvaluation] = []
    source_results: list[SourceScreeningResult] = []

    retrieval_by_source = {
        result.source_id: result
        for result in retrieval_results
    }

    for source in plan.sources:
        retrieval = retrieval_by_source.get(source.source_id)

        if retrieval is None:
            source_results.append(
                SourceScreeningResult(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    status=SourceScreeningStatus.ERROR,
                    checked_at=datetime.now(timezone.utc),
                    screening_completed=False,
                    message="No retrieval result was returned for this source.",
                )
            )
            continue

        if not retrieval.available:
            source_results.append(
                SourceScreeningResult(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    status=SourceScreeningStatus.UNAVAILABLE,
                    checked_at=retrieval.checked_at,
                    screening_completed=False,
                    message=retrieval.message,
                )
            )
            continue

        source_evaluation = evaluate_source_candidates(
            source=source,
            subject_name=subject_name,
            candidates=candidate_map.get(source.source_id, []),
            subject_identifiers=subject_identifiers,
            subject_date_of_birth=subject_date_of_birth,
            subject_countries=subject_countries,
            subject_entity_type=subject_entity_type,
            subject_gender=subject_gender,
            weights=weights,
            penalties=penalties,
            name_weights=name_weights,
            thresholds=thresholds,
        )

        source_evaluations.append(source_evaluation)

        source_results.append(
            SourceScreeningResult(
                source_id=source.source_id,
                source_name=source.source_name,
                status=source_evaluation.status,
                checked_at=source_evaluation.checked_at,
                screening_completed=True,
            )
        )

    coverage = build_screening_coverage_summary(
        sources_discovered=len(plan.sources),
        source_results=source_results,
    )
    source_evaluations_tuple = tuple(source_evaluations)

    return GlobalCandidateEvaluation(
        subject_id=subject_id,
        subject_type=subject_type,
        source_evaluations=tuple(source_evaluations),
        status=get_global_screening_status(source_evaluations_tuple),
        coverage=coverage,
        checked_at=datetime.now(timezone.utc),
    )

def get_global_screening_status(
    source_evaluations: tuple[SourceCandidateEvaluation, ...],
) -> SourceScreeningStatus:
    if any(
        evaluation.status == SourceScreeningStatus.MATCH
        for evaluation in source_evaluations
    ):
        return SourceScreeningStatus.MATCH

    if any(
        evaluation.status == SourceScreeningStatus.POSSIBLE_MATCH
        for evaluation in source_evaluations
    ):
        return SourceScreeningStatus.POSSIBLE_MATCH

    return SourceScreeningStatus.NO_MATCH

def get_positive_source_evaluations(
    global_result: GlobalCandidateEvaluation,
) -> tuple[SourceCandidateEvaluation, ...]:
    return tuple(
        evaluation
        for evaluation in global_result.source_evaluations
        if evaluation.status
        in {
            SourceScreeningStatus.MATCH,
            SourceScreeningStatus.POSSIBLE_MATCH,
        }
    )

def get_positive_candidate_evaluations(
    global_result: GlobalCandidateEvaluation,
) -> tuple[EvaluatedCandidateMatch, ...]:
    positive_candidates: list[EvaluatedCandidateMatch] = []

    for source_evaluation in global_result.source_evaluations:
        for evaluation in source_evaluation.evaluations:
            if evaluation.status in {
                SourceScreeningStatus.MATCH,
                SourceScreeningStatus.POSSIBLE_MATCH,
            }:
                positive_candidates.append(evaluation)

    return tuple(positive_candidates)

def build_positive_sanctions_findings(
    global_result: GlobalCandidateEvaluation,
) -> tuple[PositiveSanctionsFinding, ...]:
    findings: list[PositiveSanctionsFinding] = []

    for evaluation in get_positive_candidate_evaluations(global_result):
        candidate = evaluation.match_result.candidate

        source = get_source_by_id(candidate.source_id)

        findings.append(
            PositiveSanctionsFinding(
                source_id=candidate.source_id,
                source_name=(
                    source.source_name
                    if source is not None
                    else candidate.source_id
                ),
                source_uid=candidate.source_uid,
                candidate_name=candidate.name,
                issuing_country=(
                    source.issuing_country
                    if source is not None
                    else "UNKNOWN"
                ),
                status=evaluation.status,
                score=evaluation.score_breakdown.final_score,
            )
        )

    return tuple(findings)

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