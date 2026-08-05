import json
from datetime import date, datetime, time
from typing import Optional
from urllib.parse import parse_qs

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import SessionLocal
from app.models import User
from app.models.todo_model import ReminderType, ToDo

router = APIRouter(
    prefix="/api/telegram",
    tags=["Telegram"]
)

class TaskStatusUpdate(BaseModel):
    completed: bool


class MiniAppToDoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_date: Optional[date] = None
    deadline_time: Optional[time] = None
    reminder_type: ReminderType = ReminderType.NONE
    init_data: str


def get_telegram_id(init_data: str) -> int:
    try:
        parsed = parse_qs(init_data)
        user_data = json.loads(parsed["user"][0])
        return user_data["id"]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid init_data")



@router.get("/profile")
async def get_profile_webapp(init_data: str):
    telegram_id = get_telegram_id(init_data)
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id).options(selectinload(User.todos))
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        total = len(user.todos)
        active = len([t for t in user.todos if not t.completed])

        return {
            "email": user.email,
            "active_count": active,
            "completed_count": total - active,
        }

@router.get("/todos")
async def get_todos_for_webapp(init_data: str):
    telegram_id = get_telegram_id(init_data)
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id).options(selectinload(User.todos))
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user.todos


@router.post("/todos")
async def create_todo_webapp(data: MiniAppToDoCreate):
    telegram_id = get_telegram_id(data.init_data)
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        remind_at = None
        if data.target_date:
            if data.reminder_type in (ReminderType.DEADLINE, ReminderType.BOTH) and data.deadline_time:
                remind_at = datetime.combine(data.target_date, data.deadline_time)
            elif data.reminder_type == ReminderType.MORNING:
                remind_at = datetime.combine(data.target_date, time(9, 0))

        todo = ToDo(
            title=data.title,
            description=data.description,
            target_date=data.target_date,
            deadline_time=data.deadline_time,
            remind_at=remind_at,
            reminder_type=data.reminder_type,
            user_id=user.id,
        )
        session.add(todo)
        await session.commit()
        await session.refresh(todo)
        return {"status": "ok", "id": todo.id}


@router.patch("/todos/{todo_id}")
async def update_todo_status(todo_id: int, status: TaskStatusUpdate, init_data: str):
    telegram_id = get_telegram_id(init_data)
    async with SessionLocal() as session:
        result = await session.execute(
            select(ToDo).join(User).where(ToDo.id == todo_id, User.telegram_id == telegram_id)
        )
        todo = result.scalars().first()
        if not todo:
            raise HTTPException(status_code=404, detail="Task not found")

        todo.completed = status.completed
        await session.commit()
        return {"status": "ok"}




@router.delete("/account")
async def delete_account_webapp(init_data: str):
    telegram_id = get_telegram_id(init_data)
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await session.delete(user)
        await session.commit()
        return {"status": "ok", "message": "Account deleted"}