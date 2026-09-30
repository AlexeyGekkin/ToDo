from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict

from app.models.todo_model import ReminderType


class ToDoCreate(BaseModel):
    title: str
    description: str | None = None
    target_date: date | None = None
    deadline_time: time | None = None
    reminder_type: ReminderType = ReminderType.NONE


class ToDoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    target_date: date | None = None
    deadline_time: time | None = None
    reminder_type: ReminderType | None = None


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
