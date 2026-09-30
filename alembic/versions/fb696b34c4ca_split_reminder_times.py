"""split reminder times

Revision ID: fb696b34c4ca
Revises: a693aa5dce1a
Create Date: 2026-09-23 19:59:09.411451

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fb696b34c4ca'
down_revision: str | Sequence[str] | None = 'a693aa5dce1a'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        'todos',
        sa.Column(
            'morning_remind_at',
            sa.DateTime(timezone=True),
            nullable=True
        )
    )
    op.add_column(
        'todos',
        sa.Column(
            'deadline_remind_at',
            sa.DateTime(timezone=True),
            nullable=True
        )
    )
    op.drop_column('todos', 'remind_at')


def downgrade() -> None:
    op.add_column(
        'todos',
        sa.Column(
            'remind_at',
            sa.DateTime(timezone=True),
            nullable=True
        )
    )
    op.drop_column('todos', 'deadline_remind_at')
    op.drop_column('todos', 'morning_remind_at')
