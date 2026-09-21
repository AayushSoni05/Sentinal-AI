"""add sanctions screening coverage

Revision ID: 1ff57d2527d0
Revises: 922918a91161
Create Date: 2026-09-21 16:54:46.888887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ff57d2527d0'
down_revision: Union[str, Sequence[str], None] = '922918a91161'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sanctions_screening_coverage",
        sa.Column(
            "id",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "kyc_profile_id",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "subject_type",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "subject_id",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "relationship_role",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "sources_discovered",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "sources_checked",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "matches",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "possible_matches",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "no_matches",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "unavailable",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "errors",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "checked_at",
            sa.DateTime(),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["kyc_profile_id"],
            ["kyc_profiles.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_sanctions_screening_coverage_id",
        "sanctions_screening_coverage",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_sanctions_screening_coverage_kyc_profile_id",
        "sanctions_screening_coverage",
        ["kyc_profile_id"],
        unique=False
    )

    op.create_index(
        "ix_sanctions_screening_coverage_subject_id",
        "sanctions_screening_coverage",
        ["subject_id"],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_sanctions_screening_coverage_subject_id",
        table_name="sanctions_screening_coverage"
    )

    op.drop_index(
        "ix_sanctions_screening_coverage_kyc_profile_id",
        table_name="sanctions_screening_coverage"
    )

    op.drop_index(
        "ix_sanctions_screening_coverage_id",
        table_name="sanctions_screening_coverage"
    )

    op.drop_table("sanctions_screening_coverage")