import enum
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Time, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReminderType(str, enum.Enum):
    NONE = "none"
    MORNING = "morning"
    DEADLINE = "deadline"
    BOTH = "both"


class ToDo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    completed: Mapped[bool] = mapped_column(default=False, server_default=text("false"))

    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    deadline_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    remind_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    reminder_type: Mapped[ReminderType] = mapped_column(
        Enum(ReminderType, native_enum=False),
        default=ReminderType.NONE,
        server_default=ReminderType.NONE.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="todos")