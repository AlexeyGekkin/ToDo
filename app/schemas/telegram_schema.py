from datetime import date, time
from typing import Optional

from pydantic import BaseModel

from app.models.todo_model import ReminderType


class TaskStatusUpdate(BaseModel):
    completed: bool


class MiniAppToDoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_date: Optional[date] = None
    deadline_time: Optional[time] = None
    reminder_type: ReminderType = ReminderType.NONE
    init_data: str