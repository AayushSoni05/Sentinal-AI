from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal

from app.services.decision_service import (
    create_decision,
    get_decision,
    submit_analyst_decision,
    approve_decision
)


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# CREATE DECISION RECOMMENDATION
# ============================================================

@router.post(
    "/investigations/{investigation_number}/decision/recommendation"
)
def create_recommendation(
    investigation_number: str,
    recommendation: str,
    reason: str | None = None,
    db: Session = Depends(get_db)
):
    decision, error = create_decision(
        db=db,
        investigation_number=investigation_number,
        recommendation=recommendation,
        reason=reason
    )

    if decision is None:
        if error == "Investigation not found":
            raise HTTPException(
                status_code=404,
                detail=error
            )

        raise HTTPException(
            status_code=400,
            detail=error
        )

    return {
        "investigation_number": investigation_number,
        "recommendation": decision.recommendation,
        "approval_status": decision.approval_status,
        "reason": decision.reason,
        "message": "Decision recommendation created successfully"
    }


# ============================================================
# GET DECISION
# ============================================================

@router.get(
    "/investigations/{investigation_number}/decision/recommendation"
)
def get_recommendation(
    investigation_number: str,
    db: Session = Depends(get_db)
):
    decision, error = get_decision(
        db=db,
        investigation_number=investigation_number
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    return {
        "investigation_number": investigation_number,
        "recommendation": decision.recommendation,
        "analyst_decision": decision.analyst_decision,
        "approval_status": decision.approval_status,
        "approver_decision": decision.approver_decision,
        "reason": decision.reason,
        "created_at": decision.created_at
    }


# ============================================================
# ANALYST REVIEW
# ============================================================

@router.post(
    "/investigations/{investigation_number}/decision/analyst"
)
def analyst_review(
    investigation_number: str,
    analyst_decision: str,
    reason: str | None = None,
    db: Session = Depends(get_db)
):
    decision, error = submit_analyst_decision(
        db=db,
        investigation_number=investigation_number,
        analyst_decision=analyst_decision,
        reason=reason
    )

    if decision is None:
        if error == "Investigation not found":
            raise HTTPException(
                status_code=404,
                detail=error
            )

        raise HTTPException(
            status_code=400,
            detail=error
        )

    return {
        "investigation_number": investigation_number,
        "recommendation": decision.recommendation,
        "analyst_decision": decision.analyst_decision,
        "approval_status": decision.approval_status,
        "message": "Analyst decision recorded successfully"
    }


# ============================================================
# FINAL APPROVER DECISION
# ============================================================

@router.post(
    "/investigations/{investigation_number}/decision/final"
)
def final_decision(
    investigation_number: str,
    approver_decision: str,
    db: Session = Depends(get_db)
):
    decision, error = approve_decision(
        db=db,
        investigation_number=investigation_number,
        approver_decision=approver_decision
    )

    if decision is None:
        if error == "Investigation not found":
            raise HTTPException(
                status_code=404,
                detail=error
            )

        raise HTTPException(
            status_code=400,
            detail=error
        )

    return {
        "investigation_number": investigation_number,
        "recommendation": decision.recommendation,
        "analyst_decision": decision.analyst_decision,
        "approval_status": decision.approval_status,
        "approver_decision": decision.approver_decision,
        "message": "Final approver decision recorded successfully"
    }