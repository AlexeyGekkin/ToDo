"""Initial tables

Revision ID: a693aa5dce1a
Revises:
Create Date: 2026-08-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a693aa5dce1a"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "telegram_link_token",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "telegram_link_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("telegram_id"),
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
        "ix_users_telegram_id",
        "users",
        ["telegram_id"],
        unique=False,
    )

    op.create_index(
        "ix_users_telegram_link_token",
        "users",
        ["telegram_link_token"],
        unique=True,
    )

    op.create_table(
        "todos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "completed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("deadline_time", sa.Time(), nullable=True),
        sa.Column(
            "remind_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "reminder_type",
            sa.String(),
            server_default="none",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_todos_id",
        "todos",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_todos_user_id_id",
        "todos",
        ["user_id", "id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_todos_user_id_id",
        table_name="todos",
    )

    op.drop_index(
        "ix_todos_id",
        table_name="todos",
    )

    op.drop_table("todos")

    op.drop_index(
        "ix_users_telegram_link_token",
        table_name="users",
    )

    op.drop_index(
        "ix_users_telegram_id",
        table_name="users",
    )

    op.drop_index(
        "ix_users_email",
        table_name="users",
    )

    op.drop_index(
        "ix_users_id",
        table_name="users",
    )

    op.drop_table("users")