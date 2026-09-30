from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.todo_model import ToDo

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    password: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        unique=True,
        nullable=True
    )

    telegram_link_token: Mapped[str | None] = mapped_column(
        String,
        unique=True,
        nullable=True
    )

    telegram_link_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    todos: Mapped[list["ToDo"]] = relationship(
        "ToDo",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        server_default="Europe/Samara",
    )