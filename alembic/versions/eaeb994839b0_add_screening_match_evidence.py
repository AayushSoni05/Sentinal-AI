"""add screening match evidence

Revision ID: eaeb994839b0
Revises: 37e9a3e114a1
Create Date: 2026-08-31 15:06:30.492603

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eaeb994839b0'
down_revision: Union[str, Sequence[str], None] = '37e9a3e114a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add screening match evidence fields."""

    op.add_column(
        "screening_results",
        sa.Column(
            "source_uid",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "screening_results",
        sa.Column(
            "country_match",
            sa.Boolean(),
            nullable=True
        )
    )

    op.add_column(
        "screening_results",
        sa.Column(
            "identifier_match",
            sa.Boolean(),
            nullable=True
        )
    )

    op.add_column(
        "screening_results",
        sa.Column(
            "match_strength",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "screening_results",
        sa.Column(
            "evidence_strength",
            sa.String(),
            nullable=True
        )
    )

    op.create_index(
        "ix_screening_results_source_uid",
        "screening_results",
        ["source_uid"],
        unique=False
    )


def downgrade() -> None:
    """Remove screening match evidence fields."""

    op.drop_index(
        "ix_screening_results_source_uid",
        table_name="screening_results"
    )

    op.drop_column(
        "screening_results",
        "evidence_strength"
    )

    op.drop_column(
        "screening_results",
        "match_strength"
    )

    op.drop_column(
        "screening_results",
        "identifier_match"
    )

    op.drop_column(
        "screening_results",
        "country_match"
    )

    op.drop_column(
        "screening_results",
        "source_uid"
    )