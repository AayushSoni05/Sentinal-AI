"""add legal entity number

Revision ID: 299bc3611d87
Revises: 9dfe6404a444
Create Date: 2026-09-08 13:06:59.246214
"""

from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision: str = "299bc3611d87"
down_revision: Union[str, Sequence[str], None] = "9dfe6404a444"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add business-facing LegalEntity number."""

    op.add_column(
        "legal_entities",
        sa.Column(
            "legal_entity_number",
            sa.String(),
            nullable=True
        )
    )

    bind = op.get_bind()

    rows = bind.execute(
        sa.text(
            """
            SELECT id
            FROM legal_entities
            ORDER BY created_at, id
            """
        )
    ).fetchall()

    for index, row in enumerate(rows, start=1):
        legal_entity_number = (
            f"LE-{datetime.now().strftime('%Y%m%d')}-{index:06d}"
        )

        bind.execute(
            sa.text(
                """
                UPDATE legal_entities
                SET legal_entity_number = :number
                WHERE id = :id
                """
            ),
            {
                "number": legal_entity_number,
                "id": row[0],
            }
        )

    op.create_index(
        "ix_legal_entities_legal_entity_number",
        "legal_entities",
        ["legal_entity_number"],
        unique=True
    )


def downgrade() -> None:
    """Remove business-facing LegalEntity number."""

    op.drop_index(
        "ix_legal_entities_legal_entity_number",
        table_name="legal_entities"
    )

    op.drop_column(
        "legal_entities",
        "legal_entity_number"
    )