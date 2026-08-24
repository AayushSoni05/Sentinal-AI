"""add kyc profile

Revision ID: 098c313959f1
Revises: 28993e76f55b
Create Date: 2026-08-24 18:42:23.402492

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "098c313959f1"
down_revision: Union[str, Sequence[str], None] = "28993e76f55b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create kyc_profiles table."""

    op.create_table(
        "kyc_profiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("identity_type", sa.String(), nullable=True),
        sa.Column("identity_number", sa.String(), nullable=True),
        sa.Column("aadhaar_number", sa.String(), nullable=True),
        sa.Column("pan_number", sa.String(), nullable=True),
        sa.Column("onboarding_channel", sa.String(), nullable=True),
        sa.Column("customer_country", sa.String(), nullable=True),
        sa.Column("pep_status", sa.String(), nullable=True),
        sa.Column("negative_news", sa.String(), nullable=True),
        sa.Column("name_screening_result", sa.String(), nullable=True),
        sa.Column("occupation", sa.String(), nullable=True),
        sa.Column("source_of_funds_type", sa.String(), nullable=True),
        sa.Column("funds_documentation", sa.String(), nullable=True),
        sa.Column("monthly_turnover", sa.String(), nullable=True),
        sa.Column("actual_monthly_turnover", sa.String(), nullable=True),
        sa.Column("product_category", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_kyc_profiles_id",
        "kyc_profiles",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_kyc_profiles_customer_id",
        "kyc_profiles",
        ["customer_id"],
        unique=True
    )


def downgrade() -> None:
    """Remove kyc_profiles table."""

    op.drop_index(
        "ix_kyc_profiles_customer_id",
        table_name="kyc_profiles"
    )

    op.drop_index(
        "ix_kyc_profiles_id",
        table_name="kyc_profiles"
    )

    op.drop_table("kyc_profiles")