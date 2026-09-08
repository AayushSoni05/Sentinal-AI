from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.models import Person


def create_person(
    db: Session,
    full_name: str,
    date_of_birth: str | None = None,
    nationality: str | None = None,
    country_of_residence: str | None = None,
    identity_type: str | None = None,
    identity_number: str | None = None
):
    person_id = str(uuid4())

    person = Person(
        id=person_id,
        full_name=full_name,
        nationality=nationality,
        country_of_residence=country_of_residence,
        identity_type=identity_type,
        identity_number=identity_number
    )

    if date_of_birth:
        person.date_of_birth = datetime.fromisoformat(date_of_birth)

    db.add(person)
    db.commit()
    db.refresh(person)

    return person