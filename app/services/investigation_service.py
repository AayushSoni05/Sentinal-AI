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
    search_investigations
)

from app.utils.logger import logger

from app.services.audit_service import create_audit_log


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