import enum
from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Time,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user_model import User

class ReminderType(str, enum.Enum):
    NONE = "none"
    MORNING = "morning"
    DEADLINE = "deadline"
    BOTH = "both"


class ToDo(Base):
    __tablename__ = "todos"

    __table_args__ = (
        Index(
            "ix_todos_user_id_id",
            "user_id",
            "id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    completed: Mapped[bool] = mapped_column(
        default=False,
        server_default=text("false")
    )

    target_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    deadline_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True
    )

    morning_remind_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    deadline_remind_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    reminder_type: Mapped[ReminderType] = mapped_column(
        Enum(
            ReminderType,
            native_enum=False
        ),
        default=ReminderType.NONE,
        server_default=ReminderType.NONE.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="todos"
    )