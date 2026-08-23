from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.repository import (
    create_investigation_decision,
    get_investigation_decision,
    update_investigation_decision,
    get_investigation_by_number,
    update_customer_status
)

from app.utils.logger import logger


# ============================================================
# ALLOWED DECISION VALUES
# ============================================================

ALLOWED_RECOMMENDATIONS = {
    "Clear",
    "Monitor",
    "Review Required",
    "Block Recommended"
}


ALLOWED_ANALYST_DECISIONS = {
    "Agree",
    "Disagree",
    "Needs More Review"
}


ALLOWED_APPROVER_DECISIONS = {
    "Approved",
    "Rejected",
    "Returned"
}


# ============================================================
# RECOMMENDATION → CUSTOMER STATUS
# ============================================================

RECOMMENDATION_STATUS_MAP = {
    "Clear": "Active",
    "Monitor": "Active",
    "Review Required": "Review Required",
    "Block Recommended": "Blocked"
}


# ============================================================
# CREATE RECOMMENDATION
# ============================================================

def create_decision(
    db: Session,
    investigation_number: str,
    recommendation: str,
    reason: str | None = None
):
    investigation = get_investigation_by_number(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        return None, "Investigation not found"

    if investigation.status != "Decision":
        return (
            None,
            "Investigation must be in Decision status"
        )

    if recommendation not in ALLOWED_RECOMMENDATIONS:
        return None, "Invalid recommendation"

    existing_decision = get_investigation_decision(
        db=db,
        investigation_id=investigation.id
    )

    if existing_decision is not None:
        return (
            None,
            "Decision already exists for this investigation"
        )

    decision_id = str(uuid4())

    decision = create_investigation_decision(
        db=db,
        decision_id=decision_id,
        investigation_id=investigation.id,
        recommendation=recommendation,
        reason=reason
    )

    logger.info(
        f"Decision recommendation created: "
        f"{investigation.investigation_number} | "
        f"Recommendation: {recommendation}"
    )

    return decision, None


# ============================================================
# GET DECISION
# ============================================================

def get_decision(
    db: Session,
    investigation_number: str
):
    investigation = get_investigation_by_number(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        return None, "Investigation not found"

    decision = get_investigation_decision(
        db=db,
        investigation_id=investigation.id
    )

    if decision is None:
        return None, "Decision not found"

    return decision, None


# ============================================================
# ANALYST REVIEW
# ============================================================

def submit_analyst_decision(
    db: Session,
    investigation_number: str,
    analyst_decision: str,
    reason: str | None = None
):
    investigation = get_investigation_by_number(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        return None, "Investigation not found"

    decision = get_investigation_decision(
        db=db,
        investigation_id=investigation.id
    )

    if decision is None:
        return None, "Decision not found"

    # Pending is the normal state.
    # Returned means the approver sent it back for more work.
    if decision.approval_status not in {"Pending"}:
        return None, "Decision is already processed"

    if analyst_decision not in ALLOWED_ANALYST_DECISIONS:
        return None, "Invalid analyst decision"

    decision = update_investigation_decision(
        db=db,
        investigation_id=investigation.id,
        analyst_decision=analyst_decision,
        reason=reason,
        approver_decision=None
    )

    logger.info(
        f"Analyst decision submitted: "
        f"{investigation.investigation_number} | "
        f"Decision: {analyst_decision}"
    )

    return decision, None


# ============================================================
# FINAL APPROVER DECISION
# ============================================================

def approve_decision(
    db: Session,
    investigation_number: str,
    approver_decision: str
):
    investigation = get_investigation_by_number(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        return None, "Investigation not found"

    decision = get_investigation_decision(
        db=db,
        investigation_id=investigation.id
    )

    if decision is None:
        return None, "Decision not found"

    if decision.approval_status != "Pending":
        return None, "Decision is already processed"

    if decision.analyst_decision is None:
        return None, (
            "Analyst review is required before final decision"
        )

    if approver_decision not in ALLOWED_APPROVER_DECISIONS:
        return None, "Invalid approver decision"

    # --------------------------------------------------------
    # RETURNED
    # --------------------------------------------------------
    if approver_decision == "Returned":

        decision = update_investigation_decision(
            db=db,
            investigation_id=investigation.id,
            approver_decision="Returned"
        )

        logger.info(
            f"Decision returned for further review: "
            f"{investigation.investigation_number}"
        )

        return decision, None

    # --------------------------------------------------------
    # REJECTED
    # --------------------------------------------------------
    if approver_decision == "Rejected":

        decision = update_investigation_decision(
            db=db,
            investigation_id=investigation.id,
            approval_status="Rejected",
            approver_decision="Rejected"
        )

        logger.info(
            f"Recommendation rejected: "
            f"{investigation.investigation_number} | "
            f"Recommendation: {decision.recommendation}"
        )

        return decision, None

    # --------------------------------------------------------
    # APPROVED
    # --------------------------------------------------------
    if approver_decision == "Approved":

        new_customer_status = RECOMMENDATION_STATUS_MAP.get(
            decision.recommendation
        )

        if new_customer_status is None:
            return (
                None,
                "No customer action defined for recommendation"
            )

        customer = investigation.customer

        if customer is None:
            return (
                None,
                "Customer linked to investigation not found"
            )

        updated_customer = update_customer_status(
            db=db,
            customer_number=customer.customer_number,
            status=new_customer_status
        )

        if updated_customer is None:
            return (
                None,
                "Customer not found"
            )

        decision = update_investigation_decision(
            db=db,
            investigation_id=investigation.id,
            approval_status="Approved",
            approver_decision="Approved"
        )

        logger.info(
            f"Final decision approved: "
            f"{investigation.investigation_number} | "
            f"Recommendation: {decision.recommendation} | "
            f"Customer: {customer.customer_number} | "
            f"New Status: {new_customer_status}"
        )

        return decision, None