from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.repository import (
    create_investigation_decision,
    get_investigation_decision,
    update_investigation_decision,
    get_investigation_by_number,
    finalize_approved_decision
)

from app.services.audit_service import (
    create_audit_log
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
    reason: str | None = None,
    user_id: str | None = None
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

    if analyst_decision not in ALLOWED_ANALYST_DECISIONS:
        return None, "Invalid analyst decision"

# --------------------------------------------------------
# AUDIT ANALYST ACTION
# --------------------------------------------------------

    create_audit_log(
        db=db,
        user_id=user_id,
        action="ANALYST_REVIEW",
        entity_type="Investigation",
        entity_id=investigation.investigation_number,
        old_value="Analyst review pending",
        new_value=analyst_decision,
        reason=reason
    )

    decision = update_investigation_decision(
        db=db,
        investigation_id=investigation.id,
        analyst_decision=analyst_decision,
        reason=reason
    )

    logger.info(
        f"Analyst decision submitted: "
        f"{investigation.investigation_number} | "
        f"Decision: {analyst_decision}"
    )

    return decision, None

# ============================================================
# FINAL CHECKER DECISION
# ============================================================

def approve_decision(
    db: Session,
    investigation_number: str,
    approver_decision: str,
    reason: str | None = None,
    user_id: str | None = None
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

    if not reason or not reason.strip():
        return None, "Checker reason is required"

    old_status = decision.approval_status

    # --------------------------------------------------------
    # RETURNED
    # --------------------------------------------------------

    if approver_decision == "Returned":

        create_audit_log(
            db=db,
            user_id=user_id,
            action="RETURN_DECISION",
            entity_type="Investigation",
            entity_id=investigation.investigation_number,
            old_value=old_status,
            new_value="Returned",
            reason=reason
        )

        decision = update_investigation_decision(
            db=db,
            investigation_id=investigation.id,
            approver_decision="Returned",
            reason=reason
        )

        logger.info(
            f"Decision returned for further review: "
            f"{investigation.investigation_number} | "
            f"Reason: {reason}"
        )

        return decision, None

    # --------------------------------------------------------
    # REJECTED
    # --------------------------------------------------------

    if approver_decision == "Rejected":

        create_audit_log(
            db=db,
            user_id=user_id,
            action="REJECT_DECISION",
            entity_type="Investigation",
            entity_id=investigation.investigation_number,
            old_value=old_status,
            new_value="Rejected",
            reason=reason
        )

        decision = update_investigation_decision(
            db=db,
            investigation_id=investigation.id,
            approval_status="Rejected",
            approver_decision="Rejected",
            reason=reason
        )

        logger.info(
            f"Recommendation rejected: "
            f"{investigation.investigation_number} | "
            f"Recommendation: {decision.recommendation} | "
            f"Reason: {reason}"
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

        create_audit_log(
            db=db,
            user_id=user_id,
            action="APPROVE_DECISION",
            entity_type="Investigation",
            entity_id=investigation.investigation_number,
            old_value=(
                f"Decision={old_status}; "
                f"Customer={customer.status}"
            ),
            new_value=(
                f"Decision=Approved; "
                f"Customer={new_customer_status}"
            ),
            reason=reason
        )

        updated_customer, finalized_decision = (
            finalize_approved_decision(
                db=db,
                investigation_id=investigation.id,
                customer_number=customer.customer_number,
                customer_status=new_customer_status,
                reason=reason,
                user_id=user_id
            )
        )

        if (
            updated_customer is None
            or finalized_decision is None
        ):
            return (
                None,
                "Unable to finalize approved decision"
            )

        logger.info(
            f"Final decision approved: "
            f"{investigation.investigation_number} | "
            f"Recommendation: "
            f"{finalized_decision.recommendation} | "
            f"Customer: "
            f"{updated_customer.customer_number} | "
            f"New Status: "
            f"{updated_customer.status} | "
            f"Reason: {reason}"
        )

        return finalized_decision, None