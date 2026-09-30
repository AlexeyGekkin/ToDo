"""add user timezone

Revision ID: e9b7e93bf42d
Revises: 2f98c6a76120
Create Date: 2026-09-27 20:57:16.083009

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e9b7e93bf42d'
down_revision: str | Sequence[str] | None = '2f98c6a76120'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "timezone",
        server_default="Europe/Samara",
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "timezone",
        server_default="Europe/Moscow",
    )
