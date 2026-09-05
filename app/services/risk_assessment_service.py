from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.models import (
    RiskAssessment
)
from app.database.repository import (
    get_investigation_by_number,
    get_risk_assessment,
    create_risk_assessment,
    update_risk_assessment,
    get_active_risk_rules,
    get_latest_screening_results
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

    # --------------------------------------------------------
    # SCREENING RISK
    # --------------------------------------------------------

    sanctions_assessment = evaluate_sanctions_rule(
        db=db,
        kyc_profile_id=kyc_result["kyc_profile_id"]
    )

    pep_assessment = evaluate_pep_risk(
        db=db,
        kyc_profile_id=kyc_result["kyc_profile_id"]
    )

    adverse_media_assessment = evaluate_adverse_media_risk(
        db=db,
        kyc_profile_id=kyc_result["kyc_profile_id"]
    )

    sanctions_hit_score = sanctions_assessment["hit_score"]

    if sanctions_assessment["action"] == "BLOCK":

        score = 100

        factors.append({
            "factor": "SANCTIONS",
            "score": 100,
            "hit_score": sanctions_hit_score,
            "risk_tier": sanctions_assessment["risk_tier"],
            "action": sanctions_assessment["action"],
            "rule_name": sanctions_assessment["rule_name"],
            "reason": (
                f"Sanctions hit score "
                f"{sanctions_hit_score} triggered "
                "a blocking rule"
            )
        })

    elif sanctions_assessment["action"] == "REVIEW":

        sanctions_score = 0

        if sanctions_hit_score >= 85:
            sanctions_score = 50

        score += sanctions_score

        factors.append({
            "factor": "SANCTIONS",
            "score": sanctions_score,
            "hit_score": sanctions_hit_score,
            "risk_tier": sanctions_assessment["risk_tier"],
            "action": sanctions_assessment["action"],
            "rule_name": sanctions_assessment["rule_name"],
            "reason": (
                f"Sanctions hit score "
                f"{sanctions_hit_score} requires review"
            )
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
        "recommended_action": sanctions_assessment["action"],
        "assessment_status": assessment_status,
        "assessment_reason": assessment_reason,
        "sanctions": {
            "hit_score": sanctions_assessment["hit_score"],
            "rule_name": sanctions_assessment["rule_name"],
            "risk_tier": sanctions_assessment["risk_tier"],
            "recommended_action": sanctions_assessment["action"]
        },
        "pep": pep_assessment,
        "adverse_media": adverse_media_assessment,
        "factors": factors
    }, None
# ============================================================
# FIND MATCHING RISK RULE
# ============================================================

def find_matching_risk_rule(
    db: Session,
    factor: str,
    hit_score: float
):
    rules = get_active_risk_rules(
        db=db,
        factor=factor
    )

    for rule in rules:
        min_score = float(rule.min_score)
        max_score = float(rule.max_score)

        if min_score <= hit_score <= max_score:
            return rule

    return None

# ============================================================
# EVALUATE RISK RULE BY SCORE
# ============================================================

def evaluate_risk_rule_by_score(
    db: Session,
    factor: str,
    hit_score: float
):
    rule = find_matching_risk_rule(
        db=db,
        factor=factor,
        hit_score=hit_score
    )

    if rule is None:
        return {
            "hit_score": hit_score,
            "rule_name": None,
            "risk_tier": None,
            "action": "REVIEW"
        }

    return {
        "hit_score": hit_score,
        "rule_name": rule.rule_name,
        "risk_tier": rule.risk_tier,
        "action": rule.action
    }

# ============================================================
# GET SANCTIONS HIT SCORE
# ============================================================

def get_highest_sanctions_hit_score(
    db: Session,
    kyc_profile_id: str
):
    screening_results = get_latest_screening_results(
        db=db,
        kyc_profile_id=kyc_profile_id
    )

    sanctions_results = [
        result
        for result in screening_results
        if result.screening_type == "SANCTIONS"
    ]

    hit_scores = []

    for result in sanctions_results:
        if result.match_confidence is None:
            continue

        try:
            hit_scores.append(
                float(result.match_confidence)
            )
        except (TypeError, ValueError):
            continue

    if not hit_scores:
        return 0.0

    return max(hit_scores)

# ============================================================
# EVALUATE SANCTIONS RISK RULE
# ============================================================

def evaluate_sanctions_rule(
    db: Session,
    kyc_profile_id: str
):
    hit_score = get_highest_sanctions_hit_score(
        db=db,
        kyc_profile_id=kyc_profile_id
    )

    if hit_score <= 0:
        return {
            "hit_score": 0.0,
            "risk_tier": None,
            "action": None,
            "rule_name": None
        }

    rule = find_matching_risk_rule(
        db=db,
        factor="SANCTIONS",
        hit_score=hit_score
    )

    if rule is None:
        return {
            "hit_score": hit_score,
            "risk_tier": None,
            "action": "REVIEW",
            "rule_name": None
        }

    return {
        "hit_score": hit_score,
        "risk_tier": rule.risk_tier,
        "action": rule.action,
        "rule_name": rule.rule_name
    }

# ============================================================
# GET LATEST SCREENING RESULT FOR FACTOR
# ============================================================

def get_latest_screening_result_for_factor(
    db: Session,
    kyc_profile_id: str,
    screening_type: str
):
    screening_results = get_latest_screening_results(
        db=db,
        kyc_profile_id=kyc_profile_id
    )

    matching_results = [
        result
        for result in screening_results
        if result.screening_type == screening_type
    ]

    if not matching_results:
        return None

    return matching_results[0]

# ============================================================
# EVALUATE PEP RISK
# ============================================================

def evaluate_pep_risk(
    db: Session,
    kyc_profile_id: str
):
    result = get_latest_screening_result_for_factor(
        db=db,
        kyc_profile_id=kyc_profile_id,
        screening_type="PEP"
    )

    if result is None:
        return {
            "factor": "PEP",
            "score": 0,
            "recommended_action": "CLEAR",
            "reason": "No PEP screening result found"
        }

    if result.result in {
        "CONFIRMED_MATCH",
        "MATCH",
        "POSSIBLE_MATCH"
    }:
        return {
            "factor": "PEP",
            "score": 0,
            "recommended_action": "REVIEW",
            "reason": (
                f"PEP screening result: "
                f"{result.result}"
            )
        }

    if result.result in {
        "CLEAR",
        "NO_MATCH"
    }:
        return {
            "factor": "PEP",
            "score": 0,
            "recommended_action": "CLEAR",
            "reason": "No PEP concern detected"
        }

    return {
        "factor": "PEP",
        "score": 0,
        "recommended_action": "REVIEW",
        "reason": (
            f"PEP screening returned "
            f"{result.result}"
        )
    }

# ============================================================
# EVALUATE ADVERSE MEDIA RISK
# ============================================================

def evaluate_adverse_media_risk(
    db: Session,
    kyc_profile_id: str
):
    result = get_latest_screening_result_for_factor(
        db=db,
        kyc_profile_id=kyc_profile_id,
        screening_type="ADVERSE_MEDIA"
    )

    if result is None:
        return {
            "factor": "ADVERSE_MEDIA",
            "score": 0,
            "recommended_action": "CLEAR",
            "reason": "No adverse media screening result found"
        }

    if result.result in {
        "CONFIRMED_MATCH",
        "MATCH",
        "POSSIBLE_MATCH"
    }:
        return {
            "factor": "ADVERSE_MEDIA",
            "score": 0,
            "recommended_action": "REVIEW",
            "reason": (
                f"Adverse media screening result: "
                f"{result.result}"
            )
        }

    if result.result in {
        "CLEAR",
        "NO_MATCH"
    }:
        return {
            "factor": "ADVERSE_MEDIA",
            "score": 0,
            "recommended_action": "CLEAR",
            "reason": "No adverse media concern detected"
        }

    return {
        "factor": "ADVERSE_MEDIA",
        "score": 0,
        "recommended_action": "REVIEW",
        "reason": (
            f"Adverse media screening returned "
            f"{result.result}"
        )
    }