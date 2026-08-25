"""add customer domain entities

Revision ID: 8ca0fb9a7af1
Revises: 098c313959f1
Create Date: 2026-08-25 17:26:55.489076

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8ca0fb9a7af1"
down_revision: Union[str, Sequence[str], None] = "098c313959f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Person and LegalEntity links to Customer."""

    op.add_column(
        "customers",
        sa.Column(
            "person_id",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "customers",
        sa.Column(
            "legal_entity_id",
            sa.String(),
            nullable=True
        )
    )

    op.create_index(
        op.f("ix_customers_person_id"),
        "customers",
        ["person_id"],
        unique=True
    )

    op.create_index(
        op.f("ix_customers_legal_entity_id"),
        "customers",
        ["legal_entity_id"],
        unique=True
    )

    op.create_foreign_key(
        None,
        "customers",
        "persons",
        ["person_id"],
        ["id"]
    )

    op.create_foreign_key(
        None,
        "customers",
        "legal_entities",
        ["legal_entity_id"],
        ["id"]
    )


def downgrade() -> None:
    """Remove Person and LegalEntity links from Customer."""

    op.drop_constraint(
        None,
        "customers",
        type_="foreignkey"
    )

    op.drop_constraint(
        None,
        "customers",
        type_="foreignkey"
    )

    op.drop_index(
        op.f("ix_customers_person_id"),
        table_name="customers"
    )

    op.drop_index(
        op.f("ix_customers_legal_entity_id"),
        table_name="customers"
    )

    op.drop_column(
        "customers",
        "person_id"
    )

    op.drop_column(
        "customers",
        "legal_entity_id"
    )