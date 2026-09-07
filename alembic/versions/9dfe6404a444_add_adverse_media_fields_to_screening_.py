"""add adverse media fields to screening results

Revision ID: 9dfe6404a444
Revises: e3a8d4158ded
Create Date: 2026-09-07 15:00:19.568510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9dfe6404a444'
down_revision: Union[str, Sequence[str], None] = 'e3a8d4158ded'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "screening_results",
        sa.Column(
            "adverse_media_category",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "screening_results",
        sa.Column(
            "adverse_media_headline",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "screening_results",
        sa.Column(
            "adverse_media_summary",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "screening_results",
        sa.Column(
            "adverse_media_source",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "screening_results",
        sa.Column(
            "adverse_media_published_date",
            sa.DateTime(),
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "screening_results",
        "adverse_media_published_date"
    )

    op.drop_column(
        "screening_results",
        "adverse_media_source"
    )

    op.drop_column(
        "screening_results",
        "adverse_media_summary"
    )

    op.drop_column(
        "screening_results",
        "adverse_media_headline"
    )

    op.drop_column(
        "screening_results",
        "adverse_media_category"
    )
