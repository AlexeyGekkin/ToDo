from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TodoCreate(BaseModel):
    title: str
    description: str | None = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    is_done: bool
    created_at: datetime  # Добавили поле времени

    model_config = ConfigDict(from_attributes=True)


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_done: bool | None = None