from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.models import KYCProfile
from app.database.repository import get_customer_by_number


# ============================================================
# CREATE KYC PROFILE
# ============================================================

def create_kyc_profile(
    db: Session,
    customer_number: str,
    data
):
    customer = get_customer_by_number(
        db=db,
        customer_number=customer_number
    )

    if customer is None:
        return None, "Customer not found"

    existing_profile = (
        db.query(KYCProfile)
        .filter(
            KYCProfile.customer_id == customer.id
        )
        .first()
    )

    if existing_profile is not None:
        return None, "KYC profile already exists"

    profile = KYCProfile(
        id=str(uuid4()),
        customer_id=customer.id,
        identity_type=data.identity_type,
        identity_number=data.identity_number,
        aadhaar_number=data.aadhaar_number,
        pan_number=data.pan_number,
        onboarding_channel=data.onboarding_channel,
        customer_country=data.customer_country,
        occupation=data.occupation,
        source_of_funds_type=data.source_of_funds_type,
        funds_documentation=data.funds_documentation,
        monthly_turnover=data.monthly_turnover,
        actual_monthly_turnover=data.actual_monthly_turnover,
        product_category=data.product_category
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile, None


# ============================================================
# GET KYC PROFILE
# ============================================================

def get_kyc_profile(
    db: Session,
    customer_number: str
):
    customer = get_customer_by_number(
        db=db,
        customer_number=customer_number
    )

    if customer is None:
        return None, "Customer not found"

    profile = (
        db.query(KYCProfile)
        .filter(
            KYCProfile.customer_id == customer.id
        )
        .first()
    )

    if profile is None:
        return None, "KYC profile not found"

    return profile, None


# ============================================================
# UPDATE KYC PROFILE
# ============================================================

def update_kyc_profile(
    db: Session,
    customer_number: str,
    data
):
    customer = get_customer_by_number(
        db=db,
        customer_number=customer_number
    )

    if customer is None:
        return None, "Customer not found"

    profile = (
        db.query(KYCProfile)
        .filter(
            KYCProfile.customer_id == customer.id
        )
        .first()
    )

    if profile is None:
        return None, "KYC profile not found"

    fields = [
        "identity_type",
        "identity_number",
        "aadhaar_number",
        "pan_number",
        "onboarding_channel",
        "customer_country",
        "occupation",
        "source_of_funds_type",
        "funds_documentation",
        "monthly_turnover",
        "actual_monthly_turnover",
        "product_category"
    ]

    for field in fields:
        value = getattr(data, field)

        if value is not None:
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile, None