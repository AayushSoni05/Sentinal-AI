# ============================================================
# COMPANY CDD SERVICE
# ============================================================

from sqlalchemy.orm import Session

from app.database.models import (
    EntityRelationship,
    Person,
    LegalEntity
)

from app.services.onboarding_service import (
    get_onboarding_requirements
)

# ============================================================
# GET COMPANY RELATIONSHIPS
# ============================================================

def get_company_relationships(
    db: Session,
    legal_entity_id: str,
    relationship_type: str | None = None
):
    query = (
        db.query(EntityRelationship)
        .filter(
            EntityRelationship.to_legal_entity_id
            == legal_entity_id
        )
    )

    if relationship_type is not None:
        query = query.filter(
            EntityRelationship.relationship_type
            == relationship_type
        )

    relationships = query.all()

    results = []

    for relationship in relationships:

        if relationship.from_person_id:
            person = (
                db.query(Person)
                .filter(
                    Person.id
                    == relationship.from_person_id
                )
                .first()
            )

            if person:
                results.append({
                    "relationship_id":
                        relationship.id,
                    "relationship_type":
                        relationship.relationship_type,
                    "subject_type": "Person",
                    "subject_id": person.id,
                    "name": person.full_name,
                    "subject_country": person.country_of_residence,
                    "subject_identifiers": None,
                    "ownership_percentage":
                        relationship.ownership_percentage,
                    "voting_percentage":
                        relationship.voting_percentage,
                    "is_control":
                        relationship.is_control
                })

        elif relationship.from_legal_entity_id:
            entity = (
                db.query(LegalEntity)
                .filter(
                    LegalEntity.id
                    == relationship.from_legal_entity_id
                )
                .first()
            )

            if entity:
                results.append({
                    "relationship_id":
                        relationship.id,
                    "relationship_type":
                        relationship.relationship_type,
                    "subject_type": "LegalEntity",
                    "subject_id": entity.id,
                    "name": entity.legal_name,
                    "subject_country":entity.country_of_incorporation,
                    "subject_identifiers": None,
                    "ownership_percentage":
                        relationship.ownership_percentage,
                    "voting_percentage":
                        relationship.voting_percentage,
                    "is_control":
                        relationship.is_control
                })

    return results

# ============================================================
# GET COMPANY CDD PARTIES
# ============================================================

def get_company_cdd_parties(
    db: Session,
    legal_entity_id: str
):
    relationships = get_company_relationships(
        db=db,
        legal_entity_id=legal_entity_id
    )

    result = {
        "directors": [],
        "authorized_persons": [],
        "authorized_signatories": [],
        "shareholders": [],
        "controllers": [],
        "ubos": []
    }

    relationship_map = {
        "DIRECTOR_OF": "directors",
        "AUTHORIZED_PERSON_OF": "authorized_persons",
        "AUTHORIZED_SIGNATORY_OF": "authorized_signatories",
        "SHAREHOLDER_OF": "shareholders",
        "CONTROLS": "controllers",
        "UBO_OF": "ubos"
    }


    for relationship in relationships:
        key = relationship_map.get(
            relationship["relationship_type"]
        )

        if key:
            result[key].append(
                relationship
            )

    return result

# ============================================================
# CHECK COMPANY CDD COMPLETENESS
# ============================================================

def check_company_cdd_completeness(
    db: Session,
    legal_entity_id: str,
    customer_type: str = "Company"
):
    requirements, error = get_onboarding_requirements(
        customer_type
    )

    if requirements is None:
        return None, error

    parties = get_company_cdd_parties(
        db=db,
        legal_entity_id=legal_entity_id
    )

    missing_sections = []

    required_sections = requirements["required_sections"]

    if "ownership_control" in required_sections:

        if not parties["directors"]:
            missing_sections.append("directors")

        if not parties["shareholders"]:
            missing_sections.append("shareholders")

        if not parties["controllers"]:
            missing_sections.append("controllers")

        if not parties["ubos"]:
            missing_sections.append("ubos")

    if "authorized_persons" in required_sections:

        if not parties["authorized_persons"]:
            missing_sections.append(
                "authorized_persons"
            )

        if not parties["authorized_signatories"]:
            missing_sections.append(
                "authorized_signatories"
            )

    return {
        "legal_entity_id": legal_entity_id,
        "customer_type": customer_type,
        "is_complete": len(missing_sections) == 0,
        "missing_sections": missing_sections
    }, None

# ============================================================
# GET COMPANY SCREENING SUBJECTS
# ============================================================

def get_company_screening_subjects(
    db: Session,
    legal_entity_id: str
):
    parties = get_company_cdd_parties(
        db=db,
        legal_entity_id=legal_entity_id
    )

    subjects = []

    included_roles = {
        "directors",
        "authorized_persons",
        "authorized_signatories",
        "shareholders",
        "controllers",
        "ubos"
    }

    role_labels = {
        "directors": "Director",
        "authorized_persons": "Authorized Person",
        "authorized_signatories": "Authorized Signatory",
        "shareholders": "Shareholder",
        "controllers": "Controller",
        "ubos": "UBO"
    }

    for role in included_roles:

        for party in parties[role]:

            subjects.append({
                "subject_type": party["subject_type"],
                "subject_id": party["subject_id"],
                "name": party["name"],
                "relationship_role": role_labels[role],
                "subject_country": party["subject_country"],
                "subject_identifiers": party["subject_identifiers"]
            })

    return subjects