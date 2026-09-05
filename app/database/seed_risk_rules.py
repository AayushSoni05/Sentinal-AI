from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import RiskRule


DEFAULT_RISK_RULES = [
    {
        "rule_name": "OFAC Confirmed",
        "factor": "SANCTIONS",
        "min_score": 100,
        "max_score": 100,
        "risk_tier": "CRITICAL",
        "action": "BLOCK"
    },
    {
        "rule_name": "OFAC High Risk",
        "factor": "SANCTIONS",
        "min_score": 95,
        "max_score": 99.99,
        "risk_tier": "HIGH",
        "action": "REVIEW"
    },
    {
        "rule_name": "OFAC Review",
        "factor": "SANCTIONS",
        "min_score": 85,
        "max_score": 94.99,
        "risk_tier": "HIGH",
        "action": "REVIEW"
    }
]


def seed_risk_rules():
    db: Session = SessionLocal()

    try:
        for rule_data in DEFAULT_RISK_RULES:

            existing_rule = (
                db.query(RiskRule)
                .filter(
                    RiskRule.rule_name
                    == rule_data["rule_name"]
                )
                .first()
            )

            if existing_rule:
                print(
                    f"Risk rule already exists: "
                    f"{rule_data['rule_name']}"
                )
                continue

            rule = RiskRule(
                id=str(uuid4()),
                rule_name=rule_data["rule_name"],
                factor=rule_data["factor"],
                min_score=str(
                    rule_data["min_score"]
                ),
                max_score=str(
                    rule_data["max_score"]
                ),
                risk_tier=rule_data["risk_tier"],
                action=rule_data["action"],
                is_active=True
            )

            db.add(rule)

            print(
                f"Created risk rule: "
                f"{rule_data['rule_name']}"
            )

        db.commit()

        print("Risk rule seeding completed.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_risk_rules()