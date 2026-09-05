from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.auth.dependencies import get_current_user
from app.database.models import User
from app.services.risk_assessment_service import build_risk_assessment


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# BUILD RISK ASSESSMENT
# ============================================================

@router.get(
    "/investigations/{investigation_number}/risk-assessment"
)
def get_risk_assessment(
    investigation_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result, error = build_risk_assessment(
        db=db,
        investigation_number=investigation_number
    )

    if result is None:
        status_code = (
            404
            if error in {
                "Investigation not found",
                "Customer linked to investigation not found",
                "KYC profile not found"
            }
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return result