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

    today = datetime.now().strftime("%Y%m%d")

    latest_person = (
        db.query(Person)
        .filter(
            Person.person_number.like(f"PE-{today}-%")
        )
        .order_by(
            Person.person_number.desc()
        )
        .first()
    )

    if latest_person:
        last_number = int(
            latest_person.person_number.split("-")[-1]
        )
        next_number = last_number + 1
    else:
        next_number = 1

    person_number = f"PE-{today}-{next_number:06d}"

    person = Person(
        id=person_id,
        person_number=person_number,
        full_name=full_name,
        nationality=nationality,
        country_of_residence=country_of_residence,
        identity_type=identity_type,
        identity_number=identity_number
    )

    if date_of_birth:
        person.date_of_birth = datetime.fromisoformat(
            date_of_birth
        )

    db.add(person)
    db.commit()
    db.refresh(person)

    return person