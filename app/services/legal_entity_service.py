from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.models import LegalEntity


def create_legal_entity(
    db: Session,
    legal_name: str,
    trading_name: str | None = None,
    entity_type: str = "Company",
    registration_number: str | None = None,
    incorporation_date: str | None = None,
    country_of_incorporation: str | None = None,
    registered_address: str | None = None,
    principal_business_address: str | None = None,
    business_activity: str | None = None,
    industry: str | None = None
):
    legal_entity_id = str(uuid4())

    today = datetime.now().strftime("%Y%m%d")

    latest_legal_entity = (
        db.query(LegalEntity)
        .filter(
            LegalEntity.legal_entity_number.like(
                f"LE-{today}-%"
            )
        )
        .order_by(
            LegalEntity.legal_entity_number.desc()
        )
        .first()
    )

    if latest_legal_entity:
        last_number = int(
            latest_legal_entity.legal_entity_number.split("-")[-1]
        )
        next_number = last_number + 1
    else:
        next_number = 1

    legal_entity_number = (
        f"LE-{today}-{next_number:06d}"
    )

    legal_entity = LegalEntity(
        id=legal_entity_id,
        legal_entity_number=legal_entity_number,
        legal_name=legal_name,
        trading_name=trading_name,
        entity_type=entity_type,
        registration_number=registration_number,
        country_of_incorporation=country_of_incorporation,
        registered_address=registered_address,
        principal_business_address=principal_business_address,
        business_activity=business_activity,
        industry=industry
    )

    if incorporation_date:
        legal_entity.incorporation_date = (
            datetime.fromisoformat(incorporation_date)
        )

    db.add(legal_entity)
    db.commit()
    db.refresh(legal_entity)

    return legal_entity