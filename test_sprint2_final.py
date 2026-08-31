from app.database.connection import SessionLocal
from app.database.models import ScreeningResult
from app.services.company_cdd_service import get_company_screening_subjects
from app.services.screening_service import (
    build_screening_plan,
    execute_screening_task
)

db = SessionLocal()

legal_entity_id = "f1e38de6-cfa1-4b2e-b58e-024d784b8f13"
kyc_profile_id = "bff6f7be-34e2-4d79-ac01-1101acbd67f9"

try:

    subjects = get_company_screening_subjects(
        db=db,
        legal_entity_id=legal_entity_id
    )

    print("SUBJECTS:")
    print(subjects)

    plan = build_screening_plan(subjects)

    print("\nPLAN:")
    for task in plan:
        print({
            "name": task["name"],
            "type": task["screening_type"],
            "country": task["subject_country"],
            "role": task["relationship_role"]
        })

    print("\nEXECUTION:")

    for task in plan:

        result, error = execute_screening_task(
            db=db,
            screening_task=task,
            kyc_profile_id=kyc_profile_id
        )

        print({
            "name": task["name"],
            "type": task["screening_type"],
            "result": result.result if result else None,
            "provider": result.provider if result else None,
            "error": error
        })

    db.commit()

    print("\nCOMMITTED")

    rows = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.kyc_profile_id
            == kyc_profile_id
        )
        .order_by(
            ScreeningResult.checked_at.desc()
        )
        .limit(3)
        .all()
    )

    print("\nDATABASE:")

    for row in rows:
        print({
            "type": row.screening_type,
            "result": row.result,
            "provider": row.provider,
            "matched_name": row.matched_name,
            "source_uid": row.source_uid,
            "country_match": row.country_match,
            "identifier_match": row.identifier_match,
            "match_strength": row.match_strength,
            "evidence_strength": row.evidence_strength
        })

except Exception:
    db.rollback()
    raise

finally:
    db.close()