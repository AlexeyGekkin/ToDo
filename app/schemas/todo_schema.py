from datetime import date, datetime, time
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.todo_model import ReminderType


class ToDoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_date: Optional[date] = None
    deadline_time: Optional[time] = None
    remind_at: Optional[datetime] = None
    reminder_type: ReminderType = ReminderType.NONE


class ToDoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    target_date: Optional[date] = None
    deadline_time: Optional[time] = None
    remind_at: Optional[datetime] = None
    reminder_type: Optional[ReminderType] = None


class ToDoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    target_date: Optional[date] = None
    deadline_time: Optional[time] = None
    remind_at: Optional[datetime] = None
    reminder_type: ReminderType
    user_id: int
    model_config = ConfigDict(from_attributes=True)