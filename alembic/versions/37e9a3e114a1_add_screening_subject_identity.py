"""add screening subject identity

Revision ID: 37e9a3e114a1
Revises: 08dbfc0b5309
Create Date: 2026-08-26 18:00:41.644841

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "37e9a3e114a1"
down_revision: Union[str, Sequence[str], None] = "08dbfc0b5309"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add screening subject identity fields."""

    op.add_column(
        "screening_results",
        sa.Column(
            "subject_type",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "screening_results",
        sa.Column(
            "subject_id",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "screening_results",
        sa.Column(
            "relationship_role",
            sa.String(),
            nullable=True
        )
    )

    op.create_index(
        "ix_screening_results_subject_id",
        "screening_results",
        ["subject_id"],
        unique=False
    )


def downgrade() -> None:
    """Remove screening subject identity fields."""

    op.drop_index(
        "ix_screening_results_subject_id",
        table_name="screening_results"
    )

    op.drop_column(
        "screening_results",
        "relationship_role"
    )

    op.drop_column(
        "screening_results",
        "subject_id"
    )

    op.drop_column(
        "screening_results",
        "subject_type"
    )