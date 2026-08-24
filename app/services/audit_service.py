from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.models import AuditLog


def create_audit_log(
    db: Session,
    user_id: str | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
    reason: str | None = None
):
    audit_log = AuditLog(
        id=str(uuid4()),
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        reason=reason
    )

    db.add(audit_log)
    db.flush()

    return audit_log