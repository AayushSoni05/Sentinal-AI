from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal

from app.schemas.investigation import (
    InvestigationRequest,
    InvestigationUpdate
)

from app.auth.roles import (
    require_maker,
    require_checker
)

from app.database.models import User

from app.services.investigation_service import (
    create_new_investigation,
    get_investigation_service,
    update_investigation_service,
    delete_investigation_service,
    change_investigation_status,
    search_investigations_service,
    get_investigation_screening_results,
    get_investigation_match_review,
    execute_investigation_screening,
    evaluate_investigation_review
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    investigation, error = create_new_investigation(
        db=db,
        customer_number=request.customer_number,
        company_name=request.company_name,
        user_id=current_user.id
    )

    if investigation is None:
        if error == "Customer not found":
            raise HTTPException(
                status_code=404,
                detail=error
            )

        raise HTTPException(
            status_code=403,
            detail=error
        )

    return {
        "id": investigation.id,
        "investigation_number": investigation.investigation_number,
        "customer_id": investigation.customer_id,
        "company_name": investigation.company_name,
        "status": investigation.status,
        "created_by": current_user.username,
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_checker)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_checker)
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
# GET INVESTIGATION SCREENING RESULTS
# ============================================================

@router.get(
    "/investigations/{investigation_number}/screening-results"
)
def get_investigation_screening_results_api(
    investigation_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_checker)
):
    result, error = get_investigation_screening_results(
        db=db,
        investigation_number=investigation_number
    )

    if result is None:
        status_code = (
            404
            if error in {
                "Investigation not found",
                "Investigation customer not found",
                "KYC profile not found"
            }
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return result

# ============================================================
# EXECUTE INVESTIGATION SCREENING
# ============================================================

@router.post(
    "/investigations/{investigation_number}/screening"
)
def execute_investigation_screening_api(
    investigation_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    result, error = execute_investigation_screening(
        db=db,
        investigation_number=investigation_number
    )

    if result is None:
        status_code = (
            404
            if error in {
                "Investigation not found",
                "Investigation customer not found",
                "KYC profile not found"
            }
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return {
        **result,
        "executed_by": current_user.username,
        "message": "Investigation screening executed successfully"
    }

# ============================================================
# EVALUATE INVESTIGATION FOR REVIEW
# ============================================================

@router.get(
    "/investigations/{investigation_number}/review-evaluation"
)
def evaluate_investigation_review_api(
    investigation_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_checker)
):
    result, error = evaluate_investigation_review(
        db=db,
        investigation_number=investigation_number
    )

    if result is None:
        status_code = (
            404
            if error in {
                "Investigation not found",
                "Investigation customer not found",
                "KYC profile not found"
            }
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return result

# ============================================================
# UPDATE INVESTIGATION DETAILS
# ============================================================

@router.put("/investigations/{investigation_number}")
def update_investigation(
    investigation_number: str,
    request: InvestigationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
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
        "updated_by": current_user.username,
        "message": "Investigation updated successfully"
    }


# ============================================================
# DELETE INVESTIGATION
# ============================================================

@router.delete("/investigations/{investigation_number}")
def delete_investigation(
    investigation_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
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
        "deleted_by": current_user.username,
        "message": "Investigation deleted successfully"
    }


# ============================================================
# SUBMIT INVESTIGATION
# ============================================================

@router.post("/investigations/{investigation_number}/submit")
def submit_investigation(
    investigation_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    investigation, error = change_investigation_status(
        db=db,
        investigation_number=investigation_number,
        new_status="Submitted",
        user_id=current_user.id
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
        "submitted_by": current_user.username,
        "message": "Investigation submitted successfully"
    }


# ============================================================
# MOVE TO REVIEW
# ============================================================

@router.post("/investigations/{investigation_number}/review")
def review_investigation(
    investigation_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_checker)
):
    investigation, error = change_investigation_status(
        db=db,
        investigation_number=investigation_number,
        new_status="Under Review",
        user_id=current_user.id
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
        "reviewed_by": current_user.username,
        "message": "Investigation moved to review"
    }


# ============================================================
# START INVESTIGATION
# ============================================================

@router.post("/investigations/{investigation_number}/start")
def start_investigation(
    investigation_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    investigation, error = change_investigation_status(
        db=db,
        investigation_number=investigation_number,
        new_status="Investigation",
        user_id=current_user.id
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
        "started_by": current_user.username,
        "message": "Investigation started successfully"
    }


# ============================================================
# MOVE TO DECISION
# ============================================================

@router.post("/investigations/{investigation_number}/decision")
def move_to_decision(
    investigation_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    investigation, error = change_investigation_status(
        db=db,
        investigation_number=investigation_number,
        new_status="Decision",
        user_id=current_user.id
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
        "moved_by": current_user.username,
        "message": "Investigation moved to decision"
    }


# ============================================================
# CANCEL INVESTIGATION
# ============================================================

@router.post("/investigations/{investigation_number}/cancel")
def cancel_investigation(
    investigation_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    investigation, error = change_investigation_status(
        db=db,
        investigation_number=investigation_number,
        new_status="Cancelled",
        user_id=current_user.id
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
        "cancelled_by": current_user.username,
        "message": "Investigation cancelled successfully"
    }

# ============================================================
# GET INVESTIGATION MATCH REVIEW
# ============================================================

@router.get(
    "/investigations/{investigation_number}/match-review"
)
def get_investigation_match_review_api(
    investigation_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_checker)
):
    result, error = get_investigation_match_review(
        db=db,
        investigation_number=investigation_number
    )

    if result is None:
        status_code = (
            404
            if error in {
                "Investigation not found",
                "Investigation customer not found",
                "KYC profile not found"
            }
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return result