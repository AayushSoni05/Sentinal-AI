"""repair customer foreign keys

Revision ID: 18ed0c711cb8
Revises: f265a0c1242b
Create Date: 2026-08-25 18:00:00

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "18ed0c711cb8"
down_revision: Union[str, Sequence[str], None] = "f265a0c1242b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Repair missing foreign-key constraints."""

    with op.batch_alter_table("customers") as batch_op:

        batch_op.create_foreign_key(
            "fk_customers_person_id",
            "persons",
            ["person_id"],
            ["id"]
        )

        batch_op.create_foreign_key(
            "fk_customers_legal_entity_id",
            "legal_entities",
            ["legal_entity_id"],
            ["id"]
        )

    with op.batch_alter_table("investigations") as batch_op:

        batch_op.create_foreign_key(
            "fk_investigations_customer_id",
            "customers",
            ["customer_id"],
            ["id"]
        )


def downgrade() -> None:
    """Remove repaired foreign-key constraints."""

    with op.batch_alter_table("investigations") as batch_op:

        batch_op.drop_constraint(
            "fk_investigations_customer_id",
            type_="foreignkey"
        )

    with op.batch_alter_table("customers") as batch_op:

        batch_op.drop_constraint(
            "fk_customers_legal_entity_id",
            type_="foreignkey"
        )

        batch_op.drop_constraint(
            "fk_customers_person_id",
            type_="foreignkey"
        )