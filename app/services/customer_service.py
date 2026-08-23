from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.repository import (
    create_customer_with_next_number,
    get_all_customers,
    get_customer_by_number,
    update_customer,
    search_customers,
    get_customer_investigations
)

from app.utils.logger import logger


# ============================================================
# CREATE CUSTOMER
# ============================================================

def create_new_customer(
    db: Session,
    name: str,
    customer_type: str,
    country: str,
    pan: str | None = None,
    gst_cin: str | None = None
):
    today = datetime.now().strftime("%Y%m%d")

    prefix = f"CUS-{today}-"

    customer_id = str(uuid4())

    customer = create_customer_with_next_number(
        db=db,
        customer_id=customer_id,
        prefix=prefix,
        name=name,
        customer_type=customer_type,
        country=country,
        pan=pan,
        gst_cin=gst_cin
    )

    logger.info(
        f"Customer created: "
        f"{customer.customer_number} | "
        f"Name: {customer.name}"
    )

    return customer


# ============================================================
# GET CUSTOMER
# ============================================================

def get_all_customers_service(
    db: Session
):
    return get_all_customers(db)


def get_customer_service(
    db: Session,
    customer_number: str
):
    return get_customer_by_number(
        db=db,
        customer_number=customer_number
    )


# ============================================================
# UPDATE CUSTOMER PROFILE
# ============================================================

def update_customer_service(
    db: Session,
    customer_number: str,
    name: str | None = None,
    customer_type: str | None = None,
    country: str | None = None,
    pan: str | None = None,
    gst_cin: str | None = None
):
    customer = update_customer(
        db=db,
        customer_number=customer_number,
        name=name,
        customer_type=customer_type,
        country=country,
        pan=pan,
        gst_cin=gst_cin
    )

    if customer:
        logger.info(
            f"Customer updated: "
            f"{customer.customer_number}"
        )

    return customer


# ============================================================
# DELETE / ARCHIVE CUSTOMER
# ============================================================

def delete_customer_service(
    db: Session,
    customer_number: str
):
    customer = get_customer_by_number(
        db=db,
        customer_number=customer_number
    )

    if customer is None:
        return None, "Customer not found"

    investigations = get_customer_investigations(
        db=db,
        customer_number=customer_number
    )

    if investigations:
        return (
            None,
            "Customer cannot be deleted because "
            "investigation history exists"
        )

    customer.status = "Inactive"

    db.commit()
    db.refresh(customer)

    logger.info(
        f"Customer deactivated: "
        f"{customer.customer_number}"
    )

    return customer, None


# ============================================================
# SEARCH CUSTOMERS
# ============================================================

def search_customers_service(
    db: Session,
    name: str | None = None,
    country: str | None = None,
    status: str | None = None,
    pan: str | None = None,
    customer_type: str | None = None
):
    return search_customers(
        db=db,
        name=name,
        country=country,
        status=status,
        pan=pan,
        customer_type=customer_type
    )


# ============================================================
# CUSTOMER INVESTIGATION HISTORY
# ============================================================

def get_customer_investigations_service(
    db: Session,
    customer_number: str
):
    customer = get_customer_by_number(
        db=db,
        customer_number=customer_number
    )

    if customer is None:
        return None, "Customer not found"

    investigations = get_customer_investigations(
        db=db,
        customer_number=customer_number
    )

    return investigations, None