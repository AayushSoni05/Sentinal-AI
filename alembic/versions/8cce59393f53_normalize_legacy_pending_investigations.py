"""normalize legacy pending investigations

Revision ID: 8cce59393f53
Revises: d6529f41a3b3
Create Date: 2026-08-23 16:22:38.525379

"""

from typing import Sequence, Union

from alembic import op


revision: str = "8cce59393f53"
down_revision: Union[str, Sequence[str], None] = "d6529f41a3b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert legacy Pending investigations to Draft."""

    op.execute(
        """
        UPDATE investigations
        SET status = 'Draft'
        WHERE status = 'Pending'
        """
    )


def downgrade() -> None:
    """Restore Draft investigations to Pending."""

    op.execute(
        """
        UPDATE investigations
        SET status = 'Pending'
        WHERE status = 'Draft'
        """
    )