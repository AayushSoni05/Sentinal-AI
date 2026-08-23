from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal

from app.schemas.customer import (
    CustomerRequest,
    CustomerUpdate
)

from app.services.customer_service import (
    create_new_customer,
    get_customer_service,
    update_customer_service,
    delete_customer_service,
    search_customers_service,
    get_customer_investigations_service
)


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# CREATE CUSTOMER
# ============================================================

@router.post("/customers")
def create_customer(
    request: CustomerRequest,
    db: Session = Depends(get_db)
):
    customer = create_new_customer(
        db=db,
        name=request.name,
        customer_type=request.customer_type,
        country=request.country,
        pan=request.pan,
        gst_cin=request.gst_cin
    )

    return {
        "id": customer.id,
        "customer_number": customer.customer_number,
        "name": customer.name,
        "customer_type": customer.customer_type,
        "country": customer.country,
        "pan": customer.pan,
        "gst_cin": customer.gst_cin,
        "status": customer.status,
        "created_at": customer.created_at,
        "message": "Customer created successfully"
    }


# ============================================================
# CUSTOMER SEARCH / LIST
# ============================================================

@router.get("/customers")
def search_customers(
    name: str | None = None,
    country: str | None = None,
    status: str | None = None,
    pan: str | None = None,
    customer_type: str | None = None,
    db: Session = Depends(get_db)
):
    customers = search_customers_service(
        db=db,
        name=name,
        country=country,
        status=status,
        pan=pan,
        customer_type=customer_type
    )

    return [
        {
            "id": customer.id,
            "customer_number": customer.customer_number,
            "name": customer.name,
            "customer_type": customer.customer_type,
            "country": customer.country,
            "pan": customer.pan,
            "gst_cin": customer.gst_cin,
            "status": customer.status,
            "created_at": customer.created_at
        }
        for customer in customers
    ]


# ============================================================
# GET ONE CUSTOMER
# ============================================================

@router.get("/customers/{customer_number}")
def get_customer(
    customer_number: str,
    db: Session = Depends(get_db)
):
    customer = get_customer_service(
        db=db,
        customer_number=customer_number
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return {
        "id": customer.id,
        "customer_number": customer.customer_number,
        "name": customer.name,
        "customer_type": customer.customer_type,
        "country": customer.country,
        "pan": customer.pan,
        "gst_cin": customer.gst_cin,
        "status": customer.status,
        "created_at": customer.created_at
    }


# ============================================================
# CUSTOMER INVESTIGATION HISTORY
# ============================================================

@router.get(
    "/customers/{customer_number}/investigations"
)
def get_customer_investigations(
    customer_number: str,
    db: Session = Depends(get_db)
):
    investigations, error = get_customer_investigations_service(
        db=db,
        customer_number=customer_number
    )

    if investigations is None:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    return [
        {
            "id": investigation.id,
            "investigation_number": investigation.investigation_number,
            "customer_id": investigation.customer_id,
            "company_name": investigation.company_name,
            "status": investigation.status,
            "created_at": investigation.created_at
        }
        for investigation in investigations
    ]


# ============================================================
# UPDATE CUSTOMER PROFILE
# ============================================================

@router.put("/customers/{customer_number}")
def update_customer(
    customer_number: str,
    request: CustomerUpdate,
    db: Session = Depends(get_db)
):
    customer = update_customer_service(
        db=db,
        customer_number=customer_number,
        name=request.name,
        customer_type=request.customer_type,
        country=request.country,
        pan=request.pan,
        gst_cin=request.gst_cin
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return {
        "id": customer.id,
        "customer_number": customer.customer_number,
        "name": customer.name,
        "customer_type": customer.customer_type,
        "country": customer.country,
        "pan": customer.pan,
        "gst_cin": customer.gst_cin,
        "status": customer.status,
        "message": "Customer updated successfully"
    }


# ============================================================
# DELETE CUSTOMER
# ============================================================

@router.delete("/customers/{customer_number}")
def delete_customer(
    customer_number: str,
    db: Session = Depends(get_db)
):
    customer = delete_customer_service(
        db=db,
        customer_number=customer_number
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return {
        "customer_number": customer.customer_number,
        "message": "Customer deleted successfully"
    }