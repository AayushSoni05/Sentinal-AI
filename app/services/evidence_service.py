from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.models import Evidence


# ============================================================
# ALLOWED VERIFICATION STATUSES
# ============================================================

ALLOWED_VERIFICATION_STATUSES = {
    "Not Provided",
    "Provided",
    "Pending Verification",
    "Verified",
    "Rejected",
    "Expired"
}

ALLOWED_VERIFICATION_TRANSITIONS = {
    "Not Provided": {
        "Provided"
    },

    "Provided": {
        "Pending Verification"
    },

    "Pending Verification": {
        "Verified",
        "Rejected"
    },

    "Verified": {
        "Expired"
    },

    "Rejected": {
        "Pending Verification"
    },

    "Expired": {
        "Pending Verification"
    }
}


# ============================================================
# CREATE EVIDENCE
# ============================================================

def create_evidence(
    db: Session,
    subject_type: str,
    subject_id: str,
    document_type: str,
    document_number: str | None = None,
    issuing_authority: str | None = None,
    issuing_country: str | None = None,
    issue_date=None,
    expiry_date=None,
    storage_reference: str | None = None,
    metadata_text: str | None = None
):
    evidence = Evidence(
        id=str(uuid4()),
        subject_type=subject_type,
        subject_id=subject_id,
        document_type=document_type,
        document_number=document_number,
        issuing_authority=issuing_authority,
        issuing_country=issuing_country,
        issue_date=issue_date,
        expiry_date=expiry_date,
        verification_status="Provided",
        storage_reference=storage_reference,
        metadata_text=metadata_text
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


# ============================================================
# GET EVIDENCE
# ============================================================

def get_evidence(
    db: Session,
    evidence_id: str
):
    return (
        db.query(Evidence)
        .filter(Evidence.id == evidence_id)
        .first()
    )


# ============================================================
# UPDATE VERIFICATION STATUS
# ============================================================

def update_evidence_verification(
    db: Session,
    evidence_id: str,
    verification_status: str,
    verification_method: str | None = None,
    verified_by: str | None = None
):
    if verification_status not in ALLOWED_VERIFICATION_STATUSES:
        return None, "Invalid verification status"

    evidence = (
        db.query(Evidence)
        .filter(Evidence.id == evidence_id)
        .first()
    )

    if evidence is None:
        return None, "Evidence not found"

    allowed_next_statuses = ALLOWED_VERIFICATION_TRANSITIONS.get(
        evidence.verification_status,
        set()
    )

    if verification_status not in allowed_next_statuses:
        return (
            None,
            (
                f"Invalid verification transition: "
                f"{evidence.verification_status} "
                f"-> {verification_status}"
            )
        )

    evidence.verification_status = verification_status
    evidence.verification_method = verification_method
    evidence.verified_by = verified_by

    if verification_status == "Verified":
        from datetime import datetime

        evidence.verified_at = datetime.utcnow()

    db.commit()
    db.refresh(evidence)

    return evidence, None