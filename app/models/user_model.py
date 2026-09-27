from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


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

    telegram_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        unique=True,
        nullable=True
    )

    telegram_link_token: Mapped[Optional[str]] = mapped_column(
        String,
        unique=True,
        nullable=True
    )

    telegram_link_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    todos: Mapped[List["ToDo"]] = relationship(
        "ToDo",
        back_populates="user",
        cascade="all, delete-orphan"
    )