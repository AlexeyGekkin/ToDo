from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.todo_model import ReminderType


class ToDoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    reminder_type: Optional[ReminderType] = None

class ToDoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    reminder_type: Optional[ReminderType] = None

class ToDoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    due_date: Optional[datetime] = None
    reminder_type: Optional[ReminderType] = None
    user_id: int

    class Config:
        from_attributes = True