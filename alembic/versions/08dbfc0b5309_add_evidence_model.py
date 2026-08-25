"""add evidence model

Revision ID: 08dbfc0b5309
Revises: YOUR_FK_REPAIR_REVISION_ID
Create Date: 2026-08-25 17:56:46.111783

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "08dbfc0b5309"
down_revision: Union[str, Sequence[str], None] = "18ed0c711cb8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create evidence table."""

    op.create_table(
        "evidence",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("subject_type", sa.String(), nullable=False),
        sa.Column("subject_id", sa.String(), nullable=False),
        sa.Column("document_type", sa.String(), nullable=False),
        sa.Column("document_number", sa.String(), nullable=True),
        sa.Column("issuing_authority", sa.String(), nullable=True),
        sa.Column("issuing_country", sa.String(), nullable=True),
        sa.Column("issue_date", sa.DateTime(), nullable=True),
        sa.Column("expiry_date", sa.DateTime(), nullable=True),
        sa.Column(
            "verification_status",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "verification_method",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "verified_by",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "verified_at",
            sa.DateTime(),
            nullable=True
        ),
        sa.Column(
            "storage_reference",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "metadata_text",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        op.f("ix_evidence_id"),
        "evidence",
        ["id"],
        unique=False
    )

    op.create_index(
        op.f("ix_evidence_subject_id"),
        "evidence",
        ["subject_id"],
        unique=False
    )


def downgrade() -> None:
    """Remove evidence table."""

    op.drop_index(
        op.f("ix_evidence_subject_id"),
        table_name="evidence"
    )

    op.drop_index(
        op.f("ix_evidence_id"),
        table_name="evidence"
    )

    op.drop_table("evidence")