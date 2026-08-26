# ============================================================
# ENTITY RELATIONSHIP SERVICE
# ============================================================

from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.repository import (
    create_entity_relationship
)


# ============================================================
# ALLOWED ENTITY RELATIONSHIP TYPES
# ============================================================

ALLOWED_ENTITY_RELATIONSHIP_TYPES = {
    "OWNS",
    "CONTROLS",
    "DIRECTOR_OF",
    "AUTHORIZED_PERSON_OF",
    "AUTHORIZED_SIGNATORY_OF",
    "SHAREHOLDER_OF",
    "UBO_OF"
}


# ============================================================
# VALIDATE RELATIONSHIP TYPE
# ============================================================

def validate_entity_relationship_type(
    relationship_type: str
):
    if relationship_type not in ALLOWED_ENTITY_RELATIONSHIP_TYPES:
        return False, "Invalid entity relationship type"

    return True, None


# ============================================================
# VALIDATE RELATIONSHIP PARTICIPANTS
# ============================================================

def validate_entity_relationship(
    from_person_id: str | None = None,
    from_legal_entity_id: str | None = None,
    to_legal_entity_id: str | None = None,
    relationship_type: str | None = None
):
    valid, error = validate_entity_relationship_type(
        relationship_type
    )

    if not valid:
        return False, error

    if (
        from_person_id is None
        and from_legal_entity_id is None
    ):
        return (
            False,
            "A relationship must have a source person "
            "or source legal entity"
        )

    if to_legal_entity_id is None:
        return (
            False,
            "A relationship must have a target legal entity"
        )

    if (
        from_person_id is not None
        and from_legal_entity_id is not None
    ):
        return (
            False,
            "A relationship cannot have both "
            "from_person_id and from_legal_entity_id"
        )

    return True, None

# ============================================================
# VALIDATE OWNERSHIP / VOTING PERCENTAGES
# ============================================================

def validate_relationship_percentages(
    relationship_type: str,
    ownership_percentage: float | None = None,
    voting_percentage: float | None = None
):
    ownership_types = {
        "OWNS",
        "SHAREHOLDER_OF",
        "UBO_OF"
    }

    if relationship_type in ownership_types:

        if ownership_percentage is not None:
            if not 0 <= ownership_percentage <= 100:
                return (
                    False,
                    "Ownership percentage must be between 0 and 100"
                )

        if voting_percentage is not None:
            if not 0 <= voting_percentage <= 100:
                return (
                    False,
                    "Voting percentage must be between 0 and 100"
                )

    return True, None

# ============================================================
# VALIDATE CONTROL FLAG
# ============================================================

def validate_relationship_control(
    relationship_type: str,
    is_control: bool
):
    control_types = {
        "CONTROLS",
        "UBO_OF",
        "DIRECTOR_OF"
    }

    if is_control and relationship_type not in control_types:
        return (
            False,
            "is_control=True is not valid for this relationship type"
        )

    return True, None

# ============================================================
# VALIDATE RELATIONSHIP SOURCE TYPE
# ============================================================

RELATIONSHIP_SOURCE_RULES = {
    "OWNS": {
        "person",
        "legal_entity"
    },

    "CONTROLS": {
        "person",
        "legal_entity"
    },

    "DIRECTOR_OF": {
        "person"
    },

    "AUTHORIZED_PERSON_OF": {
        "person"
    },

    "AUTHORIZED_SIGNATORY_OF": {
        "person"
    },

    "SHAREHOLDER_OF": {
        "person",
        "legal_entity"
    },

    "UBO_OF": {
        "person"
    }
}


def validate_relationship_source_type(
    relationship_type: str,
    from_person_id: str | None = None,
    from_legal_entity_id: str | None = None
):
    if from_person_id is not None:
        source_type = "person"

    elif from_legal_entity_id is not None:
        source_type = "legal_entity"

    else:
        return (
            False,
            "Relationship source is required"
        )

    allowed_source_types = RELATIONSHIP_SOURCE_RULES.get(
        relationship_type,
        set()
    )

    if source_type not in allowed_source_types:
        return (
            False,
            (
                f"{relationship_type} cannot have "
                f"{source_type} as its source"
            )
        )

    return True, None

# ============================================================
# CREATE ENTITY RELATIONSHIP
# ============================================================

def create_entity_relationship_service(
    db: Session,
    relationship_type: str,
    from_person_id: str | None = None,
    from_legal_entity_id: str | None = None,
    to_legal_entity_id: str | None = None,
    ownership_percentage: float | None = None,
    voting_percentage: float | None = None,
    is_control: bool = False,
    effective_from=None,
    effective_to=None,
    evidence_reference: str | None = None
):

    valid, error = validate_entity_relationship(
        from_person_id=from_person_id,
        from_legal_entity_id=from_legal_entity_id,
        to_legal_entity_id=to_legal_entity_id,
        relationship_type=relationship_type
    )

    if not valid:
        return None, error

    valid, error = validate_relationship_source_type(
        relationship_type=relationship_type,
        from_person_id=from_person_id,
        from_legal_entity_id=from_legal_entity_id
    )

    if not valid:
        return None, error
    
    valid, error = validate_relationship_percentages(
        relationship_type=relationship_type,
        ownership_percentage=ownership_percentage,
        voting_percentage=voting_percentage
    )

    if not valid:
        return None, error

    valid, error = validate_relationship_control(
        relationship_type=relationship_type,
        is_control=is_control
    )

    if not valid:
        return None, error

    relationship_id = str(uuid4())

    relationship = create_entity_relationship(
        db=db,
        relationship_id=relationship_id,
        relationship_type=relationship_type,
        from_person_id=from_person_id,
        from_legal_entity_id=from_legal_entity_id,
        to_legal_entity_id=to_legal_entity_id,
        ownership_percentage=ownership_percentage,
        voting_percentage=voting_percentage,
        is_control=is_control,
        effective_from=effective_from,
        effective_to=effective_to,
        evidence_reference=evidence_reference
    )

    return relationship, None