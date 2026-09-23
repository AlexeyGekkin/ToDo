"""split reminder times

Revision ID: fb696b34c4ca
Revises: a693aa5dce1a
Create Date: 2026-09-23 19:59:09.411451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fb696b34c4ca'
down_revision: Union[str, Sequence[str], None] = 'a693aa5dce1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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
