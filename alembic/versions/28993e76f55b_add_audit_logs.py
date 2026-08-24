"""add audit logs

Revision ID: 28993e76f55b
Revises: 8cce59393f53
Create Date: 2026-08-24

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "28993e76f55b"
down_revision: Union[str, Sequence[str], None] = "8cce59393f53"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create audit_logs table."""

    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "user_id",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "action",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "entity_type",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "entity_id",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "old_value",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "new_value",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "reason",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_audit_logs_id",
        "audit_logs",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_audit_logs_user_id",
        "audit_logs",
        ["user_id"],
        unique=False
    )


def downgrade() -> None:
    """Remove audit_logs table."""

    op.drop_index(
        "ix_audit_logs_user_id",
        table_name="audit_logs"
    )

    op.drop_index(
        "ix_audit_logs_id",
        table_name="audit_logs"
    )

    op.drop_table("audit_logs")