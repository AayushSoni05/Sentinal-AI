from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.repository import (
    create_investigation_with_next_number,
    get_all_investigations,
    get_investigation_by_number,
    update_investigation,
    delete_investigation,
    get_customer_by_number,
    search_investigations,
    get_screening_results,
    get_latest_screening_results
)

from app.utils.logger import logger

from app.services.audit_service import create_audit_log

from app.services.company_cdd_service import (
    check_company_cdd_completeness,
    get_company_screening_subjects
)

from app.services.screening_service import (
    get_screening_summary,
    build_screening_plan
)

# ============================================================
# INVESTIGATION LIFECYCLE
# ============================================================

ALLOWED_STATUS_TRANSITIONS = {
    "Draft": {"Submitted"},
    "Submitted": {"Under Review"},
    "Under Review": {"Investigation"},
    "Investigation": {"Decision"},
    "Decision": set(),

    # Terminal / legacy states
    "Approved": set(),
    "Rejected": set(),
    "Cancelled": set(),
}


# ============================================================
# CREATE INVESTIGATION
# ============================================================

def create_new_investigation(
    db: Session,
    customer_number: str,
    company_name: str,
    user_id: str | None = None
):
    today = datetime.now().strftime("%Y%m%d")

    prefix = f"INV-{today}-"

    customer = get_customer_by_number(
        db=db,
        customer_number=customer_number
    )

    if customer is None:
        return None, "Customer not found"

    if customer.status == "Blocked":
        return None, "Blocked customers cannot create investigations"

    if customer.status == "Inactive":
        return None, "Inactive customers cannot create investigations"

    investigation_id = str(uuid4())

    investigation = create_investigation_with_next_number(
        db=db,
        investigation_id=investigation_id,
        prefix=prefix,
        customer_id=customer.id,
        company_name=company_name
    )

    logger.info(
        f"Investigation created: "
        f"{investigation.investigation_number} | "
        f"Customer: {customer.customer_number} | "
        f"Company: {investigation.company_name}"
    )

    create_audit_log(
        db=db,
        user_id=user_id,
        action="CREATE_INVESTIGATION",
        entity_type="Investigation",
        entity_id=investigation.investigation_number,
        old_value=None,
        new_value="Draft",
        reason=None
    )

    db.commit()
    db.refresh(investigation)

    return investigation, None


# ============================================================
# GET INVESTIGATION
# ============================================================

def get_all_investigations_service(
    db: Session
):
    return get_all_investigations(db)


def get_investigation_service(
    db: Session,
    investigation_number: str
):
    return get_investigation_by_number(
        db=db,
        investigation_number=investigation_number
    )

# ============================================================
# GET INVESTIGATION MATCH REVIEW
# ============================================================

def get_investigation_match_review(
    db: Session,
    investigation_number: str
):
    investigation = get_investigation_by_number(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        return None, "Investigation not found"

    customer = investigation.customer

    if customer is None:
        return None, "Investigation customer not found"

    kyc_profile = customer.kyc_profile

    if kyc_profile is None:
        return None, "KYC profile not found"

    screening_results = get_latest_screening_results(
        db=db,
        kyc_profile_id=kyc_profile.id
    )

    review_results = [
        {
            "id": result.id,
            "subject_type": result.subject_type,
            "subject_id": result.subject_id,
            "relationship_role": result.relationship_role,
            "screening_type": result.screening_type,
            "provider": result.provider,
            "result": result.result,
            "matched_name": result.matched_name,
            "match_confidence": result.match_confidence,
            "source_uid": result.source_uid,
            "country_match": result.country_match,
            "identifier_match": result.identifier_match,
            "match_strength": result.match_strength,
            "evidence_strength": result.evidence_strength,
            "evidence": result.evidence,
            "checked_at": result.checked_at
        }
        for result in screening_results
        if result.result in {
            "MATCH",
            "POSSIBLE_MATCH",
            "CONFIRMED_MATCH"
        }
    ]

    return {
        "investigation_number":
            investigation.investigation_number,
        "investigation_id":
            investigation.id,
        "status":
            investigation.status,
        "match_count":
            len(review_results),
        "matches":
            review_results
    }, None

# ============================================================
# GET INVESTIGATION SCREENING RESULTS
# ============================================================

def get_investigation_screening_results(
    db: Session,
    investigation_number: str
):
    investigation = get_investigation_by_number(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        return None, "Investigation not found"

    customer = investigation.customer

    if customer is None:
        return None, "Investigation customer not found"

    kyc_profile = customer.kyc_profile

    if kyc_profile is None:
        return None, "KYC profile not found"

    screening_results = get_latest_screening_results(
        db=db,
        kyc_profile_id=kyc_profile.id
    )

    return {
        "investigation_number":
            investigation.investigation_number,

        "investigation_id":
            investigation.id,

        "customer_id":
            investigation.customer_id,

        "company_name":
            investigation.company_name,

        "status":
            investigation.status,

        "screening_results": [
            {
                "id": result.id,
                "subject_type": result.subject_type,
                "subject_id": result.subject_id,
                "relationship_role":
                    result.relationship_role,
                "screening_type":
                    result.screening_type,
                "provider":
                    result.provider,
                "result":
                    result.result,
                "matched_name":
                    result.matched_name,
                "match_confidence":
                    result.match_confidence,
                "source_uid":
                    result.source_uid,
                "country_match":
                    result.country_match,
                "identifier_match":
                    result.identifier_match,
                "match_strength":
                    result.match_strength,
                "evidence_strength":
                    result.evidence_strength,
                "evidence":
                    result.evidence,
                "checked_at":
                    result.checked_at
            }
            for result in screening_results
        ]
    }, None

# ============================================================
# EVALUATE INVESTIGATION FOR REVIEW
# ============================================================

def evaluate_investigation_review(
    db: Session,
    investigation_number: str
):
    investigation = get_investigation_by_number(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        return None, "Investigation not found"

    customer = investigation.customer

    if customer is None:
        return None, "Investigation customer not found"

    legal_entity_id = customer.legal_entity_id

    if legal_entity_id is None:
        return None, "Customer is not linked to a legal entity"

    # --------------------------------------------------------
    # CDD COMPLETENESS
    # --------------------------------------------------------

    cdd_completeness, error = (
        check_company_cdd_completeness(
            db=db,
            legal_entity_id=legal_entity_id,
            customer_type="Company"
        )
    )

    if error:
        return None, error

    # --------------------------------------------------------
    # KYC PROFILE
    # --------------------------------------------------------

    kyc_profile = customer.kyc_profile

    if kyc_profile is None:
        return None, "KYC profile not found"

    # --------------------------------------------------------
    # SCREENING PLAN
    # --------------------------------------------------------

    subjects = get_company_screening_subjects(
        db=db,
        legal_entity_id=legal_entity_id
    )

    screening_plan = build_screening_plan(
        subjects
    )

    # --------------------------------------------------------
    # SCREENING SUMMARY
    # --------------------------------------------------------

    screening_summary, error = get_screening_summary(
        db=db,
        kyc_profile_id=kyc_profile.id,
        screening_plan=screening_plan
    )

    if error:
        return None, error

    # --------------------------------------------------------
    # REVIEW DECISION
    # --------------------------------------------------------

    if not cdd_completeness["is_complete"]:
        review_status = "REVIEW_REQUIRED"
        review_reason = "CDD_INCOMPLETE"

    elif not screening_summary["completeness"]["is_complete"]:
        review_status = "REVIEW_REQUIRED"
        review_reason = "SCREENING_INCOMPLETE"

    elif (
        screening_summary["overall_status"]
        == "CONFIRMED_MATCH"
    ):
        review_status = "ESCALATE"
        review_reason = "CONFIRMED_SCREENING_MATCH"

    elif (
        screening_summary["overall_status"]
        in {"MATCH", "REVIEW", "ERROR"}
    ):
        review_status = "REVIEW_REQUIRED"
        review_reason = "SCREENING_REVIEW_REQUIRED"

    else:
        review_status = "READY_FOR_DECISION"
        review_reason = "CDD_AND_SCREENING_CLEAR"

    return {
        "investigation_number":
            investigation.investigation_number,

        "investigation_status":
            investigation.status,

        "cdd_completeness":
            cdd_completeness,

        "screening_summary":
            screening_summary,

        "review_status":
            review_status,

        "review_reason":
            review_reason
    }, None

# ============================================================
# UPDATE INVESTIGATION DETAILS
# ============================================================

def update_investigation_service(
    db: Session,
    investigation_number: str,
    company_name: str | None = None
):
    investigation = update_investigation(
        db=db,
        investigation_number=investigation_number,
        company_name=company_name
    )

    if investigation:
        logger.info(
            f"Investigation updated: "
            f"{investigation.investigation_number}"
        )

    return investigation


# ============================================================
# DELETE INVESTIGATION
# ============================================================

def delete_investigation_service(
    db: Session,
    investigation_number: str
):
    investigation = delete_investigation(
        db=db,
        investigation_number=investigation_number
    )

    if investigation:
        logger.info(
            f"Investigation deleted: "
            f"{investigation.investigation_number}"
        )

    return investigation


# ============================================================
# SEARCH INVESTIGATIONS
# ============================================================

def search_investigations_service(
    db: Session,
    status: str | None = None,
    customer_number: str | None = None,
    investigation_number: str | None = None,
    company_name: str | None = None
):
    return search_investigations(
        db=db,
        status=status,
        customer_number=customer_number,
        investigation_number=investigation_number,
        company_name=company_name
    )


# ============================================================
# CHANGE INVESTIGATION STATUS
# ============================================================

def change_investigation_status(
    db: Session,
    investigation_number: str,
    new_status: str,
    user_id: str | None = None
):
    investigation = get_investigation_by_number(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        return None, "Investigation not found"

    current_status = investigation.status

    # Once cancelled, the investigation cannot be reopened.
    if current_status == "Cancelled":
        return (
            None,
            "Cancelled investigations cannot change status"
        )

    # Cancellation is always available from any non-cancelled state.
    if new_status == "Cancelled":
        allowed_statuses = {"Cancelled"}

    else:
        allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(
            current_status,
            set()
        )

    if new_status not in allowed_statuses:
        return (
            None,
            f"Invalid status transition: "
            f"{current_status} -> {new_status}"
        )

    create_audit_log(
        db=db,
        user_id=user_id,
        action="INVESTIGATION_STATUS_CHANGE",
        entity_type="Investigation",
        entity_id=investigation.investigation_number,
        old_value=current_status,
        new_value=new_status,
        reason=None
    )

    investigation.status = new_status

    db.commit()
    db.refresh(investigation)

    logger.info(
        f"Investigation status changed: "
        f"{investigation.investigation_number} | "
        f"{current_status} -> {new_status}"
    )

    return investigation, None