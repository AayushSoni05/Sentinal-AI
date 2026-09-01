from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.auth.roles import require_maker
from app.database.models import User

from app.services.entity_relationship_service import (
    create_entity_relationship_service
)


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# CREATE ENTITY RELATIONSHIP
# ============================================================

class EntityRelationshipRequest(BaseModel):
    relationship_type: str

    from_person_id: str | None = None
    from_legal_entity_id: str | None = None

    ownership_percentage: float | None = None
    voting_percentage: float | None = None

    is_control: bool = False

    effective_from: datetime | None = None
    effective_to: datetime | None = None

    evidence_reference: str | None = None


@router.post(
    "/legal-entities/{legal_entity_id}/relationships"
)
def create_entity_relationship(
    legal_entity_id: str,
    request: EntityRelationshipRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    relationship, error = (
        create_entity_relationship_service(
            db=db,
            relationship_type=request.relationship_type,
            from_person_id=request.from_person_id,
            from_legal_entity_id=request.from_legal_entity_id,
            to_legal_entity_id=legal_entity_id,
            ownership_percentage=request.ownership_percentage,
            voting_percentage=request.voting_percentage,
            is_control=request.is_control,
            effective_from=request.effective_from,
            effective_to=request.effective_to,
            evidence_reference=request.evidence_reference
        )
    )

    if relationship is None:
        raise HTTPException(
            status_code=400,
            detail=error
        )

    db.commit()
    db.refresh(relationship)

    return {
        "relationship_id": relationship.id,
        "relationship_type":
            relationship.relationship_type,
        "from_person_id":
            relationship.from_person_id,
        "from_legal_entity_id":
            relationship.from_legal_entity_id,
        "to_legal_entity_id":
            relationship.to_legal_entity_id,
        "ownership_percentage":
            relationship.ownership_percentage,
        "voting_percentage":
            relationship.voting_percentage,
        "is_control":
            relationship.is_control,
        "effective_from":
            relationship.effective_from,
        "effective_to":
            relationship.effective_to,
        "evidence_reference":
            relationship.evidence_reference,
        "created_by":
            current_user.username,
        "message":
            "Entity relationship created successfully"
    }