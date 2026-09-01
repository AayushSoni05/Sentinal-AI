from app.database.connection import SessionLocal
from app.database.models import Customer, KYCProfile
from app.services.company_cdd_service import (
    get_company_screening_subjects
)
from app.services.screening_service import (
    build_screening_plan,
    execute_screening_task
)

db = SessionLocal()

customer = (
    db.query(Customer)
    .filter(
        Customer.customer_number
        == "CUS-20260825-000005"
    )
    .first()
)

if customer is None:
    raise Exception("Customer not found")

kyc_profile = (
    db.query(KYCProfile)
    .filter(
        KYCProfile.customer_id
        == customer.id
    )
    .first()
)

if kyc_profile is None:
    raise Exception("KYC profile not found")

subjects = get_company_screening_subjects(
    db=db,
    legal_entity_id=customer.legal_entity_id
)

plan = build_screening_plan(subjects)

print("CUSTOMER:", customer.name)
print("KYC PROFILE:", kyc_profile.id)
print("SUBJECTS:", subjects)
print("TASK COUNT:", len(plan))

for task in plan:
    result, error = execute_screening_task(
        db=db,
        screening_task=task,
        kyc_profile_id=kyc_profile.id
    )

    print({
        "screening_type":
            task["screening_type"],
        "result":
            result.result if result else None,
        "provider":
            result.provider if result else None,
        "error":
            error
    })

db.commit()

print("COMMITTED")

db.close()