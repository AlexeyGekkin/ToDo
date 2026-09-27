"""remove redundant indexes

Revision ID: 6f81532536ec
Revises: fb696b34c4ca
Create Date: 2026-09-27 17:35:58.843500

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6f81532536ec"
down_revision: Union[str, Sequence[str], None] = "fb696b34c4ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(
        "ix_todos_id",
        table_name="todos",
    )

    op.drop_index(
        "ix_users_email",
        table_name="users",
    )

    op.drop_index(
        "ix_users_id",
        table_name="users",
    )

    op.drop_index(
        "ix_users_telegram_id",
        table_name="users",
    )

    op.drop_index(
        "ix_users_telegram_link_token",
        table_name="users",
    )

    op.create_unique_constraint(
        "uq_users_telegram_link_token",
        "users",
        ["telegram_link_token"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_users_telegram_link_token",
        "users",
        type_="unique",
    )

    op.create_index(
        "ix_users_telegram_link_token",
        "users",
        ["telegram_link_token"],
        unique=True,
    )

    op.create_index(
        "ix_users_telegram_id",
        "users",
        ["telegram_id"],
        unique=False,
    )

    op.create_index(
        "ix_users_id",
        "users",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=False,
    )

    op.create_index(
        "ix_todos_id",
        "todos",
        ["id"],
        unique=False,
    )