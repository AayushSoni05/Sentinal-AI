"""add user and role tables

Revision ID: 93db7273ad72
Revises:
Create Date: 2026-08-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "93db7273ad72"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create roles and users tables."""

    op.create_table(
        "roles",
        sa.Column(
            "id",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "name",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "description",
            sa.String(),
            nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name")
    )

    op.create_index(
        "ix_roles_id",
        "roles",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_roles_name",
        "roles",
        ["name"],
        unique=True
    )

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "username",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "email",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "password_hash",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "role_id",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="Active"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_users_id",
        "users",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_users_username",
        "users",
        ["username"],
        unique=True
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True
    )

    op.create_index(
        "ix_users_role_id",
        "users",
        ["role_id"],
        unique=False
    )


def downgrade() -> None:
    """Remove roles and users tables."""

    op.drop_index(
        "ix_users_role_id",
        table_name="users"
    )

    op.drop_index(
        "ix_users_email",
        table_name="users"
    )

    op.drop_index(
        "ix_users_username",
        table_name="users"
    )

    op.drop_index(
        "ix_users_id",
        table_name="users"
    )

    op.drop_table("users")

    op.drop_index(
        "ix_roles_name",
        table_name="roles"
    )

    op.drop_index(
        "ix_roles_id",
        table_name="roles"
    )

    op.drop_table("roles")