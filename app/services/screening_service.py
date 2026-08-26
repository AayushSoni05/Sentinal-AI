# ============================================================
# SCREENING SERVICE
# ============================================================

from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.repository import (
    create_screening_result,
     get_screening_results
)
from app.services.screening_providers import (
    MockScreeningProvider
)

# ============================================================
# GET SCREENING RESULTS
# ============================================================

def get_screening_results_service(
    db: Session,
    kyc_profile_id: str
):
    results = get_screening_results(
        db=db,
        kyc_profile_id=kyc_profile_id
    )

    return results, None

# ============================================================
# SCREENING TYPES
# ============================================================

SCREENING_TYPES = [
    "SANCTIONS",
    "PEP",
    "ADVERSE_MEDIA"
]

# ============================================================
# SCREENING POLICY BY ROLE
# ============================================================

SCREENING_POLICY = {
    "UBO": [
        "SANCTIONS",
        "PEP",
        "ADVERSE_MEDIA"
    ],

    "Director": [
        "SANCTIONS",
        "PEP",
        "ADVERSE_MEDIA"
    ],

    "Authorized Person": [
        "SANCTIONS",
        "PEP",
        "ADVERSE_MEDIA"
    ],

    "Authorized Signatory": [
        "SANCTIONS",
        "PEP"
    ],

    "Shareholder": [
        "SANCTIONS",
        "PEP"
    ],

    "Controller": [
        "SANCTIONS",
        "PEP",
        "ADVERSE_MEDIA"
    ]
}

# ============================================================
# SCREENING RESULT STATUSES
# ============================================================

ALLOWED_SCREENING_RESULTS = {
    "CLEAR",
    "MATCH",
    "POSSIBLE_MATCH",
    "CONFIRMED_MATCH",
    "ERROR"
}

# ============================================================
# VALIDATE SCREENING RESULT
# ============================================================

def validate_screening_result(
    result: str
):
    if result not in ALLOWED_SCREENING_RESULTS:
        return (
            False,
            "Invalid screening result"
        )

    return True, None

# ============================================================
# BUILD SCREENING PLAN
# ============================================================

def build_screening_plan(
    subjects
):
    screening_plan = []

    for subject in subjects:

        screening_types = SCREENING_POLICY.get(
            subject["relationship_role"],
            []
        )

        for screening_type in screening_types:

            screening_plan.append({
                "subject_type": subject["subject_type"],
                "subject_id": subject["subject_id"],
                "name": subject["name"],
                "relationship_role": subject["relationship_role"],
                "screening_type": screening_type
            })

    return deduplicate_screening_plan(
        screening_plan
    )

# ============================================================
# CHECK SCREENING COMPLETENESS
# ============================================================

def check_screening_completeness(
    screening_plan,
    screening_results
):
    expected_tasks = {
        (
            task["subject_type"],
            task["subject_id"],
            task["relationship_role"],
            task["screening_type"]
        )
        for task in screening_plan
    }

    completed_tasks = {
        (
            result.subject_type,
            result.subject_id,
            result.relationship_role,
            result.screening_type
        )
        for result in screening_results
        if (
            result.subject_type is not None
            and result.subject_id is not None
            and result.relationship_role is not None
        )
    }

    missing_tasks = expected_tasks - completed_tasks

    return {
        "is_complete": len(missing_tasks) == 0,
        "expected_count": len(expected_tasks),
        "completed_count": len(completed_tasks),
        "missing_tasks": [
            {
                "subject_type": task[0],
                "subject_id": task[1],
                "relationship_role": task[2],
                "screening_type": task[3]
            }
            for task in sorted(missing_tasks)
        ]
    }

# ============================================================
# MOCK SCREENING PROVIDER
# ============================================================

def run_mock_screening(
    screening_task
):
    return {
        "subject_type": screening_task["subject_type"],
        "subject_id": screening_task["subject_id"],
        "name": screening_task["name"],
        "relationship_role": screening_task["relationship_role"],
        "screening_type": screening_task["screening_type"],
        "provider": "MOCK_PROVIDER",
        "result": "CLEAR",
        "matched_name": None,
        "match_confidence": None,
        "evidence": "Mock screening execution"
    }

# ============================================================
# EXECUTE SCREENING TASK
# ============================================================

def execute_screening_task(
    db: Session,
    screening_task,
    kyc_profile_id: str
):
    provider = MockScreeningProvider()

    provider_result = provider.screen(
        name=screening_task["name"],
        screening_type=screening_task["screening_type"],
        subject_type=screening_task["subject_type"],
        subject_id=screening_task["subject_id"],
        relationship_role=screening_task["relationship_role"]
    )

    screening_result, error = save_screening_result(
        db=db,
        kyc_profile_id=kyc_profile_id,
        subject_type=provider_result["subject_type"],
        subject_id=provider_result["subject_id"],
        relationship_role=provider_result["relationship_role"],
        screening_type=provider_result["screening_type"],
        provider=provider_result["provider"],
        result=provider_result["result"],
        matched_name=provider_result["matched_name"],
        match_confidence=provider_result["match_confidence"],
        evidence=provider_result["evidence"]
    )

    if error:
        return None, error

    return screening_result, None

# ============================================================
# EXECUTE SCREENING PLAN
# ============================================================

def execute_screening_plan(
    db: Session,
    subjects,
    kyc_profile_id: str
):
    screening_plan = build_screening_plan(
        subjects
    )

    results = []
    errors = []

    for screening_task in screening_plan:

        result, error = execute_screening_task(
            db=db,
            screening_task=screening_task,
            kyc_profile_id=kyc_profile_id
        )

        if error:
            errors.append({
                "screening_type":
                    screening_task["screening_type"],
                "subject_id":
                    screening_task["subject_id"],
                "error": error
            })

            continue

        results.append(result)

    return {
        "total_tasks": len(screening_plan),
        "successful_tasks": len(results),
        "failed_tasks": len(errors),
        "results": results,
        "errors": errors
    }

# ============================================================
# BUILD SCREENING SUMMARY
# ============================================================

def build_screening_summary(
    screening_results,
    completeness=None
):
    summary = {
    "total_results": len(screening_results),
    "clear": 0,
    "matches": 0,
    "possible_matches": 0,
    "confirmed_matches": 0,
    "errors": 0,
    "overall_status": "REVIEW"
}

    for result in screening_results:

        if result.result == "CLEAR":
            summary["clear"] += 1

        elif result.result == "MATCH":
            summary["matches"] += 1

        elif result.result == "POSSIBLE_MATCH":
            summary["possible_matches"] += 1

        elif result.result == "CONFIRMED_MATCH":
            summary["confirmed_matches"] += 1

        elif result.result == "ERROR":
            summary["errors"] += 1

    # --------------------------------------------------------
    # SCREENING COMPLETENESS
    # --------------------------------------------------------

    if completeness is not None:
        if not completeness["is_complete"]:
            summary["overall_status"] = "REVIEW"
            return summary

    if summary["errors"] > 0:
        summary["overall_status"] = "ERROR"

    elif summary["matches"] > 0:
        summary["overall_status"] = "MATCH"

    elif summary["possible_matches"] > 0:
        summary["overall_status"] = "REVIEW"

    elif summary["total_results"] > 0:
        summary["overall_status"] = "CLEAR"

    return summary
# ============================================================
# GET SCREENING SUMMARY
# ============================================================

def get_screening_summary(
    db: Session,
    kyc_profile_id: str,
    screening_plan
):
    results, error = get_screening_results_service(
        db=db,
        kyc_profile_id=kyc_profile_id
    )

    if error:
        return None, error

    completeness = check_screening_completeness(
        screening_plan=screening_plan,
        screening_results=results
    )

    summary = build_screening_summary(
        screening_results=results,
        completeness=completeness
    )

    summary["completeness"] = completeness

    return summary, None

# ============================================================
# REMOVE DUPLICATE SCREENING TASKS
# ============================================================

def deduplicate_screening_plan(
    screening_plan
):
    unique_tasks = []
    seen = set()

    for task in screening_plan:

        key = (
            task["subject_type"],
            task["subject_id"],
            task["screening_type"]
        )

        if key in seen:
            continue

        seen.add(key)
        unique_tasks.append(task)

    return unique_tasks

# ============================================================
# SAVE SCREENING RESULT
# ============================================================

def save_screening_result(
    db: Session,
    kyc_profile_id: str,
    subject_type: str,
    subject_id: str,
    relationship_role: str,
    screening_type: str,
    provider: str,
    result: str,
    matched_name: str | None = None,
    match_confidence: str | None = None,
    evidence: str | None = None,
    checked_at=None
):
    valid, error = validate_screening_result(
        result
    )

    if not valid:
        return None, error
    result_id = str(uuid4())

    screening_result = create_screening_result(
        db=db,
        result_id=result_id,
        kyc_profile_id=kyc_profile_id,
        subject_type=subject_type,
        subject_id=subject_id,
        relationship_role=relationship_role,
        screening_type=screening_type,
        provider=provider,
        result=result,
        matched_name=matched_name,
        match_confidence=match_confidence,
        evidence=evidence,
        checked_at=checked_at
    )

    return screening_result, None

