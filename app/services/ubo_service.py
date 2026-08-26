# ============================================================
# UBO SERVICE
# ============================================================

from sqlalchemy.orm import Session

from app.database.models import (
    EntityRelationship,
    Person
)

# ============================================================
# UBO POLICY
# ============================================================

DEFAULT_UBO_OWNERSHIP_THRESHOLD = 25.0

# ============================================================
# GET DIRECT UBOS
# ============================================================

def get_direct_ubos(
    db: Session,
    legal_entity_id: str
):
    relationships = (
        db.query(EntityRelationship)
        .filter(
            EntityRelationship.to_legal_entity_id
            == legal_entity_id,

            EntityRelationship.relationship_type
            == "UBO_OF",

            EntityRelationship.from_person_id
            .isnot(None)
        )
        .all()
    )

    ubos = []

    for relationship in relationships:

        person = (
            db.query(Person)
            .filter(
                Person.id
                == relationship.from_person_id
            )
            .first()
        )

        if person:
            ubos.append({
                "person_id": person.id,
                "name": person.full_name,
                "ownership_percentage":
                    relationship.ownership_percentage,
                "voting_percentage":
                    relationship.voting_percentage,
                "is_control":
                    relationship.is_control
            })

    return ubos

# ============================================================
# CALCULATE INDIRECT OWNERSHIP
# ============================================================

def calculate_indirect_ownership(
    db: Session,
    person_id: str,
    legal_entity_id: str,
    visited_entities: set[str] | None = None
):
    if visited_entities is None:
        visited_entities = set()

    # Prevent circular ownership from causing infinite recursion.
    if legal_entity_id in visited_entities:
        return 0.0

    # Keep a path-local copy so separate ownership paths
    # can be evaluated independently.
    current_path = visited_entities | {
        legal_entity_id
    }

    total_ownership = 0.0

    relationships = (
        db.query(EntityRelationship)
        .filter(
            EntityRelationship.to_legal_entity_id
            == legal_entity_id,

            EntityRelationship.relationship_type.in_(
                [
                    "OWNS",
                    "SHAREHOLDER_OF"
                ]
            )
        )
        .all()
    )

    for relationship in relationships:

        ownership = (
            float(relationship.ownership_percentage)
            if relationship.ownership_percentage
            is not None
            else 0.0
        )

        # Ignore invalid ownership values defensively.
        if ownership <= 0:
            continue

        # Direct ownership by the person.
        if relationship.from_person_id == person_id:
            total_ownership += ownership

        # Indirect ownership through another legal entity.
        elif relationship.from_legal_entity_id:

            upstream_ownership = calculate_indirect_ownership(
                db=db,
                person_id=person_id,
                legal_entity_id=(
                    relationship.from_legal_entity_id
                ),
                visited_entities=current_path
            )

            total_ownership += (
                upstream_ownership
                * ownership
                / 100
            )

    return total_ownership

# ============================================================
# DETERMINE IF PERSON IS A POTENTIAL UBO
# ============================================================

def is_potential_ubo(
    db: Session,
    person_id: str,
    legal_entity_id: str,
    threshold: float = DEFAULT_UBO_OWNERSHIP_THRESHOLD
):
    ownership = calculate_indirect_ownership(
        db=db,
        person_id=person_id,
        legal_entity_id=legal_entity_id
    )

    return {
        "person_id": person_id,
        "legal_entity_id": legal_entity_id,
        "effective_ownership_percentage": ownership,
        "threshold": threshold,
        "is_potential_ubo": ownership >= threshold
    }

# ============================================================
# CHECK DIRECT CONTROL
# ============================================================

def has_direct_control(
    db: Session,
    person_id: str,
    legal_entity_id: str
):
    relationship = (
        db.query(EntityRelationship)
        .filter(
            EntityRelationship.from_person_id == person_id,
            EntityRelationship.to_legal_entity_id == legal_entity_id,
            EntityRelationship.is_control == "1"
        )
        .first()
    )

    return relationship is not None

# ============================================================
# DETERMINE UBO BY OWNERSHIP OR CONTROL
# ============================================================

def determine_potential_ubo(
    db: Session,
    person_id: str,
    legal_entity_id: str,
    threshold: float = DEFAULT_UBO_OWNERSHIP_THRESHOLD
):
    effective_ownership = calculate_indirect_ownership(
        db=db,
        person_id=person_id,
        legal_entity_id=legal_entity_id
    )

    direct_control = has_direct_control(
        db=db,
        person_id=person_id,
        legal_entity_id=legal_entity_id
    )

    ownership_qualifies = (
        effective_ownership >= threshold
    )

    if ownership_qualifies and direct_control:
        determination_reason = "ownership_and_control"

    elif ownership_qualifies:
        determination_reason = "ownership_threshold"

    elif direct_control:
        determination_reason = "direct_control"

    else:
        determination_reason = None

    is_potential_ubo = (
        ownership_qualifies
        or direct_control
    )

    return {
        "person_id": person_id,
        "legal_entity_id": legal_entity_id,
        "effective_ownership_percentage": effective_ownership,
        "threshold": threshold,
        "direct_control": direct_control,
        "is_potential_ubo": is_potential_ubo,
        "determination_reason": determination_reason
    }