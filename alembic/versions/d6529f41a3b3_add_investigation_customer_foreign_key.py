"""add investigation customer foreign key

Revision ID: d6529f41a3b3
Revises: 93db7273ad72
Create Date: 2026-08-23 14:34:44.511494

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d6529f41a3b3"
down_revision: Union[str, Sequence[str], None] = "93db7273ad72"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table(
        "investigations",
        recreate="always"
    ) as batch_op:

        batch_op.alter_column(
            "customer_id",
            existing_type=sa.TEXT(),
            type_=sa.String(),
            existing_nullable=True
        )

        batch_op.create_index(
            "ix_investigations_customer_id",
            ["customer_id"],
            unique=False
        )

        batch_op.create_foreign_key(
            "fk_investigations_customer_id_customers",
            "customers",
            ["customer_id"],
            ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table(
        "investigations",
        recreate="always"
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_investigations_customer_id_customers",
            type_="foreignkey"
        )

        batch_op.drop_index(
            "ix_investigations_customer_id"
        )

        batch_op.alter_column(
            "customer_id",
            existing_type=sa.String(),
            type_=sa.TEXT(),
            existing_nullable=True
        )