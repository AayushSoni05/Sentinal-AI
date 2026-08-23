from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database.models import (
    Customer,
    Investigation,
    InvestigationDecision
)


# ============================================================
# INVESTIGATION FUNCTIONS
# ============================================================

def get_latest_investigation_number(
    db: Session,
    prefix: str
):
    return (
        db.query(Investigation)
        .filter(
            Investigation.investigation_number.like(f"{prefix}%")
        )
        .order_by(
            desc(Investigation.investigation_number)
        )
        .first()
    )


def create_investigation(
    db: Session,
    investigation_id: str,
    investigation_number: str,
    company_name: str,
    customer_id: str
):
    investigation = Investigation(
        id=investigation_id,
        investigation_number=investigation_number,
        customer_id=customer_id,
        company_name=company_name,
        status="Draft"
    )

    db.add(investigation)
    db.commit()
    db.refresh(investigation)

    return investigation


def get_all_investigations(
    db: Session
):
    return (
        db.query(Investigation)
        .order_by(
            Investigation.created_at.desc()
        )
        .all()
    )


def get_investigation_by_number(
    db: Session,
    investigation_number: str
):
    return (
        db.query(Investigation)
        .filter(
            Investigation.investigation_number
            == investigation_number
        )
        .first()
    )


def update_investigation(
    db: Session,
    investigation_number: str,
    company_name: str | None = None
):
    investigation = get_investigation_by_number(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        return None

    if company_name is not None:
        investigation.company_name = company_name

    db.commit()
    db.refresh(investigation)

    return investigation


def delete_investigation(
    db: Session,
    investigation_number: str
):
    investigation = get_investigation_by_number(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        return None

    db.delete(investigation)
    db.commit()

    return investigation


def search_investigations(
    db: Session,
    status: str | None = None,
    customer_number: str | None = None,
    investigation_number: str | None = None,
    company_name: str | None = None
):
    query = db.query(Investigation)

    if status:
        query = query.filter(
            Investigation.status == status
        )

    if customer_number:
        query = query.join(
            Customer,
            Investigation.customer_id == Customer.id
        ).filter(
            Customer.customer_number == customer_number
        )

    if investigation_number:
        query = query.filter(
            Investigation.investigation_number
            == investigation_number
        )

    if company_name:
        query = query.filter(
            Investigation.company_name.ilike(
                f"%{company_name}%"
            )
        )

    return (
        query
        .order_by(
            Investigation.created_at.desc()
        )
        .all()
    )


def get_customer_investigations(
    db: Session,
    customer_number: str
):
    return (
        db.query(Investigation)
        .join(
            Customer,
            Investigation.customer_id == Customer.id
        )
        .filter(
            Customer.customer_number == customer_number
        )
        .order_by(
            Investigation.created_at.desc()
        )
        .all()
    )


# ============================================================
# CUSTOMER FUNCTIONS
# ============================================================

def create_customer(
    db: Session,
    customer_id: str,
    customer_number: str,
    name: str,
    customer_type: str,
    country: str,
    pan: str | None = None,
    gst_cin: str | None = None
):
    customer = Customer(
        id=customer_id,
        customer_number=customer_number,
        name=name,
        customer_type=customer_type,
        country=country,
        pan=pan,
        gst_cin=gst_cin,
        status="Active"
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def get_all_customers(
    db: Session
):
    return (
        db.query(Customer)
        .order_by(
            Customer.created_at.desc()
        )
        .all()
    )


def get_customer_by_number(
    db: Session,
    customer_number: str
):
    return (
        db.query(Customer)
        .filter(
            Customer.customer_number == customer_number
        )
        .first()
    )


def update_customer(
    db: Session,
    customer_number: str,
    name: str | None = None,
    customer_type: str | None = None,
    country: str | None = None,
    pan: str | None = None,
    gst_cin: str | None = None
):
    customer = get_customer_by_number(
        db=db,
        customer_number=customer_number
    )

    if customer is None:
        return None

    if name is not None:
        customer.name = name

    if customer_type is not None:
        customer.customer_type = customer_type

    if country is not None:
        customer.country = country

    if pan is not None:
        customer.pan = pan

    if gst_cin is not None:
        customer.gst_cin = gst_cin

    db.commit()
    db.refresh(customer)

    return customer


def update_customer_status(
    db: Session,
    customer_number: str,
    status: str
):
    customer = get_customer_by_number(
        db=db,
        customer_number=customer_number
    )

    if customer is None:
        return None

    customer.status = status

    db.commit()
    db.refresh(customer)

    return customer


def delete_customer(
    db: Session,
    customer_number: str
):
    customer = get_customer_by_number(
        db=db,
        customer_number=customer_number
    )

    if customer is None:
        return None

    db.delete(customer)
    db.commit()

    return customer


def search_customers(
    db: Session,
    name: str | None = None,
    country: str | None = None,
    status: str | None = None,
    pan: str | None = None,
    customer_type: str | None = None
):
    query = db.query(Customer)

    if name:
        query = query.filter(
            Customer.name.ilike(f"%{name}%")
        )

    if country:
        query = query.filter(
            Customer.country.ilike(f"%{country}%")
        )

    if status:
        query = query.filter(
            Customer.status == status
        )

    if pan:
        query = query.filter(
            Customer.pan == pan
        )

    if customer_type:
        query = query.filter(
            Customer.customer_type == customer_type
        )

    return (
        query
        .order_by(
            Customer.created_at.desc()
        )
        .all()
    )


# ============================================================
# DECISION / APPROVAL FUNCTIONS
# ============================================================

def create_investigation_decision(
    db: Session,
    decision_id: str,
    investigation_id: str,
    recommendation: str,
    reason: str | None = None
):
    decision = InvestigationDecision(
        id=decision_id,
        investigation_id=investigation_id,
        recommendation=recommendation,
        approval_status="Pending",
        reason=reason
    )

    db.add(decision)
    db.commit()
    db.refresh(decision)

    return decision


def get_investigation_decision(
    db: Session,
    investigation_id: str
):
    return (
        db.query(InvestigationDecision)
        .filter(
            InvestigationDecision.investigation_id
            == investigation_id
        )
        .first()
    )


def update_investigation_decision(
    db: Session,
    investigation_id: str,
    analyst_decision: str | None = None,
    approval_status: str | None = None,
    approver_decision: str | None = None,
    reason: str | None = None
):
    decision = get_investigation_decision(
        db=db,
        investigation_id=investigation_id
    )

    if decision is None:
        return None

    if analyst_decision is not None:
        decision.analyst_decision = analyst_decision

    if approval_status is not None:
        decision.approval_status = approval_status

    if approver_decision is not None:
        decision.approver_decision = approver_decision

    if reason is not None:
        decision.reason = reason

    db.commit()
    db.refresh(decision)

    return decision