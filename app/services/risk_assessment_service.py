from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.models import RiskAssessment
from app.database.repository import (
    get_investigation_by_number,
    get_risk_assessment,
    create_risk_assessment,
    update_risk_assessment
)
from app.services.kyc_service import check_kyc_completeness
from app.services.investigation_service import evaluate_investigation_review


# ============================================================
# RISK TIER
# ============================================================

def get_risk_tier(
    score: int
):
    if score <= 24:
        return "LOW"

    if score <= 49:
        return "MEDIUM"

    if score <= 74:
        return "HIGH"

    return "CRITICAL"


# ============================================================
# BUILD RISK ASSESSMENT
# ============================================================

def build_risk_assessment(
    db: Session,
    investigation_number: str
):
    investigation = get_investigation_by_number(
        db=db,
        investigation_number=investigation_number
    )

    if investigation is None:
        return None, "Investigation not found"

    if investigation.customer is None:
        return None, "Customer linked to investigation not found"

    customer = investigation.customer

    # --------------------------------------------------------
    # KYC COMPLETENESS
    # --------------------------------------------------------

    kyc_result, kyc_error = check_kyc_completeness(
        db=db,
        customer_number=customer.customer_number
    )

    if kyc_result is None:
        return None, kyc_error

    # --------------------------------------------------------
    # REVIEW EVALUATION
    # --------------------------------------------------------

    review_result, review_error = evaluate_investigation_review(
        db=db,
        investigation_number=investigation_number
    )

    if review_result is None:
        return None, review_error

    # --------------------------------------------------------
    # RISK FACTORS
    # --------------------------------------------------------

    score = 0
    factors = []

    # KYC completeness
    if not kyc_result["is_complete"]:
        score += 25

        factors.append({
            "factor": "KYC",
            "score": 25,
            "reason": "KYC profile is incomplete"
        })

    # CDD completeness
    cdd = review_result.get("cdd_completeness")

    if cdd and not cdd.get("is_complete", False):
        score += 25

        factors.append({
            "factor": "CDD",
            "score": 25,
            "reason": "Customer due diligence is incomplete"
        })

    # Screening outcome
    screening = review_result.get("screening_summary", {})

    confirmed_matches = screening.get(
        "confirmed_matches",
        0
    )

    matches = screening.get(
        "matches",
        0
    )

    possible_matches = screening.get(
        "possible_matches",
        0
    )

    errors = screening.get(
        "errors",
        0
    )

    if confirmed_matches > 0:
        score += 60

        factors.append({
            "factor": "Screening",
            "score": 60,
            "reason": "Confirmed screening match found"
        })

    elif matches > 0:
        score += 40

        factors.append({
            "factor": "Screening",
            "score": 40,
            "reason": "Screening match found"
        })

    elif possible_matches > 0:
        score += 25

        factors.append({
            "factor": "Screening",
            "score": 25,
            "reason": "Possible screening match found"
        })

    if errors > 0:
        score += 15

        factors.append({
            "factor": "Screening",
            "score": 15,
            "reason": "Screening errors detected"
        })

    # --------------------------------------------------------
    # CAP SCORE
    # --------------------------------------------------------

    score = min(score, 100)

    risk_tier = get_risk_tier(
        score=score
    )

    # --------------------------------------------------------
    # ASSESSMENT STATUS
    # --------------------------------------------------------

    assessment_status = "Completed"

    # --------------------------------------------------------
    # REASON
    # --------------------------------------------------------

    if factors:
        assessment_reason = "; ".join(
            factor["reason"]
            for factor in factors
        )
    else:
        assessment_reason = "No current risk factors detected"

    existing_assessment = get_risk_assessment(
        db=db,
        investigation_id=investigation.id
    )

    if existing_assessment is None:
        existing_assessment = create_risk_assessment(
            db=db,
            risk_assessment_id=str(uuid4()),
            investigation_id=investigation.id,
            risk_score=score,
            risk_tier=risk_tier,
            assessment_status=assessment_status,
            assessment_reason=assessment_reason
        )
    else:
        existing_assessment = update_risk_assessment(
            db=db,
            investigation_id=investigation.id,
            risk_score=score,
            risk_tier=risk_tier,
            assessment_status=assessment_status,
            assessment_reason=assessment_reason
        )

    return {
        "investigation_number": investigation_number,
        "customer_number": customer.customer_number,
        "risk_assessment_id": existing_assessment.id,
        "risk_score": score,
        "risk_tier": risk_tier,
        "assessment_status": assessment_status,
        "assessment_reason": assessment_reason,
        "factors": factors
    }, None