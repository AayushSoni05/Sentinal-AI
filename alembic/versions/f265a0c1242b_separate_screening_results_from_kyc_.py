"""separate screening results from kyc profile

Revision ID: f265a0c1242b
Revises: 8ca0fb9a7af1
Create Date: 2026-08-25 17:35:36.200175

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f265a0c1242b"
down_revision: Union[str, Sequence[str], None] = "8ca0fb9a7af1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove screening fields from KYC profile."""

    op.drop_column(
        "kyc_profiles",
        "pep_status"
    )

    op.drop_column(
        "kyc_profiles",
        "negative_news"
    )

    op.drop_column(
        "kyc_profiles",
        "name_screening_result"
    )


def downgrade() -> None:
    """Restore screening fields to KYC profile."""

    op.add_column(
        "kyc_profiles",
        sa.Column(
            "pep_status",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "kyc_profiles",
        sa.Column(
            "negative_news",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "kyc_profiles",
        sa.Column(
            "name_screening_result",
            sa.String(),
            nullable=True
        )
    )