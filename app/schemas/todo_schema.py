from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.todo_model import ReminderType


class ToDoCreate(BaseModel):
    title: str = Field(max_length=200)
    description: str | None = None
    target_date: date | None = None
    deadline_time: time | None = None
    reminder_type: ReminderType = ReminderType.NONE

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value

class ToDoUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    completed: bool | None = None
    target_date: date | None = None
    deadline_time: time | None = None
    reminder_type: ReminderType | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Title cannot be null")

        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value

class ToDoResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    completed: bool
    target_date: date | None = None
    deadline_time: time | None = None
    morning_remind_at: datetime | None = None
    deadline_remind_at: datetime | None = None
    reminder_type: ReminderType
    user_id: int

    model_config = ConfigDict(from_attributes=True)
