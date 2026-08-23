from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import Role


DEFAULT_ROLES = [
    {
        "name": "Customer",
        "description": "External customer access"
    },
    {
        "name": "Maker",
        "description": "Creates and investigates cases"
    },
    {
        "name": "Checker",
        "description": "Reviews and approves or rejects cases"
    },
    {
        "name": "Admin",
        "description": "Manages users, roles and system settings"
    }
]


def seed_roles():
    db: Session = SessionLocal()

    try:
        for role_data in DEFAULT_ROLES:

            existing_role = (
                db.query(Role)
                .filter(
                    Role.name == role_data["name"]
                )
                .first()
            )

            if existing_role:
                print(
                    f"Role already exists: "
                    f"{role_data['name']}"
                )
                continue

            role = Role(
                id=str(uuid4()),
                name=role_data["name"],
                description=role_data["description"]
            )

            db.add(role)

            print(
                f"Created role: "
                f"{role_data['name']}"
            )

        db.commit()

        print("Role seeding completed.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()