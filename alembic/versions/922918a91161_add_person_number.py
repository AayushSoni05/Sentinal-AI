"""add person number

Revision ID: 922918a91161
Revises: 299bc3611d87
Create Date: 2026-09-08 15:50:37.204418

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "922918a91161"
down_revision: Union[str, Sequence[str], None] = "299bc3611d87"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "persons",
        sa.Column("person_number", sa.String(), nullable=True)
    )

    bind = op.get_bind()

    rows = bind.execute(
        sa.text(
            """
            SELECT id
            FROM persons
            ORDER BY created_at, id
            """
        )
    ).fetchall()

    today = datetime.now().strftime("%Y%m%d")

    for index, row in enumerate(rows, start=1):
        person_number = f"PE-{today}-{index:06d}"

        bind.execute(
            sa.text(
                """
                UPDATE persons
                SET person_number = :person_number
                WHERE id = :id
                """
            ),
            {
                "person_number": person_number,
                "id": row[0]
            }
        )

    op.create_index(
        "ix_persons_person_number",
        "persons",
        ["person_number"],
        unique=True
    )


def downgrade() -> None:
    op.drop_index(
        "ix_persons_person_number",
        table_name="persons"
    )

    op.drop_column(
        "persons",
        "person_number"
    )