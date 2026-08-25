from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal

from app.auth.roles import (
    require_maker,
    require_checker
)

from app.database.models import User

from app.schemas.kyc import (
    KYCRequest,
    KYCUpdate
)

from app.services.kyc_service import (
    create_kyc_profile,
    get_kyc_profile,
    update_kyc_profile
)


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# CREATE KYC PROFILE
# ============================================================

@router.post(
    "/customers/{customer_number}/kyc"
)
def create_kyc(
    customer_number: str,
    request: KYCRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    profile, error = create_kyc_profile(
        db=db,
        customer_number=customer_number,
        data=request
    )

    if profile is None:

        if error == "Customer not found":
            raise HTTPException(
                status_code=404,
                detail=error
            )

        raise HTTPException(
            status_code=400,
            detail=error
        )

    return {
        "customer_number": customer_number,
        "kyc_profile_id": profile.id,
        "message": "KYC profile created successfully",
        "created_by": current_user.username
    }


# ============================================================
# GET KYC PROFILE
# ============================================================

@router.get(
    "/customers/{customer_number}/kyc"
)
def get_kyc(
    customer_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_checker)
):
    profile, error = get_kyc_profile(
        db=db,
        customer_number=customer_number
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    return {
        "customer_number": customer_number,
        "kyc_profile_id": profile.id,
        "identity_type": profile.identity_type,
        "identity_number": profile.identity_number,
        "aadhaar_number": profile.aadhaar_number,
        "pan_number": profile.pan_number,
        "onboarding_channel": profile.onboarding_channel,
        "customer_country": profile.customer_country,
        "pep_status": profile.pep_status,
        "negative_news": profile.negative_news,
        "name_screening_result": profile.name_screening_result,
        "occupation": profile.occupation,
        "source_of_funds_type": profile.source_of_funds_type,
        "funds_documentation": profile.funds_documentation,
        "monthly_turnover": profile.monthly_turnover,
        "actual_monthly_turnover": profile.actual_monthly_turnover,
        "product_category": profile.product_category,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at
    }


# ============================================================
# UPDATE KYC PROFILE
# ============================================================

@router.put(
    "/customers/{customer_number}/kyc"
)
def update_kyc(
    customer_number: str,
    request: KYCUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    profile, error = update_kyc_profile(
        db=db,
        customer_number=customer_number,
        data=request
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    return {
        "customer_number": customer_number,
        "kyc_profile_id": profile.id,
        "message": "KYC profile updated successfully",
        "updated_by": current_user.username
    }