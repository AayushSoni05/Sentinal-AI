"""add condition to risk rules

Revision ID: e3a8d4158ded
Revises: eaeb994839b0
Create Date: 2026-09-07 13:09:55.100711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3a8d4158ded'
down_revision: Union[str, Sequence[str], None] = 'eaeb994839b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "risk_rules",
        sa.Column(
            "condition",
            sa.String(),
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "risk_rules",
        "condition"
    )