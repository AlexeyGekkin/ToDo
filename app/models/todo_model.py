from sqlalchemy import (Column,Integer, String,
                        Boolean, ForeignKey, DateTime, func)
from sqlalchemy.orm import relationship

from app.database import Base


class ToDo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_done = Column(Boolean, default=False)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="todos"
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )