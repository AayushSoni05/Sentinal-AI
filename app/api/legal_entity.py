from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.auth.roles import require_maker
from app.database.models import User

from app.schemas.customer import LegalEntityRequest

from app.services.legal_entity_service import create_legal_entity


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/legal-entities")
def create_legal_entity_endpoint(
    request: LegalEntityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    legal_entity = create_legal_entity(
        db=db,
        legal_name=request.legal_name,
        trading_name=request.trading_name,
        entity_type=request.entity_type,
        registration_number=request.registration_number,
        incorporation_date=request.incorporation_date,
        country_of_incorporation=request.country_of_incorporation,
        registered_address=request.registered_address,
        principal_business_address=request.principal_business_address,
        business_activity=request.business_activity,
        industry=request.industry
    )

    return {
        "legal_entity_number": legal_entity.legal_entity_number,
        "legal_name": legal_entity.legal_name,
        "trading_name": legal_entity.trading_name,
        "entity_type": legal_entity.entity_type,
        "registration_number": legal_entity.registration_number,
        "incorporation_date": legal_entity.incorporation_date,
        "country_of_incorporation": legal_entity.country_of_incorporation,
        "registered_address": legal_entity.registered_address,
        "principal_business_address": legal_entity.principal_business_address,
        "business_activity": legal_entity.business_activity,
        "industry": legal_entity.industry,
        "created_at": legal_entity.created_at,
        "created_by": current_user.username,
        "message": "Legal entity created successfully"
    }