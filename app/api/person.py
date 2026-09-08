from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.auth.roles import require_maker
from app.database.models import User

from app.schemas.customer import PersonRequest

from app.services.person_service import create_person


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/persons")
def create_person_endpoint(
    request: PersonRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maker)
):
    person = create_person(
        db=db,
        full_name=request.full_name,
        date_of_birth=request.date_of_birth,
        nationality=request.nationality,
        country_of_residence=request.country_of_residence,
        identity_type=request.identity_type,
        identity_number=request.identity_number
    )

    return {
        "person_id": person.id,
        "full_name": person.full_name,
        "date_of_birth": person.date_of_birth,
        "nationality": person.nationality,
        "country_of_residence": person.country_of_residence,
        "identity_type": person.identity_type,
        "identity_number": person.identity_number,
        "created_at": person.created_at,
        "created_by": current_user.username,
        "message": "Person created successfully"
    }