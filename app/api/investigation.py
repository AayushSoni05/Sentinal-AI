from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal

from app.schemas.investigation import (
    InvestigationRequest,
    InvestigationUpdate
)

from app.services.investigation_service import (
    create_new_investigation,
    get_investigation_service,
    update_investigation_service,
    delete_investigation_service,
    change_investigation_status,
    search_investigations_service
)


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# CREATE INVESTIGATION
# ============================================================

@router.post("/investigations")
def create_investigation(
    request: InvestigationRequest,
    db: Session = Depends(get_db)
):
    investigation = create_new_investigation(
        db=db,
        customer_number=request.customer_number,
        company_name=request.company_name
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return {
        "id": investigation.id,
        "investigation_number": investigation.investigation_number,
        "customer_id": investigation.customer_id,
        "company_name": investigation.company_name,
        "status": investigation.status,
        "message": "Investigation created successfully"
    }


# ============================================================
# SEARCH / LIST INVESTIGATIONS
# ============================================================

@router.get("/investigations")
def search_investigations(
    status: str | None = None,
    customer_number: str | None = None,
    investigation_number: str | None = None,
    company_name: str | None = None,
    db: Session = Depends(get_db)
):
    investigations = search_investigations_service(
        db=db,
        status=status,
        customer_number=customer_number,
        investigation_number=investigation_number,
        company_name=company_name
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
# GET ONE INVESTIGATION
# ============================================================

@router.get("/investigations/{investigation_number}")
def get_investigation(
    investigation_number: str,
    db: Session = Depends(get_db)
):
    investigation = get_investigation_service(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found"
        )

    return {
        "id": investigation.id,
        "investigation_number": investigation.investigation_number,
        "customer_id": investigation.customer_id,
        "company_name": investigation.company_name,
        "status": investigation.status,
        "created_at": investigation.created_at
    }


# ============================================================
# UPDATE INVESTIGATION DETAILS
# ============================================================

@router.put("/investigations/{investigation_number}")
def update_investigation(
    investigation_number: str,
    request: InvestigationUpdate,
    db: Session = Depends(get_db)
):
    investigation = update_investigation_service(
        db=db,
        investigation_number=investigation_number,
        company_name=request.company_name
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found"
        )

    return {
        "id": investigation.id,
        "investigation_number": investigation.investigation_number,
        "customer_id": investigation.customer_id,
        "company_name": investigation.company_name,
        "status": investigation.status,
        "message": "Investigation updated successfully"
    }


# ============================================================
# DELETE INVESTIGATION
# ============================================================

@router.delete("/investigations/{investigation_number}")
def delete_investigation(
    investigation_number: str,
    db: Session = Depends(get_db)
):
    investigation = delete_investigation_service(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found"
        )

    return {
        "investigation_number": investigation.investigation_number,
        "message": "Investigation deleted successfully"
    }


# ============================================================
# INVESTIGATION LIFECYCLE
# ============================================================

@router.post("/investigations/{investigation_number}/submit")
def submit_investigation(
    investigation_number: str,
    db: Session = Depends(get_db)
):
    investigation, error = change_investigation_status(
        db=db,
        investigation_number=investigation_number,
        new_status="Submitted"
    )

    if investigation is None:
        status_code = (
            404
            if error == "Investigation not found"
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return {
        "investigation_number": investigation.investigation_number,
        "customer_id": investigation.customer_id,
        "status": investigation.status,
        "message": "Investigation submitted successfully"
    }


@router.post("/investigations/{investigation_number}/review")
def review_investigation(
    investigation_number: str,
    db: Session = Depends(get_db)
):
    investigation, error = change_investigation_status(
        db=db,
        investigation_number=investigation_number,
        new_status="Under Review"
    )

    if investigation is None:
        status_code = (
            404
            if error == "Investigation not found"
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return {
        "investigation_number": investigation.investigation_number,
        "customer_id": investigation.customer_id,
        "status": investigation.status,
        "message": "Investigation moved to review"
    }


@router.post("/investigations/{investigation_number}/start")
def start_investigation(
    investigation_number: str,
    db: Session = Depends(get_db)
):
    investigation, error = change_investigation_status(
        db=db,
        investigation_number=investigation_number,
        new_status="Investigation"
    )

    if investigation is None:
        status_code = (
            404
            if error == "Investigation not found"
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return {
        "investigation_number": investigation.investigation_number,
        "customer_id": investigation.customer_id,
        "status": investigation.status,
        "message": "Investigation started successfully"
    }


@router.post("/investigations/{investigation_number}/decision")
def move_to_decision(
    investigation_number: str,
    db: Session = Depends(get_db)
):
    investigation, error = change_investigation_status(
        db=db,
        investigation_number=investigation_number,
        new_status="Decision"
    )

    if investigation is None:
        status_code = (
            404
            if error == "Investigation not found"
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return {
        "investigation_number": investigation.investigation_number,
        "customer_id": investigation.customer_id,
        "status": investigation.status,
        "message": "Investigation moved to decision"
    }


# ============================================================
# CANCEL — AVAILABLE FROM ANY NON-CANCELLED STATUS
# ============================================================

@router.post("/investigations/{investigation_number}/cancel")
def cancel_investigation(
    investigation_number: str,
    db: Session = Depends(get_db)
):
    investigation, error = change_investigation_status(
        db=db,
        investigation_number=investigation_number,
        new_status="Cancelled"
    )

    if investigation is None:
        status_code = (
            404
            if error == "Investigation not found"
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return {
        "investigation_number": investigation.investigation_number,
        "customer_id": investigation.customer_id,
        "status": investigation.status,
        "message": "Investigation cancelled successfully"
    }