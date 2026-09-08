from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.auth.roles import require_maker
from app.database.models import User, Customer, Person, LegalEntity

from app.services.entity_relationship_service import (
    create_entity_relationship_service
)

from app.database.models import (
    User,
    Customer,
    Person,
    LegalEntity,
    EntityRelationship
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

    from_person_number: str | None = None
    from_legal_entity_number: str | None = None

    ownership_percentage: float | None = None
    voting_percentage: float | None = None

    is_control: bool = False

    effective_from: datetime | None = None
    effective_to: datetime | None = None

    evidence_reference: str | None = None


@router.post(
    "/customers/{customer_number}/relationships"
)
def create_entity_relationship(
    customer_number: str,
    request: EntityRelationshipRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.customer_number == customer_number
        )
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    if customer.customer_type != "Company":
        raise HTTPException(
            status_code=400,
            detail="Relationships are only available for Company customers"
        )

    if not customer.legal_entity_id:
        raise HTTPException(
            status_code=400,
            detail="Company customer is missing legal entity"
        )

    legal_entity_id = customer.legal_entity_id
    from_person_id = None

    if request.from_person_number:
        person = (
            db.query(Person)
            .filter(
                Person.person_number == request.from_person_number
            )
            .first()
        )

        if person is None:
            raise HTTPException(
                status_code=404,
                detail="Person not found"
            )

        from_person_id = person.id

    from_legal_entity_id = None

    if request.from_legal_entity_number:
        legal_entity = (
            db.query(LegalEntity)
            .filter(
                LegalEntity.legal_entity_number
                == request.from_legal_entity_number
            )
            .first()
        )

        if legal_entity is None:
            raise HTTPException(
                status_code=404,
                detail="Source legal entity not found"
            )

        from_legal_entity_id = legal_entity.id

    relationship, error = (
        create_entity_relationship_service(
            db=db,
            relationship_type=request.relationship_type,
            from_person_id=from_person_id,
            from_legal_entity_id=from_legal_entity_id,
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

    from_person_number = None
    if relationship.from_person_id:
        person = (
            db.query(Person)
            .filter(Person.id == relationship.from_person_id)
            .first()
        )
        if person:
            from_person_number = person.person_number

    from_legal_entity_number = None
    if relationship.from_legal_entity_id:
        source_legal_entity = (
            db.query(LegalEntity)
            .filter(
                LegalEntity.id == relationship.from_legal_entity_id
            )
            .first()
        )
        if source_legal_entity:
            from_legal_entity_number = (
                source_legal_entity.legal_entity_number
            )

    target_customer = (
        db.query(Customer)
        .filter(
            Customer.legal_entity_id ==
            relationship.to_legal_entity_id
        )
        .first()
    )

    return {
        "relationship_id": relationship.id,
        "relationship_type":
            relationship.relationship_type,
        "from_person_number": from_person_number,
        "from_legal_entity_number": from_legal_entity_number,
        "to_customer_number": (
            target_customer.customer_number
            if target_customer
            else None
        ),
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

@router.get(
    "/customers/{customer_number}/relationships"
)
def get_customer_relationships(
    customer_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.customer_number == customer_number
        )
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    if customer.customer_type != "Company":
        raise HTTPException(
            status_code=400,
            detail="Relationships are only available for Company customers"
        )

    if not customer.legal_entity_id:
        raise HTTPException(
            status_code=400,
            detail="Company customer is missing legal entity"
        )

    relationships = (
        db.query(EntityRelationship)
        .filter(
            EntityRelationship.to_legal_entity_id
            == customer.legal_entity_id
        )
        .all()
    )

    results = []

    for relationship in relationships:

        from_person_number = None

        if relationship.from_person_id:
            person = (
                db.query(Person)
                .filter(
                    Person.id == relationship.from_person_id
                )
                .first()
            )

            if person:
                from_person_number = person.person_number

        from_legal_entity_number = None

        if relationship.from_legal_entity_id:
            legal_entity = (
                db.query(LegalEntity)
                .filter(
                    LegalEntity.id
                    == relationship.from_legal_entity_id
                )
                .first()
            )

            if legal_entity:
                from_legal_entity_number = (
                    legal_entity.legal_entity_number
                )

        results.append({
            "relationship_id": relationship.id,
            "relationship_type":
                relationship.relationship_type,
            "from_person_number":
                from_person_number,
            "from_legal_entity_number":
                from_legal_entity_number,
            "to_customer_number":
                customer.customer_number,
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
                relationship.evidence_reference
        })

    return {
        "customer_number": customer.customer_number,
        "relationships": results,
        "count": len(results)
    }