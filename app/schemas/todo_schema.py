from pydantic import BaseModel


class TodoCreate(BaseModel):
    title: str
    description: str | None = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    is_done: bool

    class Config:
        from_attributes = True

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_done: bool | None = None